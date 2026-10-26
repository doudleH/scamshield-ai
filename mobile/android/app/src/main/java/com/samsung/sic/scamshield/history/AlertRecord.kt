package com.samsung.sic.scamshield.history

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "alert_history")
data class AlertRecord(
    @PrimaryKey(autoGenerate = true)
    val id: Int = 0,
    val sender: String,
    val timestamp: Long,
    val preview: String,
    val riskPercent: Int,
    val alertLevel: String,
    val reason: String,
    val isReported: Boolean = false
)
