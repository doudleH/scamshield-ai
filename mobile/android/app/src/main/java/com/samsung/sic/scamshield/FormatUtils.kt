package com.samsung.sic.scamshield

object FormatUtils {
    /**
     * Định dạng số lượng hiển thị trên toàn bộ giao diện:
     * Dưới 100: hiển thị bình thường (0, 1, ..., 98, 99)
     * Từ 100 trở đi: hiển thị "99+" để chống vỡ khung giao diện.
     */
    fun formatBadgeCount(count: Int): String {
        return if (count >= 100) "99+" else count.toString()
    }

    fun formatBadgeCount(count: Long): String {
        return if (count >= 100L) "99+" else count.toString()
    }
}
