package com.safechild.agent.utils

import android.content.Context
import android.util.Base64
import android.util.Log
import okhttp3.*
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.RequestBody.Companion.asRequestBody
import org.json.JSONObject
import java.io.File
import java.security.SecureRandom
import java.util.concurrent.TimeUnit
import javax.crypto.Cipher
import javax.crypto.spec.GCMParameterSpec
import javax.crypto.spec.SecretKeySpec

class SecureUploader(private val context: Context) {
    
    companion object {
        private const val TAG = "SecureUploader"
        private const val TIMEOUT_MINUTES = 10L
        private const val CHUNK_SIZE = 5 * 1024 * 1024 // 5MB chunks
    }
    
    private val client = OkHttpClient.Builder()
        .connectTimeout(TIMEOUT_MINUTES, TimeUnit.MINUTES)
        .readTimeout(TIMEOUT_MINUTES, TimeUnit.MINUTES)
        .writeTimeout(TIMEOUT_MINUTES, TimeUnit.MINUTES)
        .build()
    
    fun upload(file: File, token: String, serverUrl: String): Boolean {
        return try {
            // For large files, use chunked upload
            if (file.length() > CHUNK_SIZE) {
                uploadChunked(file, token, serverUrl)
            } else {
                uploadSingle(file, token, serverUrl)
            }
        } catch (e: Exception) {
            Log.e(TAG, "Upload failed", e)
            false
        }
    }
    
    private fun uploadSingle(file: File, token: String, serverUrl: String): Boolean {
        val url = "$serverUrl/collection/upload"
        
        val requestBody = MultipartBody.Builder()
            .setType(MultipartBody.FORM)
            .addFormDataPart("token", token)
            .addFormDataPart("clientNumber", "auto") // Will be resolved from token
            .addFormDataPart(
                "file",
                file.name,
                file.asRequestBody("application/zip".toMediaType())
            )
            .build()
        
        val request = Request.Builder()
            .url(url)
            .post(requestBody)
            .addHeader("User-Agent", "SafeChildAgent/1.0")
            .build()
        
        client.newCall(request).execute().use { response ->
            if (response.isSuccessful) {
                val responseBody = response.body?.string()
                Log.d(TAG, "Upload successful: $responseBody")
                return true
            } else {
                Log.e(TAG, "Upload failed: ${response.code} - ${response.body?.string()}")
                return false
            }
        }
    }
    
    private fun uploadChunked(file: File, token: String, serverUrl: String): Boolean {
        val totalChunks = (file.length() / CHUNK_SIZE).toInt() + 1
        val uploadId = generateUploadId()
        
        file.inputStream().buffered().use { input ->
            var chunkIndex = 0
            val buffer = ByteArray(CHUNK_SIZE)
            
            while (true) {
                val bytesRead = input.read(buffer)
                if (bytesRead <= 0) break
                
                val chunk = if (bytesRead < CHUNK_SIZE) {
                    buffer.copyOf(bytesRead)
                } else {
                    buffer
                }
                
                val success = uploadChunk(
                    chunk = chunk,
                    chunkIndex = chunkIndex,
                    totalChunks = totalChunks,
                    uploadId = uploadId,
                    token = token,
                    serverUrl = serverUrl,
                    fileName = file.name
                )
                
                if (!success) {
                    Log.e(TAG, "Chunk $chunkIndex upload failed")
                    return false
                }
                
                chunkIndex++
            }
        }
        
        // Finalize upload
        return finalizeChunkedUpload(uploadId, token, serverUrl, file.name)
    }
    
    private fun uploadChunk(
        chunk: ByteArray,
        chunkIndex: Int,
        totalChunks: Int,
        uploadId: String,
        token: String,
        serverUrl: String,
        fileName: String
    ): Boolean {
        val url = "$serverUrl/collection/upload-chunk"
        
        val requestBody = MultipartBody.Builder()
            .setType(MultipartBody.FORM)
            .addFormDataPart("token", token)
            .addFormDataPart("upload_id", uploadId)
            .addFormDataPart("chunk_index", chunkIndex.toString())
            .addFormDataPart("total_chunks", totalChunks.toString())
            .addFormDataPart("file_name", fileName)
            .addFormDataPart(
                "chunk",
                "chunk_$chunkIndex",
                RequestBody.create("application/octet-stream".toMediaType(), chunk)
            )
            .build()
        
        val request = Request.Builder()
            .url(url)
            .post(requestBody)
            .addHeader("User-Agent", "SafeChildAgent/1.0")
            .build()
        
        return try {
            client.newCall(request).execute().use { response ->
                response.isSuccessful
            }
        } catch (e: Exception) {
            Log.e(TAG, "Chunk upload error", e)
            false
        }
    }
    
    private fun finalizeChunkedUpload(
        uploadId: String,
        token: String,
        serverUrl: String,
        fileName: String
    ): Boolean {
        val url = "$serverUrl/collection/upload-complete"
        
        val json = JSONObject().apply {
            put("token", token)
            put("upload_id", uploadId)
            put("file_name", fileName)
        }
        
        val requestBody = RequestBody.create(
            "application/json".toMediaType(),
            json.toString()
        )
        
        val request = Request.Builder()
            .url(url)
            .post(requestBody)
            .addHeader("User-Agent", "SafeChildAgent/1.0")
            .build()
        
        return try {
            client.newCall(request).execute().use { response ->
                if (response.isSuccessful) {
                    Log.d(TAG, "Chunked upload finalized successfully")
                    true
                } else {
                    Log.e(TAG, "Finalize failed: ${response.body?.string()}")
                    false
                }
            }
        } catch (e: Exception) {
            Log.e(TAG, "Finalize error", e)
            false
        }
    }
    
    private fun generateUploadId(): String {
        val bytes = ByteArray(16)
        SecureRandom().nextBytes(bytes)
        return Base64.encodeToString(bytes, Base64.NO_WRAP or Base64.URL_SAFE)
    }
    
    // Optional: Encrypt file before upload (AES-GCM)
    fun encryptFile(file: File): Pair<File, Map<String, String>> {
        val key = ByteArray(32).also { SecureRandom().nextBytes(it) }
        val iv = ByteArray(12).also { SecureRandom().nextBytes(it) }
        
        val cipher = Cipher.getInstance("AES/GCM/NoPadding")
        val keySpec = SecretKeySpec(key, "AES")
        val gcmSpec = GCMParameterSpec(128, iv)
        cipher.init(Cipher.ENCRYPT_MODE, keySpec, gcmSpec)
        
        val encryptedFile = File(context.cacheDir, "${file.name}.enc")
        
        file.inputStream().use { input ->
            encryptedFile.outputStream().use { output ->
                val buffer = ByteArray(8192)
                var bytesRead: Int
                while (input.read(buffer).also { bytesRead = it } != -1) {
                    val encrypted = cipher.update(buffer, 0, bytesRead)
                    if (encrypted != null) output.write(encrypted)
                }
                val finalBlock = cipher.doFinal()
                if (finalBlock != null) output.write(finalBlock)
            }
        }
        
        val metadata = mapOf(
            "key" to Base64.encodeToString(key, Base64.NO_WRAP),
            "iv" to Base64.encodeToString(iv, Base64.NO_WRAP),
            "algorithm" to "AES-GCM-256"
        )
        
        return Pair(encryptedFile, metadata)
    }
}
