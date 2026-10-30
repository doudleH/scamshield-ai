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

class SmsReceiver : BroadcastReceiver() {

    companion object {
        private const val TAG = "ScamShield_SmsReceiver"

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
            Log.d(TAG, "Cháº¿ Ä‘á»™ báº£o vá»‡ Ä‘ang táº¯t. Bá» qua tin nháº¯n.")
            return
        }

        if (intent.action == Telephony.Sms.Intents.SMS_RECEIVED_ACTION) {
            val messages: Array<SmsMessage>? = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.KITKAT) {
                Telephony.Sms.Intents.getMessagesFromIntent(intent)
            } else {
                null
            }

            if (messages.isNullOrEmpty()) return

            val sender = messages[0].originatingAddress ?: "KhÃ´ng rÃµ ngÆ°á»i gá»­i"
            val fullBody = StringBuilder()
            for (msg in messages) {
                fullBody.append(msg.messageBody)
            }
            val originalSms = fullBody.toString()

            Log.d(TAG, "Nháº­n tin nháº¯n tá»«: $sender")

            if (isLegitimateBankOtpMessage(sender, originalSms)) {
                Log.i(TAG, "Bá» qua tin nháº¯n xÃ¡c thá»±c ngÃ¢n hÃ ng chÃ­nh thá»‘ng.")
                return
            }

            val sanitizedSms = redactSensitiveDataOnDevice(originalSms)

            CoroutineScope(Dispatchers.IO).launch {
                processSmsDetection(context, sender, originalSms, sanitizedSms)
            }
        }
    }

    private fun processSmsDetection(context: Context, sender: String, displaySms: String, safeSms: String) {
        val localResult = evaluateScamRiskOnDevice(
            sender = sender,
            content = displaySms,
            extraDomains = RulesSync.syncedDomains(context),
            extraKeywords = RulesSync.syncedKeywords(context)
        )

        if (localResult.isScam) {
            Log.i(TAG, "PhÃ¡t hiá»‡n má»‘i Ä‘e dá»a: ${localResult.reason} (${localResult.riskPercent}%)")

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
                    Log.d(TAG, "ÄÃ£ lÆ°u cáº£nh bÃ¡o vÃ o lá»‹ch sá»­.")
                } catch (e: Exception) {
                    Log.e(TAG, "Lá»—i lÆ°u database: ${e.message}")
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

        val payload = JSONObject().apply {
            put("sms_text", safeSms)
            put("url_text", "")
        }

        val response = BackendApi.post("/api/v1/scan", payload.toString(), timeoutMs = 2500)
        if (response == null || response.code != 200) {
            Log.d(TAG, "Dá»‹ch vá»¥ mÃ¡y chá»§ táº¡m thá»i ngoáº¡i tuyáº¿n, sá»­ dá»¥ng káº¿t quáº£ kiá»ƒm tra thiáº¿t bá»‹.")
            return
        }

        try {
            val jsonRes = JSONObject(response.body)
            val alertLevel = jsonRes.optString("alert_level", "SAFE")
            val statusLabel = jsonRes.optString("status_label", "")
            val riskScore = jsonRes.optDouble("overall_risk_score", 0.0)
            val reasonsArray = jsonRes.optJSONArray("reasons")

            val reasonsSummary = if (reasonsArray != null && reasonsArray.length() > 0) {
                reasonsArray.getString(0)
            } else {
                "PhÃ¡t hiá»‡n dáº¥u hiá»‡u rá»§i ro tá»« mÃ¡y chá»§ phÃ¢n tÃ­ch."
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
        } catch (e: Exception) {
            Log.e(TAG, "Pháº£n há»“i mÃ¡y chá»§ khÃ´ng há»£p lá»‡: ${e.message}")
        }
    }

    fun evaluateScamRiskOnDevice(
        sender: String,
        content: String,
        extraDomains: List<String> = emptyList(),
        extraKeywords: List<String> = emptyList()
    ): OnDeviceResult {
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
            "phanthuong", "pháº§nthÆ°á»Ÿng", "traophucloi", "phucloi", "phÃºclá»£i",
            "naptien", "náº¡ptiá»n", "lannap", "láº§nnáº¡p", "nhanthem", "nháº­nthÃªm",
            "100phantram", "100%", "daithang", "Ä‘áº¡itháº¯ng", "dangkinhan", "Ä‘ÄƒngkÃ½nháº­n",
            "taotaikhoan", "táº¡otÃ ikhoáº£n", "nhan201ngin", "585nghin", "nhan88k",
            "cobac", "cá»báº¡c", "taixiu", "tÃ i xá»‰u", "nohu", "ná»•hÅ©", "gamebai", "baccarat"
        )
        val gamblingMatches = gamblingNoSpaceKeywords.filter { lower.contains(it) }

        val regularScamKeywords = listOf(
            "phan thuong", "pháº§n thÆ°á»Ÿng", "trung thuong", "trÃºng thÆ°á»Ÿng", "nhan qua", "nháº­n quÃ ",
            "tri an", "tri Ã¢n", "vip", "khoa the", "khÃ³a tháº»", "tai khoan bi khoa", "tÃ i khoáº£n bá»‹ khÃ³a",
            "xac minh", "xÃ¡c minh", "24h", "phat nguoi", "pháº¡t nguá»™i", "cong an", "cÃ´ng an",
            "vay von", "vay vá»‘n", "giai ngan", "giáº£i ngÃ¢n", "viec lam", "chot don",
            "tuyen dung", "lam tai nha", "luong cao", "xu ly don hang",
            "tra luong trong ngay", "lien he zalo", "khong can kinh nghiem",
            "kiem tien", "thu dong", "tham gia nhom", "nhan nhiem vu",
            "tha tim", "xem video", "telegram", "kiemtien"
        )
        val regularMatches = regularScamKeywords.filter { lower.contains(it) }

        val syncedDomainHit = allExtractedDomains.firstOrNull { domain ->
            extraDomains.any { domain == it || domain.endsWith(".$it") }
        }
        if (syncedDomainHit != null) {
            riskScore = maxOf(riskScore, 99)
            reasons.add("TÃªn miá»n náº±m trong danh sÃ¡ch lá»«a Ä‘áº£o cáº­p nháº­t tá»« mÃ¡y chá»§: '$syncedDomainHit'")
        }

        if (hasBankTyposquatting) {
            riskScore = maxOf(riskScore, 98)
            reasons.add("PhÃ¡t hiá»‡n tÃªn miá»n láº¡ máº¡o danh thÆ°Æ¡ng hiá»‡u ngÃ¢n hÃ ng: '$fakeBankDomainName'")
        }

        if (gamblingMatches.size >= 2) {
            riskScore = maxOf(riskScore, 96)
            reasons.add("Chá»©a cÃ¡c tá»« khÃ³a lá»«a Ä‘áº£o náº¡p tiá»n táº·ng thÆ°á»Ÿng viáº¿t dÃ­nh liá»n: ${gamblingMatches.take(3).joinToString(", ")}")
        } else if (gamblingMatches.size == 1 && hasUntrustedDomain) {
            riskScore = maxOf(riskScore, 92)
            reasons.add("Dá»¥ dá»— nháº­n pháº§n thÆ°á»Ÿng phÃºc lá»£i kÃ¨m liÃªn káº¿t láº¡ chÆ°a xÃ¡c minh")
        }

        if (hasGoogleDecoy) {
            riskScore = maxOf(riskScore, 97)
            reasons.add("Sá»­ dá»¥ng ká»¹ thuáº­t chÃ¨n liÃªn káº¿t trung gian Ä‘á»ƒ ngá»¥y trang")
        }

        if (regularMatches.size >= 2) {
            riskScore = maxOf(riskScore, 90)
            reasons.add("PhÃ¡t hiá»‡n cÃ¡c tá»« khÃ³a kÃ­ch Ä‘á»™ng tÃ¢m lÃ½ kháº©n cáº¥p: ${regularMatches.take(3).joinToString(", ")}")
        } else if (regularMatches.size == 1 && hasUntrustedDomain) {
            riskScore = maxOf(riskScore, 88)
            reasons.add("YÃªu cáº§u thao tÃ¡c kháº©n cáº¥p kÃ¨m liÃªn káº¿t ngoÃ i chÆ°a Ä‘Æ°á»£c xÃ¡c thá»±c")
        }

        val syncedMatches = extraKeywords.filter { lower.contains(it) }
        if (syncedMatches.size >= 2) {
            riskScore = maxOf(riskScore, 95)
            reasons.add("Khá»›p tá»« khÃ³a lá»«a Ä‘áº£o cáº­p nháº­t tá»« mÃ¡y chá»§: ${syncedMatches.take(3).joinToString(", ")}")
        } else if (syncedMatches.size == 1 && hasUntrustedDomain) {
            riskScore = maxOf(riskScore, 92)
            reasons.add("Dáº¥u hiá»‡u lá»«a Ä‘áº£o má»›i cáº­p nháº­t kÃ¨m liÃªn káº¿t ngoÃ i chÆ°a xÃ¡c thá»±c")
        }

        val isPersonalPhone = sender.startsWith("+84") || (sender.startsWith("0") && sender.length in 10..12)
        if (isPersonalPhone && (hasBankTyposquatting || BANK_BRAND_TOKENS.any { lower.contains(it) })) {
            riskScore = maxOf(riskScore, 85)
            reasons.add("Sá»‘ Ä‘iá»‡n thoáº¡i cÃ¡ nhÃ¢n ($sender) giáº£ danh thÃ´ng bÃ¡o ngÃ¢n hÃ ng")
        }

        return if (riskScore >= 70) {
            OnDeviceResult(
                isScam = true,
                alertLevel = "DANGEROUS",
                statusLabel = "Cáº¢NH BÃO NGUY CÆ  CAO",
                riskPercent = riskScore,
                reason = reasons.joinToString(". ")
            )
        } else if (riskScore >= 40) {
            OnDeviceResult(
                isScam = true,
                alertLevel = "CAUTION",
                statusLabel = "Cáº¢NH BÃO ÄÃNG NGá»œ",
                riskPercent = riskScore,
                reason = reasons.joinToString(". ")
            )
        } else {
            OnDeviceResult(
                isScam = false,
                alertLevel = "SAFE",
                statusLabel = "AN TOÃ€N",
                riskPercent = riskScore,
                reason = "KhÃ´ng phÃ¡t hiá»‡n dáº¥u hiá»‡u báº¥t thÆ°á»ng."
            )
        }
    }

    private fun isLegitimateBankOtpMessage(sender: String, content: String): Boolean {
        val cleanSender = sender.uppercase().replace(" ", "").replace("-", "")
        val isBankSender = TRUSTED_BANK_SENDERS.any { cleanSender.contains(it) }
        val lowerContent = content.lowercase()
        val hasOtpKeyword = lowerContent.contains("otp") || lowerContent.contains("mÃ£ xÃ¡c thá»±c") || lowerContent.contains("ma xac thuc")
        val hasAnyLink = lowerContent.contains("http://") || lowerContent.contains("https://") ||
                         lowerContent.contains(".xyz") || lowerContent.contains(".top") ||
                         lowerContent.contains(".site") || lowerContent.contains(".com")
        return isBankSender && hasOtpKeyword && !hasAnyLink
    }

    private fun redactSensitiveDataOnDevice(rawText: String): String {
        var text = rawText
        val otpPattern = Regex("""(?i)(?:mÃ£\s*(?:otp|xÃ¡c\s*thá»±c)?|otp\s*(?:code|is|lÃ )?\s*[:\s]*)([0-9]{4,8})\b""")
        text = text.replace(otpPattern) { matchResult ->
            val prefix = matchResult.value.substring(0, matchResult.value.length - matchResult.groupValues[1].length)
            "$prefix[MÃƒ_XÃC_THá»°C_ÄÃƒ_áº¨N_DANH]"
        }
        val cardPattern = Regex("""\b\d{10,19}\b""")
        text = text.replace(cardPattern, "[Sá»_TÃ€I_KHOáº¢N_ÄÃƒ_áº¨N_DANH]")
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
