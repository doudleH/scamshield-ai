package com.samsung.sic.scamshield

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.os.Build
import android.provider.Telephony
import android.telephony.SmsMessage
import android.util.Log
import com.samsung.sic.scamshield.history.AlertDatabase
import com.samsung.sic.scamshield.history.AlertRecord
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import org.json.JSONObject
import java.io.OutputStreamWriter
import java.net.HttpURLConnection
import java.net.URL

class SmsReceiver : BroadcastReceiver() {

    companion object {
        private const val TAG = "ScamShield_SmsReceiver"
        private const val BACKEND_API_URL = "http://10.0.2.2:8000/api/v1/scan"

        private val TRUSTED_BANK_SENDERS = setOf(
            "VIETCOMBANK", "VCB", "MBBANK", "TECHCOMBANK", "TCB", "BIDV",
            "AGRIBANK", "ACB", "VPBANK", "TPBANK", "SACOMBANK", "VIB",
            "VIETTELMONEY", "MOMO", "ZALOPAY", "VNPAY"
        )

        private val TRUSTED_DOMAINS = setOf(
            "vietcombank.com.vn", "bidv.com.vn", "mbbank.com.vn", "techcombank.com.vn",
            "agribank.com.vn", "acb.com.vn", "vpbank.com.vn", "tpbank.com.vn",
            "sacombank.com.vn", "vib.com.vn", "shb.com.vn", "hdbank.com.vn",
            "viettelmoney.vn", "momo.vn", "zalopay.vn", "vnpay.vn",
            "chinhphu.vn", "ncsc.vn", "vnexpress.net", "dantri.com.vn", "tuoitre.vn",
            "thanhnien.vn", "vietnamnet.vn", "vtv.vn", "zalo.me",
            "google.com", "facebook.com", "youtube.com"
        )

        private val BANK_BRAND_TOKENS = listOf(
            "bidv", "vietcombank", "vcb", "mbbank", "techcombank", "tcb",
            "agribank", "vpbank", "tpbank", "sacombank", "acb", "vib"
        )
    }

    override fun onReceive(context: Context?, intent: Intent?) {
        if (context == null || intent == null) return

        val prefs = context.getSharedPreferences("scamshield_prefs", Context.MODE_PRIVATE)
        val isProtectionEnabled = prefs.getBoolean("is_protection_enabled", true)
        if (!isProtectionEnabled) {
            Log.d(TAG, "Chế độ bảo vệ đang tắt. Bỏ qua tin nhắn.")
            return
        }

        if (intent.action == Telephony.Sms.Intents.SMS_RECEIVED_ACTION) {
            val messages: Array<SmsMessage>? = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.KITKAT) {
                Telephony.Sms.Intents.getMessagesFromIntent(intent)
            } else {
                null
            }

            if (messages.isNullOrEmpty()) return

            val sender = messages[0].originatingAddress ?: "Không rõ người gửi"
            val fullBody = StringBuilder()
            for (msg in messages) {
                fullBody.append(msg.messageBody)
            }
            val originalSms = fullBody.toString()

            Log.d(TAG, "Nhận tin nhắn từ: $sender")

            if (isLegitimateBankOtpMessage(sender, originalSms)) {
                Log.i(TAG, "Bỏ qua tin nhắn xác thực ngân hàng chính thống.")
                return
            }

            val sanitizedSms = redactSensitiveDataOnDevice(originalSms)

            CoroutineScope(Dispatchers.IO).launch {
                processSmsDetection(context, sender, originalSms, sanitizedSms)
            }
        }
    }

    private fun processSmsDetection(context: Context, sender: String, displaySms: String, safeSms: String) {
        val localResult = evaluateScamRiskOnDevice(sender, displaySms)

        if (localResult.isScam) {
            Log.i(TAG, "Phát hiện mối đe dọa: ${localResult.reason} (${localResult.riskPercent}%)")

            CoroutineScope(Dispatchers.IO).launch {
                try {
                    val db = AlertDatabase.getDatabase(context)
                    db.alertDao().insertAlert(
                        AlertRecord(
                            sender = sender,
                            timestamp = System.currentTimeMillis(),
                            preview = displaySms.take(100),
                            riskPercent = localResult.riskPercent,
                            alertLevel = localResult.alertLevel,
                            reason = localResult.reason
                        )
                    )
                    Log.d(TAG, "Đã lưu cảnh báo vào lịch sử.")
                } catch (e: Exception) {
                    Log.e(TAG, "Lỗi lưu database: ${e.message}")
                }
            }

            NotificationHelper.showScamAlertNotification(
                context = context,
                sender = sender,
                alertLevel = localResult.alertLevel,
                statusLabel = localResult.statusLabel,
                riskPercent = localResult.riskPercent,
                reason = localResult.reason,
                fullMessage = displaySms
            )
            return
        }

        try {
            val url = URL(BACKEND_API_URL)
            val conn = url.openConnection() as HttpURLConnection
            conn.requestMethod = "POST"
            conn.setRequestProperty("Content-Type", "application/json; charset=utf-8")
            conn.setRequestProperty("Accept", "application/json")
            conn.doOutput = true
            conn.connectTimeout = 2000
            conn.readTimeout = 2500

            val payload = JSONObject().apply {
                put("sms_text", safeSms)
                put("url_text", "")
            }

            OutputStreamWriter(conn.outputStream).use { writer ->
                writer.write(payload.toString())
                writer.flush()
            }

            if (conn.responseCode == HttpURLConnection.HTTP_OK) {
                val responseText = conn.inputStream.bufferedReader().use { it.readText() }
                val jsonRes = JSONObject(responseText)
                val alertLevel = jsonRes.optString("alert_level", "SAFE")
                val statusLabel = jsonRes.optString("status_label", "")
                val riskScore = jsonRes.optDouble("overall_risk_score", 0.0)
                val reasonsArray = jsonRes.optJSONArray("reasons")

                val reasonsSummary = if (reasonsArray != null && reasonsArray.length() > 0) {
                    reasonsArray.getString(0)
                } else {
                    "Phát hiện dấu hiệu rủi ro từ máy chủ phân tích."
                }

                if (alertLevel == "DANGEROUS" || alertLevel == "CAUTION") {
                    NotificationHelper.showScamAlertNotification(
                        context = context,
                        sender = sender,
                        alertLevel = alertLevel,
                        statusLabel = statusLabel,
                        riskPercent = (riskScore * 100).toInt(),
                        reason = reasonsSummary,
                        fullMessage = displaySms
                    )
                }
            }
            conn.disconnect()
        } catch (e: Exception) {
            Log.d(TAG, "Dịch vụ máy chủ tạm thời ngoại tuyến, sử dụng kết quả kiểm tra thiết bị.")
        }
    }

    fun evaluateScamRiskOnDevice(sender: String, content: String): OnDeviceResult {
        val lower = content.lowercase()
        var riskScore = 0
        val reasons = mutableListOf<String>()

        val domainRegex = Regex("""(?i)\b([a-zA-Z0-9-]+\.)+(?:com|vn|net|org|xyz|top|site|vip|club|cc|me|online|info|biz)\b""")
        val allExtractedDomains = domainRegex.findAll(content).map { it.value.lowercase() }.toList()

        var hasUntrustedDomain = false
        var hasBankTyposquatting = false
        var fakeBankDomainName = ""
        var hasGoogleDecoy = false

        for (domain in allExtractedDomains) {
            val isGov = domain.endsWith(".gov.vn")
            val isWhitelisted = TRUSTED_DOMAINS.any { domain == it || domain.endsWith(".$it") }

            if (!isGov && !isWhitelisted) {
                hasUntrustedDomain = true

                for (bankToken in BANK_BRAND_TOKENS) {
                    if (domain.contains(bankToken)) {
                        hasBankTyposquatting = true
                        fakeBankDomainName = domain
                        break
                    }
                }
            }

            if (domain.contains("google.com") && hasUntrustedDomain) {
                hasGoogleDecoy = true
            }
        }

        val gamblingNoSpaceKeywords = listOf(
            "phanthuong", "phầnthưởng", "traophucloi", "phucloi", "phúclợi",
            "naptien", "nạptiền", "lannap", "lầnnạp", "nhanthem", "nhậnthêm",
            "100phantram", "100%", "daithang", "đạithắng", "dangkinhan", "đăngkýnhận",
            "taotaikhoan", "tạotàikhoản", "nhan201ngin", "585nghin", "nhan88k",
            "cobac", "cờbạc", "taixiu", "tài xỉu", "nohu", "nổhũ", "gamebai", "baccarat"
        )
        val gamblingMatches = gamblingNoSpaceKeywords.filter { lower.contains(it) }

        val regularScamKeywords = listOf(
            "phan thuong", "phần thưởng", "trung thuong", "trúng thưởng", "nhan qua", "nhận quà",
            "tri an", "tri ân", "vip", "khoa the", "khóa thẻ", "tai khoan bi khoa", "tài khoản bị khóa",
            "xac minh", "xác minh", "24h", "phat nguoi", "phạt nguội", "cong an", "công an",
            "vay von", "vay vốn", "giai ngan", "giải ngân", "viec lam", "chot don"
        )
        val regularMatches = regularScamKeywords.filter { lower.contains(it) }

        if (hasBankTyposquatting) {
            riskScore = maxOf(riskScore, 98)
            reasons.add("Phát hiện tên miền lạ mạo danh thương hiệu ngân hàng: '$fakeBankDomainName'")
        }

        if (gamblingMatches.size >= 2) {
            riskScore = maxOf(riskScore, 96)
            reasons.add("Chứa các từ khóa lừa đảo nạp tiền tặng thưởng viết dính liền: ${gamblingMatches.take(3).joinToString(", ")}")
        } else if (gamblingMatches.size == 1 && hasUntrustedDomain) {
            riskScore = maxOf(riskScore, 92)
            reasons.add("Dụ dỗ nhận phần thưởng phúc lợi kèm liên kết lạ chưa xác minh")
        }

        if (hasGoogleDecoy) {
            riskScore = maxOf(riskScore, 97)
            reasons.add("Sử dụng kỹ thuật chèn liên kết trung gian để ngụy trang")
        }

        if (regularMatches.size >= 2) {
            riskScore = maxOf(riskScore, 90)
            reasons.add("Phát hiện các từ khóa kích động tâm lý khẩn cấp: ${regularMatches.take(3).joinToString(", ")}")
        } else if (regularMatches.size == 1 && hasUntrustedDomain) {
            riskScore = maxOf(riskScore, 88)
            reasons.add("Yêu cầu thao tác khẩn cấp kèm liên kết ngoài chưa được xác thực")
        }

        val isPersonalPhone = sender.startsWith("+84") || (sender.startsWith("0") && sender.length in 10..12)
        if (isPersonalPhone && (hasBankTyposquatting || BANK_BRAND_TOKENS.any { lower.contains(it) })) {
            riskScore = maxOf(riskScore, 85)
            reasons.add("Số điện thoại cá nhân ($sender) giả danh thông báo ngân hàng")
        }

        return if (riskScore >= 70) {
            OnDeviceResult(
                isScam = true,
                alertLevel = "DANGEROUS",
                statusLabel = "CẢNH BÁO NGUY CƠ CAO",
                riskPercent = riskScore,
                reason = reasons.joinToString(". ")
            )
        } else if (riskScore >= 40) {
            OnDeviceResult(
                isScam = true,
                alertLevel = "CAUTION",
                statusLabel = "CẢNH BÁO ĐÁNG NGỜ",
                riskPercent = riskScore,
                reason = reasons.joinToString(". ")
            )
        } else {
            OnDeviceResult(
                isScam = false,
                alertLevel = "SAFE",
                statusLabel = "AN TOÀN",
                riskPercent = riskScore,
                reason = "Không phát hiện dấu hiệu bất thường."
            )
        }
    }

    private fun isLegitimateBankOtpMessage(sender: String, content: String): Boolean {
        val cleanSender = sender.uppercase().replace(" ", "").replace("-", "")
        val isBankSender = TRUSTED_BANK_SENDERS.any { cleanSender.contains(it) }
        val lowerContent = content.lowercase()
        val hasOtpKeyword = lowerContent.contains("otp") || lowerContent.contains("mã xác thực") || lowerContent.contains("ma xac thuc")
        val hasAnyLink = lowerContent.contains("http://") || lowerContent.contains("https://") ||
                         lowerContent.contains(".xyz") || lowerContent.contains(".top") ||
                         lowerContent.contains(".site") || lowerContent.contains(".com")
        return isBankSender && hasOtpKeyword && !hasAnyLink
    }

    private fun redactSensitiveDataOnDevice(rawText: String): String {
        var text = rawText
        val otpPattern = Regex("""(?i)(?:mã\s*(?:otp|xác\s*thực)?|otp\s*(?:code|is|là)?\s*[:\s]*)([0-9]{4,8})\b""")
        text = text.replace(otpPattern) { matchResult ->
            val prefix = matchResult.value.substring(0, matchResult.value.length - matchResult.groupValues[1].length)
            "$prefix[MÃ_XÁC_THỰC_ĐÃ_ẨN_DANH]"
        }
        val cardPattern = Regex("""\b\d{10,19}\b""")
        text = text.replace(cardPattern, "[SỐ_TÀI_KHOẢN_ĐÃ_ẨN_DANH]")
        return text
    }

    data class OnDeviceResult(
        val isScam: Boolean,
        val alertLevel: String,
        val statusLabel: String,
        val riskPercent: Int,
        val reason: String
    )
}
