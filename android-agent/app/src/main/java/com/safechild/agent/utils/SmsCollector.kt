package com.safechild.agent.utils

import android.Manifest
import android.content.Context
import android.content.pm.PackageManager
import android.database.Cursor
import android.net.Uri
import android.provider.Telephony
import androidx.core.content.ContextCompat
import java.text.SimpleDateFormat
import java.util.*

class SmsCollector(private val context: Context) {
    
    companion object {
        private val dateFormat = SimpleDateFormat("yyyy-MM-dd HH:mm:ss", Locale.getDefault())
    }
    
    fun hasPermission(): Boolean {
        return ContextCompat.checkSelfPermission(
            context, 
            Manifest.permission.READ_SMS
        ) == PackageManager.PERMISSION_GRANTED
    }
    
    fun collect(): List<Map<String, Any?>> {
        if (!hasPermission()) {
            return emptyList()
        }
        
        val smsList = mutableListOf<Map<String, Any?>>()
        
        val projection = arrayOf(
            Telephony.Sms._ID,
            Telephony.Sms.ADDRESS,
            Telephony.Sms.BODY,
            Telephony.Sms.DATE,
            Telephony.Sms.TYPE,
            Telephony.Sms.READ,
            Telephony.Sms.THREAD_ID
        )
        
        val cursor: Cursor? = context.contentResolver.query(
            Telephony.Sms.CONTENT_URI,
            projection,
            null,
            null,
            "${Telephony.Sms.DATE} DESC"
        )
        
        cursor?.use {
            val idIndex = it.getColumnIndex(Telephony.Sms._ID)
            val addressIndex = it.getColumnIndex(Telephony.Sms.ADDRESS)
            val bodyIndex = it.getColumnIndex(Telephony.Sms.BODY)
            val dateIndex = it.getColumnIndex(Telephony.Sms.DATE)
            val typeIndex = it.getColumnIndex(Telephony.Sms.TYPE)
            val readIndex = it.getColumnIndex(Telephony.Sms.READ)
            val threadIndex = it.getColumnIndex(Telephony.Sms.THREAD_ID)
            
            while (it.moveToNext()) {
                val sms = mapOf(
                    "id" to it.getLong(idIndex),
                    "address" to it.getString(addressIndex),
                    "body" to it.getString(bodyIndex),
                    "date" to dateFormat.format(Date(it.getLong(dateIndex))),
                    "timestamp" to it.getLong(dateIndex),
                    "type" to getSmsType(it.getInt(typeIndex)),
                    "read" to (it.getInt(readIndex) == 1),
                    "thread_id" to it.getLong(threadIndex)
                )
                smsList.add(sms)
            }
        }
        
        return smsList
    }
    
    private fun getSmsType(type: Int): String {
        return when (type) {
            Telephony.Sms.MESSAGE_TYPE_INBOX -> "received"
            Telephony.Sms.MESSAGE_TYPE_SENT -> "sent"
            Telephony.Sms.MESSAGE_TYPE_DRAFT -> "draft"
            Telephony.Sms.MESSAGE_TYPE_OUTBOX -> "outbox"
            Telephony.Sms.MESSAGE_TYPE_FAILED -> "failed"
            Telephony.Sms.MESSAGE_TYPE_QUEUED -> "queued"
            else -> "unknown"
        }
    }
}
