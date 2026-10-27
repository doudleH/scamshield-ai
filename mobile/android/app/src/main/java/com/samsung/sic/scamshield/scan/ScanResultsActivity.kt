package com.samsung.sic.scamshield.scan

import android.content.Intent
import android.content.pm.PackageManager
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.ContextCompat
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.samsung.sic.scamshield.R
import com.samsung.sic.scamshield.databinding.ActivityScanResultsBinding
import com.samsung.sic.scamshield.report.ReportActivity
import android.net.Uri
import androidx.activity.result.contract.ActivityResultContracts
import com.samsung.sic.scamshield.history.AlertDatabase
import com.samsung.sic.scamshield.history.AlertRecord
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import java.text.SimpleDateFormat
import java.util.*

class ScanResultsActivity : AppCompatActivity() {

    private lateinit var binding: ActivityScanResultsBinding
    private val allResults = mutableListOf<SmsInboxScanner.InboxScanResult>()

    private val requestSmsPermissionLauncher =
        registerForActivityResult(ActivityResultContracts.RequestPermission()) { isGranted ->
            if (isGranted) {
                startScanning()
            } else {
                Toast.makeText(this, "Cần cấp quyền đọc tin nhắn để quét hộp thư", Toast.LENGTH_LONG).show()
                finish()
            }
        }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityScanResultsBinding.inflate(layoutInflater)
        setContentView(binding.root)

        setSupportActionBar(binding.toolbar)
        supportActionBar?.setDisplayHomeAsUpEnabled(true)
        binding.toolbar.setNavigationOnClickListener { finish() }

        if (ContextCompat.checkSelfPermission(this, android.Manifest.permission.READ_SMS)
            == PackageManager.PERMISSION_GRANTED) {
            startScanning()
        } else {
            requestSmsPermissionLauncher.launch(android.Manifest.permission.READ_SMS)
        }
    }

    private fun startScanning() {
        val scanner = SmsInboxScanner(this)
        binding.cardProgress.visibility = View.VISIBLE
        binding.rvScanResults.visibility = View.GONE
        binding.layoutFilters.visibility = View.GONE
        binding.layoutEmptyState.visibility = View.GONE

        CoroutineScope(Dispatchers.IO).launch {
            scanner.scanInbox(
                onProgress = { current, total ->
                    CoroutineScope(Dispatchers.Main).launch {
                        val percent = if (total > 0) (current * 100f / total).toInt() else 0
                        binding.progressBar.progress = percent
                        binding.tvScanProgress.text = "Đang quét $current/$total tin nhắn..."
                    }
                },
                onComplete = { results ->
                    CoroutineScope(Dispatchers.Main).launch {
                        binding.cardProgress.visibility = View.GONE

                        if (results.isEmpty()) {
                            binding.layoutEmptyState.visibility = View.VISIBLE
                        } else {
                            allResults.clear()
                            allResults.addAll(results)

                            val scamList = results.filter { it.isScam }
                            val safeList = results.filter { !it.isScam }

                            CoroutineScope(Dispatchers.IO).launch {
                                try {
                                    val dao = AlertDatabase.getDatabase(applicationContext).alertDao()
                                    for (item in scamList) {
                                        if (dao.countBySenderAndTimestamp(item.sender, item.date) == 0) {
                                            dao.insertAlert(
                                                AlertRecord(
                                                    sender = item.sender,
                                                    timestamp = item.date,
                                                    preview = item.preview,
                                                    riskPercent = item.riskPercent,
                                                    alertLevel = item.alertLevel,
                                                    reason = item.reason
                                                )
                                            )
                                        }
                                    }
                                } catch (e: Exception) {
                                }
                            }

                            val allCountStr = com.samsung.sic.scamshield.FormatUtils.formatBadgeCount(results.size)
                            val scamCountStr = com.samsung.sic.scamshield.FormatUtils.formatBadgeCount(scamList.size)
                            val safeCountStr = com.samsung.sic.scamshield.FormatUtils.formatBadgeCount(safeList.size)

                            binding.tvResultHeader.visibility = View.VISIBLE
                            binding.tvResultHeader.text =
                                "Đã quét $allCountStr tin nhắn: 🚨 $scamCountStr nguy hiểm | 🟢 $safeCountStr an toàn"
                            binding.layoutFilters.visibility = View.VISIBLE
                            binding.btnFilterAll.text = "Tất cả ($allCountStr)"
                            binding.btnFilterScam.text = "🚨 Lừa đảo ($scamCountStr)"
                            binding.btnFilterSafe.text = "🟢 An toàn ($safeCountStr)"

                            val setAdapterForList: (List<SmsInboxScanner.InboxScanResult>) -> Unit = { list ->
                                binding.rvScanResults.adapter = ScanResultAdapter(list) { item ->
                                    val intent = Intent(this@ScanResultsActivity, ReportActivity::class.java).apply {
                                        putExtra("EXTRA_SENDER", item.sender)
                                        putExtra("EXTRA_RISK", item.riskPercent)
                                        putExtra("EXTRA_BODY", item.fullBody)
                                        putExtra("EXTRA_REASON", item.reason)
                                    }
                                    startActivity(intent)
                                }
                            }

                            binding.rvScanResults.visibility = View.VISIBLE
                            binding.rvScanResults.layoutManager = LinearLayoutManager(this@ScanResultsActivity)
                            updateFilterStyle(0)
                            setAdapterForList(allResults)

                            binding.btnFilterAll.setOnClickListener {
                                updateFilterStyle(0)
                                setAdapterForList(allResults)
                            }
                            binding.btnFilterScam.setOnClickListener {
                                updateFilterStyle(1)
                                setAdapterForList(scamList)
                            }
                            binding.btnFilterSafe.setOnClickListener {
                                updateFilterStyle(2)
                                setAdapterForList(safeList)
                            }
                        }
                    }
                }
            )
        }
    }

    private fun updateFilterStyle(selected: Int) {
        val primaryColor = ContextCompat.getColor(this, R.color.brand_primary)
        val dangerColor = ContextCompat.getColor(this, R.color.status_danger)
        val safeColor = ContextCompat.getColor(this, R.color.status_safe)
        val textColorMuted = ContextCompat.getColor(this, R.color.text_secondary)
        val transparent = 0x00000000

        if (selected == 0) {
            binding.btnFilterAll.backgroundTintList = android.content.res.ColorStateList.valueOf(primaryColor)
            binding.btnFilterAll.setTextColor(0xFFFFFFFF.toInt())
            binding.btnFilterAll.strokeWidth = 0
        } else {
            binding.btnFilterAll.backgroundTintList = android.content.res.ColorStateList.valueOf(transparent)
            binding.btnFilterAll.setTextColor(textColorMuted)
            binding.btnFilterAll.strokeColor = android.content.res.ColorStateList.valueOf(ContextCompat.getColor(this, R.color.border_subtle))
            binding.btnFilterAll.strokeWidth = 2
        }

        if (selected == 1) {
            binding.btnFilterScam.backgroundTintList = android.content.res.ColorStateList.valueOf(dangerColor)
            binding.btnFilterScam.setTextColor(0xFFFFFFFF.toInt())
            binding.btnFilterScam.strokeWidth = 0
        } else {
            binding.btnFilterScam.backgroundTintList = android.content.res.ColorStateList.valueOf(transparent)
            binding.btnFilterScam.setTextColor(dangerColor)
            binding.btnFilterScam.strokeColor = android.content.res.ColorStateList.valueOf(dangerColor)
            binding.btnFilterScam.strokeWidth = 2
        }

        if (selected == 2) {
            binding.btnFilterSafe.backgroundTintList = android.content.res.ColorStateList.valueOf(safeColor)
            binding.btnFilterSafe.setTextColor(0xFFFFFFFF.toInt())
            binding.btnFilterSafe.strokeWidth = 0
        } else {
            binding.btnFilterSafe.backgroundTintList = android.content.res.ColorStateList.valueOf(transparent)
            binding.btnFilterSafe.setTextColor(safeColor)
            binding.btnFilterSafe.strokeColor = android.content.res.ColorStateList.valueOf(safeColor)
            binding.btnFilterSafe.strokeWidth = 2
        }
    }
}

class ScanResultAdapter(
    private val items: List<SmsInboxScanner.InboxScanResult>,
    private val onReportClick: (SmsInboxScanner.InboxScanResult) -> Unit = {}
) : RecyclerView.Adapter<ScanResultAdapter.ViewHolder>() {

    inner class ViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        val tvSender: TextView = itemView.findViewById(R.id.tvSender)
        val tvTimestamp: TextView = itemView.findViewById(R.id.tvTimestamp)
        val tvPreview: TextView = itemView.findViewById(R.id.tvPreview)
        val tvReason: TextView = itemView.findViewById(R.id.tvReason)
        val tvRiskBadge: TextView = itemView.findViewById(R.id.tvRiskBadge)
        val viewAccentBar: View = itemView.findViewById(R.id.viewAccentBar)
        val btnReport: View = itemView.findViewById(R.id.btnReport)
        val btnOpenSms: View = itemView.findViewById(R.id.btnOpenSms)
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_scan_result, parent, false)
        return ViewHolder(view)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        val item = items[position]
        val sdf = SimpleDateFormat("dd/MM/yyyy HH:mm", Locale.getDefault())

        holder.tvSender.text = item.sender
        holder.tvTimestamp.text = sdf.format(Date(item.date))
        holder.tvPreview.text = item.preview

        val openSms = {
            try {
                val uri = Uri.parse("smsto:${Uri.encode(item.sender)}")
                val intent = Intent(Intent.ACTION_VIEW, uri)
                intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
                holder.itemView.context.startActivity(intent)
            } catch (e: Exception) {
                Toast.makeText(holder.itemView.context, "Không thể mở ứng dụng tin nhắn", Toast.LENGTH_SHORT).show()
            }
        }

        holder.btnOpenSms.setOnClickListener { openSms() }
        holder.itemView.setOnClickListener { openSms() }

        if (item.isScam) {
            val dangerColor = if (item.alertLevel == "DANGEROUS") 0xFFef4444.toInt() else 0xFFf59e0b.toInt()
            val dangerBg = if (item.alertLevel == "DANGEROUS") 0xCCcc0000.toInt() else 0xCCcc7700.toInt()
            holder.viewAccentBar.setBackgroundColor(dangerColor)
            holder.tvRiskBadge.setBackgroundColor(dangerBg)
            holder.tvRiskBadge.text = "🚨 ${item.riskPercent}%"
            holder.tvReason.setTextColor(dangerColor)
            holder.tvReason.text = "🔍 ${item.reason}"
            holder.btnReport.visibility = View.VISIBLE
            holder.btnReport.setOnClickListener {
                onReportClick(item)
            }
        } else {
            val safeColor = 0xFF10b981.toInt()
            val safeBg = 0xCC059669.toInt()
            holder.viewAccentBar.setBackgroundColor(safeColor)
            holder.tvRiskBadge.setBackgroundColor(safeBg)
            holder.tvRiskBadge.text = "🟢 AN TOÀN"
            holder.tvReason.setTextColor(safeColor)
            holder.tvReason.text = "✅ ${item.reason}"
            holder.btnReport.visibility = View.GONE
        }
    }

    override fun getItemCount() = items.size
}
