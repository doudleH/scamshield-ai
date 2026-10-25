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
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat

/**
 * MainActivity: Giao diện chính của ứng dụng di động ScamShield AI.
 * - Quản lý công tắc BẬT / TẮT lá chắn bảo vệ SMS linh hoạt.
 * - Mở cài đặt quyền ứng dụng trong hệ thống Android khi người dùng muốn thu hồi quyền.
 * - Hộp thử nghiệm tin nhắn trực tiếp (Sandbox Tester) giúp kiểm tra AI trên mọi loại nội dung
 *   mà không lo bị bộ lọc nhà mạng viễn thông chặn.
 * - Nút giả lập demo nhanh phục vụ thuyết trình đồ án trước hội đồng.
 */
class MainActivity : AppCompatActivity() {

    companion object {
        private const val PERMISSION_REQUEST_CODE = 2026
        private const val PREFS_NAME = "scamshield_prefs"
        private const val KEY_PROTECTION_ENABLED = "is_protection_enabled"
    }

    private lateinit var tvStatus: TextView
    private lateinit var tvDetails: TextView
    private lateinit var btnToggleProtection: Button
    private lateinit var btnOpenSettings: Button
    private lateinit var etCustomSms: EditText
    private lateinit var btnTestCustomSms: Button
    private lateinit var btnSimulate: Button

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        tvStatus = findViewById(R.id.tvProtectionStatus)
        tvDetails = findViewById(R.id.tvAlertDetails)
        btnToggleProtection = findViewById(R.id.btnToggleProtection)
        btnOpenSettings = findViewById(R.id.btnOpenSettings)
        etCustomSms = findViewById(R.id.etCustomSms)
        btnTestCustomSms = findViewById(R.id.btnTestCustomSms)
        btnSimulate = findViewById(R.id.btnSimulateScam)

        // Khởi tạo kênh thông báo
        NotificationHelper.createNotificationChannel(this)

        // Cập nhật giao diện trạng thái ban đầu
        updateUIState()

        // 1. Nút Bật / Tắt hoặc Cấp quyền
        btnToggleProtection.setOnClickListener {
            if (!hasSmsPermissions()) {
                requestSmsPermissions()
            } else {
                toggleProtectionState()
            }
        }

        // 2. Nút Mở cài đặt quyền hệ thống Android
        btnOpenSettings.setOnClickListener {
            openAppSettings()
        }

        // 3. Hộp Thử Nghiệm Tin Nhắn Trực Tiếp (Sandbox Tester)
        btnTestCustomSms.setOnClickListener {
            testCustomMessage()
        }

        // 4. Nút Giả lập demo nhanh mẫu Vietcombank
        btnSimulate.setOnClickListener {
            simulateIncomingScamMessage()
        }

        // Xử lý dữ liệu nếu người dùng mở app từ thông báo đẩy
        handleIntentData()
    }

    override fun onResume() {
        super.onResume()
        updateUIState()
    }

    /**
     * Kiểm tra xem các quyền SMS cốt lõi đã được cấp chưa
     */
    private fun hasSmsPermissions(): Boolean {
        val hasReceive = ContextCompat.checkSelfPermission(this, Manifest.permission.RECEIVE_SMS) == PackageManager.PERMISSION_GRANTED
        val hasRead = ContextCompat.checkSelfPermission(this, Manifest.permission.READ_SMS) == PackageManager.PERMISSION_GRANTED
        return hasReceive && hasRead
    }

    /**
     * Đồng bộ trạng thái hiển thị của nút bấm và nhãn bảo vệ
     */
    private fun updateUIState() {
        val prefs = getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
        val isEnabled = prefs.getBoolean(KEY_PROTECTION_ENABLED, true)

        if (!hasSmsPermissions()) {
            tvStatus.text = "🔴 THIẾU QUYỀN ĐỌC TIN NHẮN"
            tvStatus.setTextColor(Color.parseColor("#ef4444"))
            btnToggleProtection.text = "🔑 CẤP QUYỀN ĐỌC TIN NHẮN SMS"
            btnToggleProtection.setBackgroundColor(Color.parseColor("#2563eb"))
        } else {
            if (isEnabled) {
                tvStatus.text = "🟢 LÁ CHẮN ĐANG BẬT (BẢO VỆ 24/7)"
                tvStatus.setTextColor(Color.parseColor("#10b981"))
                btnToggleProtection.text = "⏸️ TẠM DỪNG LÁ CHẮN BẢO VỆ"
                btnToggleProtection.setBackgroundColor(Color.parseColor("#f59e0b"))
            } else {
                tvStatus.text = "🟡 LÁ CHẮN ĐÃ TẮT (TẠM DỪNG)"
                tvStatus.setTextColor(Color.parseColor("#f59e0b"))
                btnToggleProtection.text = "▶️ KÍCH HOẠT LÁ CHẮN BẢO VỆ"
                btnToggleProtection.setBackgroundColor(Color.parseColor("#10b981"))
            }
        }
    }

    /**
     * Đổi trạng thái Bật <-> Tắt bảo vệ
     */
    private fun toggleProtectionState() {
        val prefs = getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
        val currentState = prefs.getBoolean(KEY_PROTECTION_ENABLED, true)
        val newState = !currentState

        prefs.edit().putBoolean(KEY_PROTECTION_ENABLED, newState).apply()
        updateUIState()

        if (newState) {
            Toast.makeText(this, "✅ Đã kích hoạt lá chắn bảo vệ tin nhắn 24/7!", Toast.LENGTH_SHORT).show()
        } else {
            Toast.makeText(this, "⏸️ Đã tạm dừng bảo vệ. App sẽ không quét tin nhắn đến.", Toast.LENGTH_SHORT).show()
        }
    }

    /**
     * Mở trang Cài đặt ứng dụng của Android để người dùng xem hoặc thu hồi quyền
     */
    private fun openAppSettings() {
        val intent = Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS).apply {
            data = Uri.fromParts("package", packageName, null)
        }
        startActivity(intent)
        Toast.makeText(this, "Bạn có thể xem hoặc thay đổi quyền SMS trong mục này", Toast.LENGTH_LONG).show()
    }

    /**
     * Yêu cầu cấp quyền đọc tin nhắn SMS
     */
    private fun requestSmsPermissions() {
        val permissions = mutableListOf(Manifest.permission.RECEIVE_SMS, Manifest.permission.READ_SMS)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            permissions.add(Manifest.permission.POST_NOTIFICATIONS)
        }

        AlertDialog.Builder(this)
            .setTitle("🛡️ Cấp Quyền Bảo Vệ SMS")
            .setMessage("ScamShield AI cần quyền đọc tin nhắn để tự động phát hiện mã độc, đường link giả mạo ngân hàng ngay khi tin nhắn vừa gửi đến.\n\nCam kết: Hệ thống ẩn danh hóa mã OTP tại chỗ, tuyệt đối không lưu trữ thông tin cá nhân của bạn!")
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
                Toast.makeText(this, "✅ Đã cấp quyền và kích hoạt bảo vệ thành công!", Toast.LENGTH_SHORT).show()
            } else {
                Toast.makeText(this, "⚠️ Bạn chưa cấp đủ quyền đọc SMS cho ứng dụng.", Toast.LENGTH_LONG).show()
            }
            updateUIState()
        }
    }

    /**
     * Thử nghiệm quét bất kỳ nội dung tin nhắn nào người dùng nhập vào
     */
    private fun testCustomMessage() {
        val input = etCustomSms.text.toString().trim()
        if (input.isEmpty()) {
            Toast.makeText(this, "Vui lòng nhập nội dung tin nhắn để thử nghiệm!", Toast.LENGTH_SHORT).show()
            return
        }

        Toast.makeText(this, "Đang phân tích tin nhắn bằng AI...", Toast.LENGTH_SHORT).show()

        // Gọi trực tiếp bộ phân tích AI Cục bộ
        val detector = SmsReceiver()
        val result = detector.evaluateScamRiskOnDevice("0383775033", input)

        tvDetails.text = """
            📊 KẾT QUẢ QUÉT THỬ NGHIỆM:
            • Người gửi: 0383775033 (SIM Thử Nghiệm)
            • Đánh giá AI: ${result.statusLabel}
            • Mức độ nguy hiểm: ${result.riskPercent}%
            • Dấu hiệu phát hiện: ${result.reason}
            • Nội dung: "$input"
        """.trimIndent()

        if (result.isScam) {
            NotificationHelper.showScamAlertNotification(
                context = this,
                sender = "0383775033 (Thử Nghiệm)",
                alertLevel = result.alertLevel,
                statusLabel = result.statusLabel,
                riskPercent = result.riskPercent,
                reason = result.reason,
                fullMessage = input
            )
        } else {
            Toast.makeText(this, "✅ Tin nhắn được đánh giá an toàn, không có dấu hiệu lừa đảo.", Toast.LENGTH_LONG).show()
        }
    }

    /**
     * Giả lập tin nhắn lừa đảo mẫu Vietcombank
     */
    private fun simulateIncomingScamMessage() {
        Toast.makeText(this, "⚡ Đang bắn thông báo giả lập nhận SMS lừa đảo...", Toast.LENGTH_SHORT).show()

        val sampleSender = "Vietcombank-Fake"
        val sampleBody = "Thong bao: Tai khoan VCB Digibank cua quy khach bi khoa do dang nhap bat thuong. Vui long truy cap http://vcb-digibank-login.xyz/verify de xac minh trong 24h."

        NotificationHelper.showScamAlertNotification(
            context = this,
            sender = sampleSender,
            alertLevel = "DANGEROUS",
            statusLabel = "CẢNH BÁO LỪA ĐẢO NGUY CƠ CAO",
            riskPercent = 96,
            reason = "Chứa liên kết mạo danh tên miền ngân hàng (.xyz) và từ khóa đe dọa trong 24h",
            fullMessage = sampleBody
        )
    }

    private fun handleIntentData() {
        val sender = intent.getStringExtra("EXTRA_SENDER")
        val body = intent.getStringExtra("EXTRA_BODY")
        val risk = intent.getIntExtra("EXTRA_RISK", 0)
        val reason = intent.getStringExtra("EXTRA_REASON")

        if (!sender.isNullOrEmpty() && !body.isNullOrEmpty()) {
            tvDetails.text = """
                🚨 CHI TIẾT CẢNH BÁO VỪA PHÁT HIỆN:
                • Người gửi: $sender
                • Độ nguy hiểm: $risk%
                • Dấu hiệu: $reason
                • Nội dung: "$body"
                
                👉 Khuyến nghị: Xóa ngay tin nhắn và KHÔNG truy cập liên kết!
            """.trimIndent()
        }
    }
}
