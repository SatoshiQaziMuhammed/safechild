package com.safechild.agent.utils

import android.Manifest
import android.content.Context
import android.content.pm.PackageManager
import android.database.Cursor
import android.provider.ContactsContract
import androidx.core.content.ContextCompat

class ContactCollector(private val context: Context) {
    
    fun hasPermission(): Boolean {
        return ContextCompat.checkSelfPermission(
            context, 
            Manifest.permission.READ_CONTACTS
        ) == PackageManager.PERMISSION_GRANTED
    }
    
    fun collect(): List<Map<String, Any?>> {
        if (!hasPermission()) {
            return emptyList()
        }
        
        val contactList = mutableListOf<Map<String, Any?>>()
        val contactMap = mutableMapOf<String, MutableMap<String, Any?>>()
        
        // Get basic contact info
        val contactCursor: Cursor? = context.contentResolver.query(
            ContactsContract.Contacts.CONTENT_URI,
            arrayOf(
                ContactsContract.Contacts._ID,
                ContactsContract.Contacts.DISPLAY_NAME,
                ContactsContract.Contacts.PHOTO_URI,
                ContactsContract.Contacts.HAS_PHONE_NUMBER
            ),
            null,
            null,
            ContactsContract.Contacts.DISPLAY_NAME + " ASC"
        )
        
        contactCursor?.use { cursor ->
            val idIndex = cursor.getColumnIndex(ContactsContract.Contacts._ID)
            val nameIndex = cursor.getColumnIndex(ContactsContract.Contacts.DISPLAY_NAME)
            val photoIndex = cursor.getColumnIndex(ContactsContract.Contacts.PHOTO_URI)
            val hasPhoneIndex = cursor.getColumnIndex(ContactsContract.Contacts.HAS_PHONE_NUMBER)
            
            while (cursor.moveToNext()) {
                val contactId = cursor.getString(idIndex)
                val contact = mutableMapOf<String, Any?>(
                    "id" to contactId,
                    "name" to cursor.getString(nameIndex),
                    "photo_uri" to cursor.getString(photoIndex),
                    "phones" to mutableListOf<Map<String, String>>(),
                    "emails" to mutableListOf<Map<String, String>>()
                )
                contactMap[contactId] = contact
            }
        }
        
        // Get phone numbers
        val phoneCursor: Cursor? = context.contentResolver.query(
            ContactsContract.CommonDataKinds.Phone.CONTENT_URI,
            arrayOf(
                ContactsContract.CommonDataKinds.Phone.CONTACT_ID,
                ContactsContract.CommonDataKinds.Phone.NUMBER,
                ContactsContract.CommonDataKinds.Phone.TYPE,
                ContactsContract.CommonDataKinds.Phone.LABEL
            ),
            null,
            null,
            null
        )
        
        phoneCursor?.use { cursor ->
            val contactIdIndex = cursor.getColumnIndex(ContactsContract.CommonDataKinds.Phone.CONTACT_ID)
            val numberIndex = cursor.getColumnIndex(ContactsContract.CommonDataKinds.Phone.NUMBER)
            val typeIndex = cursor.getColumnIndex(ContactsContract.CommonDataKinds.Phone.TYPE)
            val labelIndex = cursor.getColumnIndex(ContactsContract.CommonDataKinds.Phone.LABEL)
            
            while (cursor.moveToNext()) {
                val contactId = cursor.getString(contactIdIndex)
                contactMap[contactId]?.let { contact ->
                    val phones = contact["phones"] as MutableList<Map<String, String>>
                    phones.add(mapOf(
                        "number" to (cursor.getString(numberIndex) ?: ""),
                        "type" to getPhoneType(cursor.getInt(typeIndex)),
                        "label" to (cursor.getString(labelIndex) ?: "")
                    ))
                }
            }
        }
        
        // Get emails
        val emailCursor: Cursor? = context.contentResolver.query(
            ContactsContract.CommonDataKinds.Email.CONTENT_URI,
            arrayOf(
                ContactsContract.CommonDataKinds.Email.CONTACT_ID,
                ContactsContract.CommonDataKinds.Email.ADDRESS,
                ContactsContract.CommonDataKinds.Email.TYPE
            ),
            null,
            null,
            null
        )
        
        emailCursor?.use { cursor ->
            val contactIdIndex = cursor.getColumnIndex(ContactsContract.CommonDataKinds.Email.CONTACT_ID)
            val addressIndex = cursor.getColumnIndex(ContactsContract.CommonDataKinds.Email.ADDRESS)
            val typeIndex = cursor.getColumnIndex(ContactsContract.CommonDataKinds.Email.TYPE)
            
            while (cursor.moveToNext()) {
                val contactId = cursor.getString(contactIdIndex)
                contactMap[contactId]?.let { contact ->
                    val emails = contact["emails"] as MutableList<Map<String, String>>
                    emails.add(mapOf(
                        "address" to (cursor.getString(addressIndex) ?: ""),
                        "type" to getEmailType(cursor.getInt(typeIndex))
                    ))
                }
            }
        }
        
        contactList.addAll(contactMap.values)
        return contactList
    }
    
    private fun getPhoneType(type: Int): String {
        return when (type) {
            ContactsContract.CommonDataKinds.Phone.TYPE_HOME -> "home"
            ContactsContract.CommonDataKinds.Phone.TYPE_MOBILE -> "mobile"
            ContactsContract.CommonDataKinds.Phone.TYPE_WORK -> "work"
            ContactsContract.CommonDataKinds.Phone.TYPE_FAX_HOME -> "fax_home"
            ContactsContract.CommonDataKinds.Phone.TYPE_FAX_WORK -> "fax_work"
            ContactsContract.CommonDataKinds.Phone.TYPE_MAIN -> "main"
            ContactsContract.CommonDataKinds.Phone.TYPE_OTHER -> "other"
            else -> "unknown"
        }
    }
    
    private fun getEmailType(type: Int): String {
        return when (type) {
            ContactsContract.CommonDataKinds.Email.TYPE_HOME -> "home"
            ContactsContract.CommonDataKinds.Email.TYPE_WORK -> "work"
            ContactsContract.CommonDataKinds.Email.TYPE_MOBILE -> "mobile"
            ContactsContract.CommonDataKinds.Email.TYPE_OTHER -> "other"
            else -> "unknown"
        }
    }
}
