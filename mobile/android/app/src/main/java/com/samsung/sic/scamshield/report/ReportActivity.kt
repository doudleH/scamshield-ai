package com.samsung.sic.scamshield.report

import android.os.Bundle
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.samsung.sic.scamshield.BackendApi
import com.samsung.sic.scamshield.databinding.ActivityReportBinding
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import org.json.JSONObject

class ReportActivity : AppCompatActivity() {

    private lateinit var binding: ActivityReportBinding

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityReportBinding.inflate(layoutInflater)
        setContentView(binding.root)

        setSupportActionBar(binding.toolbar)
        supportActionBar?.setDisplayHomeAsUpEnabled(true)
        binding.toolbar.setNavigationOnClickListener { finish() }

        val sender = intent.getStringExtra("EXTRA_SENDER") ?: "Không rõ"
        val risk = intent.getIntExtra("EXTRA_RISK", 90)
        val body = intent.getStringExtra("EXTRA_BODY") ?: ""
        val reason = intent.getStringExtra("EXTRA_REASON") ?: ""

        binding.tvReportSender.text = "Người gửi: $sender"
        binding.tvReportRisk.text = "Mức nguy hiểm: $risk%"
        binding.tvReportContent.text = "Nội dung: $body"

        binding.btnCancelReport.setOnClickListener {
            finish()
        }

        binding.btnSendReport.setOnClickListener {
            val userNote = binding.etReportNote.text.toString().trim()
            sendReportToBackend(sender, body, risk, reason, userNote)
        }
    }

    private fun sendReportToBackend(sender: String, message: String, risk: Int, reason: String, note: String) {
        binding.btnSendReport.isEnabled = false
        binding.btnSendReport.text = "⏳ ĐANG GỬI BÁO CÁO..."

        lifecycleScope.launch {
            val payload = JSONObject().apply {
                put("sender", sender)
                put("message", message)
                put("risk_percent", risk)
                put("reason", if (note.isNotEmpty()) "$reason (Ghi chú: $note)" else reason)
            }

            val response = withContext(Dispatchers.IO) {
                BackendApi.post("/api/v1/report", payload.toString())
            }

            if (response?.code == 200) {
                Toast.makeText(
                    this@ReportActivity,
                    "✅ Đã gửi báo cáo thành công! Cảm ơn bạn đã đóng góp bảo vệ cộng đồng.",
                    Toast.LENGTH_LONG
                ).show()
                finish()
            } else {
                // Không báo thành công giả khi máy chủ ngoại tuyến
                binding.btnSendReport.isEnabled = true
                binding.btnSendReport.text = "GỬI BÁO CÁO LÊN HỆ THỐNG"
                Toast.makeText(
                    this@ReportActivity,
                    "❌ Không gửi được báo cáo. Kiểm tra kết nối mạng rồi thử lại.",
                    Toast.LENGTH_LONG
                ).show()
            }
        }
    }
}
