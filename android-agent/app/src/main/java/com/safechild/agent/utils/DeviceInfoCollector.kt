package com.safechild.agent.utils

import android.content.Context
import android.os.Build
import android.provider.Settings
import java.text.SimpleDateFormat
import java.util.*

object DeviceInfoCollector {
    
    fun collect(context: Context): Map<String, Any?> {
        return mapOf(
            "collection_timestamp" to SimpleDateFormat("yyyy-MM-dd HH:mm:ss", Locale.getDefault()).format(Date()),
            "timezone" to TimeZone.getDefault().id,
            "device" to mapOf(
                "manufacturer" to Build.MANUFACTURER,
                "model" to Build.MODEL,
                "brand" to Build.BRAND,
                "device" to Build.DEVICE,
                "product" to Build.PRODUCT,
                "hardware" to Build.HARDWARE
            ),
            "os" to mapOf(
                "version" to Build.VERSION.RELEASE,
                "sdk_int" to Build.VERSION.SDK_INT,
                "security_patch" to if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) Build.VERSION.SECURITY_PATCH else "unknown",
                "incremental" to Build.VERSION.INCREMENTAL
            ),
            "android_id" to Settings.Secure.getString(context.contentResolver, Settings.Secure.ANDROID_ID),
            "app_version" to getAppVersion(context),
            "locale" to Locale.getDefault().toString()
        )
    }
    
    private fun getAppVersion(context: Context): String {
        return try {
            val packageInfo = context.packageManager.getPackageInfo(context.packageName, 0)
            "${packageInfo.versionName} (${packageInfo.longVersionCode})"
        } catch (e: Exception) {
            "unknown"
        }
    }
}
