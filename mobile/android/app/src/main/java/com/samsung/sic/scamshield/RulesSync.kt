package com.samsung.sic.scamshield

import android.content.Context
import android.util.Log
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import org.json.JSONArray
import org.json.JSONObject

/**
 * Đồng bộ bộ luật nhận diện offline từ `GET /api/v1/rules/sync`.
 * Dùng ETag: máy chủ trả 304 khi không có luật mới -> không tốn băng thông,
 * app vẫn nâng cấp được khả năng phát hiện mà không cần cài lại APK.
 */
object RulesSync {

    private const val TAG = "ScamShield_RulesSync"
    private const val PREFS = "scamshield_prefs"
    private const val KEY_VERSION = "rules_version"
    private const val KEY_ETAG = "rules_etag"
    private const val KEY_DOMAINS = "rules_domains"
    private const val KEY_KEYWORDS = "rules_keywords"

    /** Trả về true nếu đồng bộ thành công (kể cả khi đã là bản mới nhất). */
    suspend fun sync(context: Context): Boolean = withContext(Dispatchers.IO) {
        val prefs = context.getSharedPreferences(PREFS, Context.MODE_PRIVATE)
        val response = BackendApi.get("/api/v1/rules/sync", prefs.getString(KEY_ETAG, null))
            ?: return@withContext false

        if (response.code == 304) {
            Log.d(TAG, "Bộ luật đã là bản mới nhất (${prefs.getString(KEY_VERSION, "?")}).")
            return@withContext true
        }

        if (response.code != 200) {
            Log.w(TAG, "Đồng bộ luật thất bại, HTTP ${response.code}.")
            return@withContext false
        }

        try {
            val json = JSONObject(response.body)
            prefs.edit()
                .putString(KEY_VERSION, json.optString("version", "unknown"))
                .putString(KEY_ETAG, response.etag)
                .putString(KEY_DOMAINS, json.optJSONArray("new_emerging_malicious_domains").toLineList())
                .putString(KEY_KEYWORDS, json.optJSONArray("new_scam_keywords").toLineList())
                .apply()
            Log.i(TAG, "Đã cập nhật bộ luật version ${json.optString("version")}.")
            true
        } catch (e: Exception) {
            Log.e(TAG, "Dữ liệu luật không hợp lệ: ${e.message}")
            false
        }
    }

    fun syncedDomains(context: Context): List<String> = readList(context, KEY_DOMAINS)

    fun syncedKeywords(context: Context): List<String> = readList(context, KEY_KEYWORDS)

    private fun readList(context: Context, key: String): List<String> =
        context.getSharedPreferences(PREFS, Context.MODE_PRIVATE)
            .getString(key, "")
            .orEmpty()
            .lineSequence()
            .map { it.trim().lowercase() }
            .filter { it.isNotEmpty() }
            .toList()

    private fun JSONArray?.toLineList(): String {
        if (this == null) return ""
        return (0 until length())
            .mapNotNull { optString(it, "").trim() }
            .filter { it.isNotEmpty() }
            .joinToString("\n")
    }
}
