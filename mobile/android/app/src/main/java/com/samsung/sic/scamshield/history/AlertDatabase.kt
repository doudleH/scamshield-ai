package com.samsung.sic.scamshield.history

import android.content.Context
import androidx.room.Database
import androidx.room.Room
import androidx.room.RoomDatabase

@Database(
    entities = [AlertRecord::class],
    version = 1,
    exportSchema = false
)
abstract class AlertDatabase : RoomDatabase() {

    abstract fun alertDao(): AlertDao

    companion object {
        @Volatile
        private var INSTANCE: AlertDatabase? = null

        fun getDatabase(context: Context): AlertDatabase {
            return INSTANCE ?: synchronized(this) {
                Room.databaseBuilder(
                    context.applicationContext,
                    AlertDatabase::class.java,
                    "scamshield_alerts.db"
                )
                    .fallbackToDestructiveMigration()
                    .build()
                    .also { INSTANCE = it }
            }
        }
    }
}

