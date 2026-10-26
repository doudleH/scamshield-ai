package com.samsung.sic.scamshield.scan

import android.content.Context
import android.provider.Telephony
import com.samsung.sic.scamshield.SmsReceiver

class SmsInboxScanner(private val context: Context) {

    data class InboxScanResult(
        val sender: String,
        val date: Long,
        val preview: String,
        val fullBody: String,
        val riskPercent: Int,
        val reason: String,
        val alertLevel: String,
        val isScam: Boolean = false
    )

    fun scanInbox(
        onProgress: (current: Int, total: Int) -> Unit,
        onComplete: (List<InboxScanResult>) -> Unit
    ) {
        val results = mutableListOf<InboxScanResult>()
        val engine = SmsReceiver()

        val projection = arrayOf(
            Telephony.Sms.ADDRESS,
            Telephony.Sms.BODY,
            Telephony.Sms.DATE
        )

        val cursor = context.contentResolver.query(
            Telephony.Sms.Inbox.CONTENT_URI,
            projection,
            null,
            null,
            "${Telephony.Sms.DATE} DESC"
        )

        cursor?.use { c ->
            val total = minOf(c.count, 500)
            var current = 0

            while (c.moveToNext() && current < 500) {
                current++
                onProgress(current, total)

                val sender = c.getString(0) ?: "Không rõ"
                val body = c.getString(1) ?: continue
                val date = c.getLong(2)

                val result = engine.evaluateScamRiskOnDevice(sender, body)

                results.add(
                    InboxScanResult(
                        sender = sender,
                        date = date,
                        preview = body.take(100),
                        fullBody = body,
                        riskPercent = result.riskPercent,
                        reason = if (result.isScam) result.reason else "Nội dung an toàn, không có dấu hiệu lừa đảo.",
                        alertLevel = result.alertLevel,
                        isScam = result.isScam
                    )
                )
            }
        }

        onComplete(results.sortedWith(compareByDescending<InboxScanResult> { it.riskPercent }.thenByDescending { it.date }))
    }
}
