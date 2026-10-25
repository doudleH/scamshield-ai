package com.samsung.sic.scamshield

import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import android.graphics.Color
import android.media.RingtoneManager
import android.os.Build
import androidx.core.app.NotificationCompat

/**
 * Quản lý kênh thông báo đẩy và hiển thị cảnh báo lừa đảo khẩn cấp lên màn hình điện thoại.
 */
object NotificationHelper {

    private const val CHANNEL_ID = "scamshield_alert_channel"
    private const val CHANNEL_NAME = "Cảnh Báo Lừa Đảo ScamShield AI"
    private const val NOTIFICATION_ID = 1001

    /**
     * Khởi tạo kênh thông báo ưu tiên cao (Heads-up Notification)
     */
    fun createNotificationChannel(context: Context) {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val importance = NotificationManager.IMPORTANCE_HIGH
            val channel = NotificationChannel(CHANNEL_ID, CHANNEL_NAME, importance).apply {
                description = "Kênh thông báo cảnh báo nguy cơ lừa đảo SMS và Phishing thời gian thực"
                enableLights(true)
                lightColor = Color.RED
                enableVibration(true)
                vibrationPattern = longArrayOf(0, 500, 200, 500)
            }

            val notificationManager: NotificationManager =
                context.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
            notificationManager.createNotificationChannel(channel)
        }
    }

    /**
     * Hiển thị thông báo đẩy khẩn cấp lên màn hình khóa và thanh trạng thái
     */
    fun showScamAlertNotification(
        context: Context,
        sender: String,
        alertLevel: String,
        statusLabel: String,
        riskPercent: Int,
        reason: String,
        fullMessage: String
    ) {
        createNotificationChannel(context)

        // Chạm vào thông báo sẽ mở ứng dụng MainActivity để xem chi tiết
        val intent = Intent(context, MainActivity::class.java).apply {
            flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
            putExtra("EXTRA_SENDER", sender)
            putExtra("EXTRA_BODY", fullMessage)
            putExtra("EXTRA_RISK", riskPercent)
            putExtra("EXTRA_REASON", reason)
            putExtra("EXTRA_LEVEL", alertLevel)
        }

        val pendingIntent = PendingIntent.getActivity(
            context,
            0,
            intent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )

        val soundUri = RingtoneManager.getDefaultUri(RingtoneManager.TYPE_NOTIFICATION)

        val title = if (alertLevel == "DANGEROUS") {
            "🚨 CẢNH BÁO LỪA ĐẢO TỪ: $sender"
        } else {
            "⚠️ TIN NHẮN ĐÁNG NGỜ TỪ: $sender"
        }

        val content = "Phát hiện $riskPercent% rủi ro: $reason. TUYỆT ĐỐI KHÔNG BẤM LINK HOẶC CUNG CẤP OTP!"

        val notification = NotificationCompat.Builder(context, CHANNEL_ID)
            .setSmallIcon(android.R.drawable.stat_sys_warning)
            .setContentTitle(title)
            .setContentText(content)
            .setStyle(NotificationCompat.BigTextStyle().bigText(
                "Nội dung tin nhắn:\n\"$fullMessage\"\n\nĐánh giá AI: $statusLabel ($riskPercent% rủi ro)\nLý do: $reason\n\nKhuyến cáo: Xóa tin nhắn ngay hoặc gọi 156 để phản ánh."
            ))
            .setPriority(NotificationCompat.PRIORITY_MAX)
            .setCategory(NotificationCompat.CATEGORY_ALARM)
            .setColor(if (alertLevel == "DANGEROUS") Color.RED else Color.YELLOW)
            .setSound(soundUri)
            .setAutoCancel(true)
            .setContentIntent(pendingIntent)
            .build()

        val notificationManager =
            context.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
        notificationManager.notify(NOTIFICATION_ID, notification)
    }
}
