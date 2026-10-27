package com.samsung.sic.scamshield.history

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.Observer
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.samsung.sic.scamshield.R
import com.samsung.sic.scamshield.databinding.ActivityAlertHistoryBinding
import java.text.SimpleDateFormat
import java.util.*

class AlertHistoryActivity : AppCompatActivity() {

    private lateinit var binding: ActivityAlertHistoryBinding

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityAlertHistoryBinding.inflate(layoutInflater)
        setContentView(binding.root)

        setSupportActionBar(binding.toolbar)
        supportActionBar?.setDisplayHomeAsUpEnabled(true)
        binding.toolbar.setNavigationOnClickListener { finish() }

        val db = AlertDatabase.getDatabase(this)
        val dao = db.alertDao()

        dao.getTotalCount().observe(this, Observer { count ->
            binding.tvTotalCount.text = com.samsung.sic.scamshield.FormatUtils.formatBadgeCount(count ?: 0)
        })

        dao.getRecentAlerts().observe(this, Observer { alerts ->
            if (alerts.isNullOrEmpty()) {
                binding.rvAlertHistory.visibility = View.GONE
                binding.layoutEmpty.visibility = View.VISIBLE
                binding.tvDangerCount.text = "0"
            } else {
                val dangerCount = alerts.count { it.alertLevel == "DANGEROUS" }
                binding.tvDangerCount.text = com.samsung.sic.scamshield.FormatUtils.formatBadgeCount(dangerCount)
                binding.rvAlertHistory.visibility = View.VISIBLE
                binding.layoutEmpty.visibility = View.GONE
                binding.rvAlertHistory.layoutManager = LinearLayoutManager(this)
                binding.rvAlertHistory.adapter = AlertHistoryAdapter(alerts) { item ->
                    val intent = android.content.Intent(this, com.samsung.sic.scamshield.report.ReportActivity::class.java).apply {
                        putExtra("EXTRA_SENDER", item.sender)
                        putExtra("EXTRA_RISK", item.riskPercent)
                        putExtra("EXTRA_BODY", item.preview)
                        putExtra("EXTRA_REASON", item.reason)
                    }
                    startActivity(intent)
                }
            }
        })
    }
}

class AlertHistoryAdapter(
    private val items: List<AlertRecord>,
    private val onReportClick: (AlertRecord) -> Unit = {}
) : RecyclerView.Adapter<AlertHistoryAdapter.ViewHolder>() {

    inner class ViewHolder(view: View) : RecyclerView.ViewHolder(view) {
        val tvSender: TextView = view.findViewById(R.id.tvHistorySender)
        val tvTime: TextView = view.findViewById(R.id.tvHistoryTime)
        val tvPreview: TextView = view.findViewById(R.id.tvHistoryPreview)
        val tvReason: TextView = view.findViewById(R.id.tvHistoryReason)
        val tvLevel: TextView = view.findViewById(R.id.tvHistoryLevel)
        val viewBar: View = view.findViewById(R.id.viewHistoryBar)
        val btnReport: View = view.findViewById(R.id.btnHistoryReport)
        val btnOpenSms: View = view.findViewById(R.id.btnHistoryOpenSms)
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int) =
        ViewHolder(LayoutInflater.from(parent.context)
            .inflate(R.layout.item_alert_history, parent, false))

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        val item = items[position]
        val sdf = SimpleDateFormat("dd/MM HH:mm", Locale.getDefault())

        holder.tvSender.text = item.sender
        holder.tvTime.text = sdf.format(Date(item.timestamp))
        holder.tvPreview.text = item.preview
        holder.tvReason.text = if (item.reason.isNotEmpty()) "Dấu hiệu: ${item.reason}" else ""
        holder.tvLevel.text = if (item.alertLevel == "DANGEROUS") "🚨 NGUY HIỂM (${item.riskPercent}%)" else "⚠️ ĐÁNG NGỜ (${item.riskPercent}%)"

        val color = if (item.alertLevel == "DANGEROUS") 0xFFef4444.toInt() else 0xFFf59e0b.toInt()
        holder.viewBar.setBackgroundColor(color)
        holder.tvLevel.setTextColor(color)

        val openSms = {
            try {
                val uri = android.net.Uri.parse("smsto:${android.net.Uri.encode(item.sender)}")
                val smsIntent = android.content.Intent(android.content.Intent.ACTION_VIEW, uri)
                smsIntent.addFlags(android.content.Intent.FLAG_ACTIVITY_NEW_TASK)
                holder.itemView.context.startActivity(smsIntent)
            } catch (e: Exception) {
                android.widget.Toast.makeText(holder.itemView.context, "Không thể mở ứng dụng tin nhắn", android.widget.Toast.LENGTH_SHORT).show()
            }
        }
        holder.btnOpenSms.setOnClickListener { openSms() }
        holder.itemView.setOnClickListener { openSms() }

        val reportBtn = holder.btnReport as? com.google.android.material.button.MaterialButton
        if (item.isReported) {
            reportBtn?.text = "✅ Đã báo cáo"
            reportBtn?.isEnabled = false
        } else {
            reportBtn?.text = "🚩 Báo cáo"
            reportBtn?.isEnabled = true
            reportBtn?.setOnClickListener {
                onReportClick(item)
            }
        }
    }

    override fun getItemCount() = items.size
}
