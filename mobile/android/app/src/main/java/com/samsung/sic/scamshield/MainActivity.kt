package com.samsung.sic.scamshield

import android.Manifest
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.graphics.Color
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.provider.Settings
import android.view.View
import android.widget.Button
import android.widget.EditText
import android.widget.ImageButton
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import androidx.appcompat.app.AppCompatDelegate
import androidx.cardview.widget.CardView
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import androidx.lifecycle.lifecycleScope
import com.samsung.sic.scamshield.history.AlertDatabase
import com.samsung.sic.scamshield.history.AlertHistoryActivity
import com.samsung.sic.scamshield.history.AlertRecord
import com.samsung.sic.scamshield.scan.ScanResultsActivity
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch

class MainActivity : AppCompatActivity() {

    companion object {
        private const val PERMISSION_REQUEST_CODE = 2026
        private const val PREFS_NAME = "scamshield_prefs"
        private const val KEY_PROTECTION_ENABLED = "is_protection_enabled"
        private const val KEY_DARK_MODE = "is_dark_mode"
    }

    private lateinit var tvStatus: TextView
    private lateinit var tvDetails: TextView
    private lateinit var cardStatus: CardView
    private lateinit var cardAlertDetails: CardView
    private lateinit var viewAlertDetailsAccent: View
    private lateinit var btnToggleProtection: Button
    private lateinit var btnOpenSettings: Button
    private lateinit var btnThemeToggle: ImageButton
    private lateinit var etCustomSms: EditText
    private lateinit var btnTestCustomSms: Button
    private lateinit var cardScanInbox: CardView
    private lateinit var cardAlertHistory: CardView
    private lateinit var btnReportCurrentAlert: Button
    private lateinit var btnOpenCurrentSms: Button

    override fun onCreate(savedInstanceState: Bundle?) {
        val prefs = getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
        val isDarkMode = prefs.getBoolean(KEY_DARK_MODE, true)
        val defaultMode = if (isDarkMode) AppCompatDelegate.MODE_NIGHT_YES else AppCompatDelegate.MODE_NIGHT_NO
        if (AppCompatDelegate.getDefaultNightMode() != defaultMode) {
            AppCompatDelegate.setDefaultNightMode(defaultMode)
        }

        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        tvStatus = findViewById(R.id.tvProtectionStatus)
        tvDetails = findViewById(R.id.tvAlertDetails)
        cardStatus = findViewById(R.id.cardStatus)
        cardAlertDetails = findViewById(R.id.cardAlertDetails)
        viewAlertDetailsAccent = findViewById(R.id.viewAlertDetailsAccent)
        btnToggleProtection = findViewById(R.id.btnToggleProtection)
        btnOpenSettings = findViewById(R.id.btnOpenSettings)
        btnThemeToggle = findViewById(R.id.btnThemeToggle)
        etCustomSms = findViewById(R.id.etCustomSms)
        btnTestCustomSms = findViewById(R.id.btnTestCustomSms)
        cardScanInbox = findViewById(R.id.cardScanInbox)
        cardAlertHistory = findViewById(R.id.cardAlertHistory)
        btnReportCurrentAlert = findViewById(R.id.btnReportCurrentAlert)
        btnOpenCurrentSms = findViewById(R.id.btnOpenCurrentSms)

        NotificationHelper.createNotificationChannel(this)

        updateThemeToggleIcon(isDarkMode)
        updateUIState()

        btnThemeToggle.setOnClickListener {
            val currentMode = prefs.getBoolean(KEY_DARK_MODE, true)
            val newMode = !currentMode
            prefs.edit().putBoolean(KEY_DARK_MODE, newMode).apply()
            updateThemeToggleIcon(newMode)
            AppCompatDelegate.setDefaultNightMode(
                if (newMode) AppCompatDelegate.MODE_NIGHT_YES else AppCompatDelegate.MODE_NIGHT_NO
            )
        }

        btnToggleProtection.setOnClickListener {
            if (!hasSmsPermissions()) {
                requestSmsPermissions()
            } else {
                toggleProtectionState()
            }
        }

        cardScanInbox.setOnClickListener {
            if (!hasSmsPermissions()) {
                requestSmsPermissions()
            } else {
                startActivity(Intent(this, ScanResultsActivity::class.java))
            }
        }

        val tvAlertHistorySubtitle: TextView = findViewById(R.id.tvAlertHistorySubtitle)
        AlertDatabase.getDatabase(this).alertDao().getTotalCount().observe(this) { count ->
            if (count != null && count > 0) {
                tvAlertHistorySubtitle.text = "${FormatUtils.formatBadgeCount(count)} mối đe dọa"
                tvAlertHistorySubtitle.setTextColor(ContextCompat.getColor(this, R.color.status_danger))
            } else {
                tvAlertHistorySubtitle.text = "Xem các mối đe dọa"
                tvAlertHistorySubtitle.setTextColor(ContextCompat.getColor(this, R.color.text_secondary))
            }
        }

        cardAlertHistory.setOnClickListener {
            startActivity(Intent(this, AlertHistoryActivity::class.java))
        }

        btnOpenSettings.setOnClickListener {
            openAppSettings()
        }

        btnTestCustomSms.setOnClickListener {
            testCustomMessage()
        }

        handleIntentData()
    }

    override fun onResume() {
        super.onResume()
        updateUIState()
    }

    private fun updateThemeToggleIcon(isDark: Boolean) {
        if (isDark) {
            btnThemeToggle.setImageResource(R.drawable.ic_light_mode)
            btnThemeToggle.imageTintList = ContextCompat.getColorStateList(this, R.color.text_primary)
            btnThemeToggle.contentDescription = "Chuyển sang chế độ sáng"
        } else {
            btnThemeToggle.setImageResource(R.drawable.ic_dark_mode)
            btnThemeToggle.imageTintList = ContextCompat.getColorStateList(this, R.color.text_primary)
            btnThemeToggle.contentDescription = "Chuyển sang chế độ tối"
        }
    }

    private fun hasSmsPermissions(): Boolean {
        val hasReceive = ContextCompat.checkSelfPermission(this, Manifest.permission.RECEIVE_SMS) == PackageManager.PERMISSION_GRANTED
        val hasRead = ContextCompat.checkSelfPermission(this, Manifest.permission.READ_SMS) == PackageManager.PERMISSION_GRANTED
        return hasReceive && hasRead
    }

    private fun updateUIState() {
        val prefs = getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
        val isEnabled = prefs.getBoolean(KEY_PROTECTION_ENABLED, true)

        if (!hasSmsPermissions()) {
            tvStatus.text = "🔴 THIẾU QUYỀN ĐỌC TIN NHẮN"
            tvStatus.setTextColor(ContextCompat.getColor(this, R.color.status_danger))
            btnToggleProtection.text = "CẤP QUYỀN ĐỌC TIN NHẮN SMS"
            btnToggleProtection.backgroundTintList = ContextCompat.getColorStateList(this, R.color.brand_primary)
            cardStatus.setCardBackgroundColor(ContextCompat.getColor(this, R.color.status_danger_bg))
        } else {
            if (isEnabled) {
                tvStatus.text = "🟢 LÁ CHẮN ĐANG BẬT (BẢO VỆ 24/7)"
                tvStatus.setTextColor(ContextCompat.getColor(this, R.color.status_safe))
                btnToggleProtection.text = "TẠM DỪNG LÁ CHẮN BẢO VỆ"
                btnToggleProtection.backgroundTintList = ContextCompat.getColorStateList(this, R.color.btn_warning)
                cardStatus.setCardBackgroundColor(ContextCompat.getColor(this, R.color.status_safe_bg))
            } else {
                tvStatus.text = "🟡 LÁ CHẮN ĐÃ TẮT (TẠM DỪNG)"
                tvStatus.setTextColor(ContextCompat.getColor(this, R.color.status_caution))
                btnToggleProtection.text = "KÍCH HOẠT LÁ CHẮN BẢO VỆ"
                btnToggleProtection.backgroundTintList = ContextCompat.getColorStateList(this, R.color.btn_safe)
                cardStatus.setCardBackgroundColor(ContextCompat.getColor(this, R.color.status_caution_bg))
            }
        }
    }

    private fun toggleProtectionState() {
        val prefs = getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
        val currentState = prefs.getBoolean(KEY_PROTECTION_ENABLED, true)
        val newState = !currentState

        prefs.edit().putBoolean(KEY_PROTECTION_ENABLED, newState).apply()
        updateUIState()

        if (newState) {
            Toast.makeText(this, "Đã kích hoạt chế độ bảo vệ 24/7", Toast.LENGTH_SHORT).show()
        } else {
            Toast.makeText(this, "Đã tạm dừng bảo vệ tin nhắn", Toast.LENGTH_SHORT).show()
        }
    }

    private fun openAppSettings() {
        val intent = Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS).apply {
            data = Uri.fromParts("package", packageName, null)
        }
        startActivity(intent)
        Toast.makeText(this, "Quản lý quyền tin nhắn SMS trong phần Cài đặt", Toast.LENGTH_LONG).show()
    }

    private fun requestSmsPermissions() {
        val permissions = mutableListOf(Manifest.permission.RECEIVE_SMS, Manifest.permission.READ_SMS)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            permissions.add(Manifest.permission.POST_NOTIFICATIONS)
        }

        AlertDialog.Builder(this)
            .setTitle("Quyền truy cập SMS")
            .setMessage("ScamShield yêu cầu quyền đọc tin nhắn để tự động phát hiện đường dẫn lừa đảo và số điện thoại giả mạo ngân hàng theo thời gian thực.\n\nThông tin nhạy cảm và mã xác thực ngân hàng sẽ được mã hóa cục bộ.")
            .setPositiveButton("Đồng ý") { _, _ ->
                ActivityCompat.requestPermissions(this, permissions.toTypedArray(), PERMISSION_REQUEST_CODE)
            }
            .setNegativeButton("Hủy") { d, _ -> d.dismiss() }
            .show()
    }

    override fun onRequestPermissionsResult(requestCode: Int, permissions: Array<out String>, grantResults: IntArray) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        if (requestCode == PERMISSION_REQUEST_CODE) {
            val allGranted = grantResults.isNotEmpty() && grantResults.all { it == PackageManager.PERMISSION_GRANTED }
            if (allGranted) {
                getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE).edit().putBoolean(KEY_PROTECTION_ENABLED, true).apply()
                Toast.makeText(this, "Đã kích hoạt bảo vệ thành công", Toast.LENGTH_SHORT).show()
            } else {
                Toast.makeText(this, "Ứng dụng chưa được cấp đủ quyền đọc SMS", Toast.LENGTH_LONG).show()
            }
            updateUIState()
        }
    }

    private fun testCustomMessage() {
        val input = etCustomSms.text.toString().trim()
        if (input.isEmpty()) {
            Toast.makeText(this, "Vui lòng nhập nội dung tin nhắn để kiểm tra", Toast.LENGTH_SHORT).show()
            return
        }

        val detector = SmsReceiver()
        val result = detector.evaluateScamRiskOnDevice("0383775033", input)

        cardAlertDetails.visibility = View.VISIBLE
        val accentColor = if (result.isScam) {
            if (result.alertLevel == "DANGEROUS") ContextCompat.getColor(this, R.color.status_danger)
            else ContextCompat.getColor(this, R.color.status_caution)
        } else {
            ContextCompat.getColor(this, R.color.status_safe)
        }
        viewAlertDetailsAccent.setBackgroundColor(accentColor)

        tvDetails.text = """
            KẾT QUẢ PHÂN TÍCH:
            • Người gửi: 0383775033
            • Đánh giá: ${result.statusLabel}
            • Mức độ rủi ro: ${result.riskPercent}%
            • Dấu hiệu phát hiện: ${result.reason}
            • Nội dung: "$input"
        """.trimIndent()

        if (result.isScam) {
            btnOpenCurrentSms.visibility = View.VISIBLE
            btnOpenCurrentSms.setOnClickListener {
                try {
                    val uri = Uri.parse("smsto:0383775033")
                    startActivity(Intent(Intent.ACTION_VIEW, uri))
                } catch (e: Exception) {
                    Toast.makeText(this, "Không thể mở ứng dụng tin nhắn", Toast.LENGTH_SHORT).show()
                }
            }

            btnReportCurrentAlert.visibility = View.VISIBLE
            btnReportCurrentAlert.setOnClickListener {
                val reportIntent = Intent(this, com.samsung.sic.scamshield.report.ReportActivity::class.java).apply {
                    putExtra("EXTRA_SENDER", "0383775033")
                    putExtra("EXTRA_RISK", result.riskPercent)
                    putExtra("EXTRA_BODY", input)
                    putExtra("EXTRA_REASON", result.reason)
                }
                startActivity(reportIntent)
            }

            lifecycleScope.launch(Dispatchers.IO) {
                try {
                    val alertDao = AlertDatabase.getDatabase(applicationContext).alertDao()
                    alertDao.insertAlert(
                        AlertRecord(
                            sender = "0383775033",
                            timestamp = System.currentTimeMillis(),
                            preview = if (input.length > 100) input.take(100) + "..." else input,
                            riskPercent = result.riskPercent,
                            alertLevel = result.alertLevel,
                            reason = result.reason
                        )
                    )
                } catch (e: Exception) {
                }
            }

            NotificationHelper.showScamAlertNotification(
                context = this,
                sender = "0383775033",
                alertLevel = result.alertLevel,
                statusLabel = result.statusLabel,
                riskPercent = result.riskPercent,
                reason = result.reason,
                fullMessage = input
            )
        } else {
            btnOpenCurrentSms.visibility = View.GONE
            btnReportCurrentAlert.visibility = View.GONE
            Toast.makeText(this, "Nội dung an toàn, không phát hiện dấu hiệu lừa đảo", Toast.LENGTH_LONG).show()
        }
    }

    private fun handleIntentData() {
        val sender = intent.getStringExtra("EXTRA_SENDER")
        val body = intent.getStringExtra("EXTRA_BODY")
        val risk = intent.getIntExtra("EXTRA_RISK", 0)
        val reason = intent.getStringExtra("EXTRA_REASON")

        if (!sender.isNullOrEmpty() && !body.isNullOrEmpty()) {
            cardAlertDetails.visibility = View.VISIBLE
            btnOpenCurrentSms.visibility = View.VISIBLE
            btnOpenCurrentSms.setOnClickListener {
                try {
                    val uri = Uri.parse("smsto:${Uri.encode(sender)}")
                    startActivity(Intent(Intent.ACTION_VIEW, uri))
                } catch (e: Exception) {
                    Toast.makeText(this, "Không thể mở ứng dụng tin nhắn", Toast.LENGTH_SHORT).show()
                }
            }
            btnReportCurrentAlert.visibility = View.VISIBLE
            btnReportCurrentAlert.setOnClickListener {
                val reportIntent = Intent(this, com.samsung.sic.scamshield.report.ReportActivity::class.java).apply {
                    putExtra("EXTRA_SENDER", sender)
                    putExtra("EXTRA_RISK", risk)
                    putExtra("EXTRA_BODY", body)
                    putExtra("EXTRA_REASON", reason ?: "")
                }
                startActivity(reportIntent)
            }
            viewAlertDetailsAccent.setBackgroundColor(ContextCompat.getColor(this, R.color.status_danger))
            tvDetails.text = """
                CHI TIẾT CẢNH BÁO:
                • Người gửi: $sender
                • Mức độ rủi ro: $risk%
                • Dấu hiệu: $reason
                • Nội dung: "$body"
                
                Khuyến cáo: Xóa tin nhắn và không truy cập liên kết đính kèm.
            """.trimIndent()
        }
    }
}
