package com.samsung.sic.scamshield.history

import androidx.lifecycle.LiveData
import androidx.room.*

@Dao
interface AlertDao {

    @Query("SELECT * FROM alert_history ORDER BY timestamp DESC LIMIT 100")
    fun getRecentAlerts(): LiveData<List<AlertRecord>>

    @Query("SELECT * FROM alert_history WHERE alertLevel = 'DANGEROUS' ORDER BY timestamp DESC")
    fun getDangerousAlerts(): LiveData<List<AlertRecord>>

    @Query("SELECT COUNT(*) FROM alert_history")
    fun getTotalCount(): LiveData<Int>

    @Query("SELECT COUNT(*) FROM alert_history WHERE timestamp > :cutoffTime")
    suspend fun getRecentCount(cutoffTime: Long): Int

    @Query("SELECT COUNT(*) FROM alert_history WHERE sender = :sender AND timestamp = :timestamp")
    suspend fun countBySenderAndTimestamp(sender: String, timestamp: Long): Int

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertAlert(record: AlertRecord)

    @Delete
    suspend fun deleteAlert(record: AlertRecord)

    @Query("DELETE FROM alert_history WHERE timestamp < :cutoffTime")
    suspend fun deleteOldAlerts(cutoffTime: Long)

    @Query("UPDATE alert_history SET isReported = 1 WHERE id = :id")
    suspend fun markAsReported(id: Int)
}
