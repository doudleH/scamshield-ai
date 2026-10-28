package com.samsung.sic.scamshield

import android.util.Log
import java.io.BufferedReader
import java.net.HttpURLConnection
import java.net.URL

/**
 * Cổng giao tiếp duy nhất tới backend FastAPI (Module 2 — Backend & MLOps).
 * Mặc định trỏ emulator (10.0.2.2). Khi build cho máy thật / bản cloud:
 *   ./gradlew assembleDebug -PAPI_BASE_URL=https://scamshield-api.onrender.com
 */
object BackendApi {

    private const val TAG = "ScamShield_BackendApi"

    val baseUrl: String = BuildConfig.API_BASE_URL.trimEnd('/')

    data class Response(val code: Int, val body: String, val etag: String?)

    fun get(path: String, etag: String? = null, timeoutMs: Int = 4000): Response? =
        request("GET", path, null, etag, timeoutMs)

    fun post(path: String, payload: String, timeoutMs: Int = 4000): Response? =
        request("POST", path, payload, null, timeoutMs)

    private fun request(method: String, path: String, payload: String?, etag: String?, timeoutMs: Int): Response? {
        var conn: HttpURLConnection? = null
        return try {
            conn = URL(baseUrl + path).openConnection() as HttpURLConnection
            conn.requestMethod = method
            conn.connectTimeout = timeoutMs
            conn.readTimeout = timeoutMs
            conn.setRequestProperty("Accept", "application/json")
            if (etag != null) conn.setRequestProperty("If-None-Match", etag)
            if (payload != null) {
                conn.setRequestProperty("Content-Type", "application/json; charset=utf-8")
                conn.doOutput = true
                conn.outputStream.use { it.write(payload.toByteArray(Charsets.UTF_8)) }
            }

            val code = conn.responseCode
            val stream = if (code in 200..299) conn.inputStream else conn.errorStream
            val body = stream?.bufferedReader()?.use(BufferedReader::readText).orEmpty()
            Response(code, body, conn.getHeaderField("ETag"))
        } catch (e: Exception) {
            Log.d(TAG, "Backend không phản hồi ($method $path): ${e.message}")
            null
        } finally {
            conn?.disconnect()
        }
    }
}
