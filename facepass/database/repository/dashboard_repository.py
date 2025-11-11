from typing import List, Dict, Any
from facepass.database.setup_database.executor_query import QueryExecutor


class DashboardRepository:
    """Repository para queries relacionadas ao dashboard de gestão"""

    def __init__(self, connection):
        self.connection = connection
        self.executor = QueryExecutor(connection)

    def get_today_accesses_count(self) -> int:
        query = """
            SELECT COUNT(*) as count
            FROM accessRegisters
            WHERE DATE(created_at) = CURDATE()
        """
        result = self.executor.execute_query_one(query)
        return result['count'] if result else 0

    def get_today_allowed_count(self) -> int:
        query = """
            SELECT COUNT(*) as count
            FROM accessRegisters
            WHERE DATE(created_at) = CURDATE()
            AND access_allowed = TRUE
        """
        result = self.executor.execute_query_one(query)
        return result['count'] if result else 0

    def get_today_denied_count(self) -> int:
        query = """
            SELECT COUNT(*) as count
            FROM accessRegisters
            WHERE DATE(created_at) = CURDATE()
            AND access_allowed = FALSE
        """
        result = self.executor.execute_query_one(query)
        return result['count'] if result else 0

    def get_unread_notifications_count(self) -> int:
        query = """
            SELECT COUNT(*) as count
            FROM notifications
            WHERE is_read = FALSE
        """
        result = self.executor.execute_query_one(query)
        return result['count'] if result else 0

    def get_all_users_attendance(self, date: str = "") -> List[Dict[str, Any]]:
        if not date:
            date_condition = "DATE(created_at) = CURDATE()"
        else:
            date_condition = f"DATE(created_at) = '{date}'"

        query = f"""
            SELECT
                u.id,
                u.name,
                u.position,
                u.email,
                COALESCE(attendance.last_entry, NULL) as last_entry_time,
                COALESCE(attendance.last_exit, NULL) as last_exit_time,
                COALESCE(attendance.total_accesses, 0) as access_count,
                CASE
                    WHEN attendance.last_entry IS NOT NULL AND
                         (attendance.last_exit IS NULL OR attendance.last_entry > attendance.last_exit)
                    THEN 'Presente'
                    WHEN attendance.last_entry IS NULL
                    THEN 'Ausente'
                    ELSE 'Saiu'
                END as status
            FROM users u
            LEFT JOIN (
                SELECT
                    user_id,
                    MAX(CASE WHEN type_access = 'entrada' AND access_allowed = TRUE
                        THEN created_at END) as last_entry,
                    MAX(CASE WHEN type_access = 'saida' AND access_allowed = TRUE
                        THEN created_at END) as last_exit,
                    COUNT(*) as total_accesses
                FROM accessRegisters
                WHERE {date_condition}
                GROUP BY user_id
            ) attendance ON u.id = attendance.user_id
            WHERE u.approved = TRUE
            ORDER BY
                CASE
                    WHEN status = 'Presente' THEN 1
                    WHEN status = 'Saiu' THEN 2
                    ELSE 3
                END,
                u.name
        """
        return self.executor.execute_query(query)

    def get_accesses_by_day(self, days: int = 30) -> List[Dict[str, Any]]:
        query = """
            SELECT
                DATE(created_at) as date,
                COUNT(*) as total,
                SUM(CASE WHEN access_allowed = TRUE THEN 1 ELSE 0 END) as allowed,
                SUM(CASE WHEN access_allowed = FALSE THEN 1 ELSE 0 END) as denied
            FROM accessRegisters
            WHERE created_at >= DATE_SUB(CURDATE(), INTERVAL %s DAY)
            GROUP BY DATE(created_at)
            ORDER BY date
        """
        return self.executor.execute_query(query, (days,))

    def get_accesses_by_hour(self) -> List[Dict[str, Any]]:
        query = """
            SELECT
                HOUR(created_at) as hour,
                COUNT(*) as total,
                SUM(CASE WHEN access_allowed = TRUE THEN 1 ELSE 0 END) as allowed,
                SUM(CASE WHEN access_allowed = FALSE THEN 1 ELSE 0 END) as denied
            FROM accessRegisters
            WHERE DATE(created_at) = CURDATE()
            GROUP BY HOUR(created_at)
            ORDER BY hour
        """
        return self.executor.execute_query(query)

    def get_success_rate_by_day(self, days: int = 30) -> List[Dict[str, Any]]:
        query = """
            SELECT
                DATE(created_at) as date,
                COUNT(*) as total_attempts,
                SUM(CASE WHEN access_allowed = TRUE THEN 1 ELSE 0 END) as successful,
                ROUND((SUM(CASE WHEN access_allowed = TRUE THEN 1 ELSE 0 END) * 100.0 / COUNT(*)), 2) as success_rate
            FROM accessRegisters
            WHERE created_at >= DATE_SUB(CURDATE(), INTERVAL %s DAY)
            GROUP BY DATE(created_at)
            ORDER BY date
        """
        return self.executor.execute_query(query, (days,))

    def get_top_users(self, limit=10):
        query = """
            SELECT
                u.name,
                u.position,
                COUNT(ar.id) as access_count,
                MAX(ar.created_at) as last_access
            FROM users u
            INNER JOIN accessRegisters ar ON u.id = ar.user_id
            WHERE ar.access_allowed = TRUE
            GROUP BY u.id, u.name, u.position
            ORDER BY access_count DESC
            LIMIT %s
        """
        return self.executor.execute_query(query, (limit,))

    def get_notifications_by_type(self, days=30):
        query = """
            SELECT
                type_notification,
                COUNT(*) as count,
                SUM(CASE WHEN is_read = TRUE THEN 1 ELSE 0 END) as read_count,
                SUM(CASE WHEN is_read = FALSE THEN 1 ELSE 0 END) as unread_count
            FROM notifications
            WHERE created_at >= DATE_SUB(CURDATE(), INTERVAL %s DAY)
            GROUP BY type_notification
            ORDER BY count DESC
        """
        return self.executor.execute_query(query, (days,))

    def get_overtime_by_user(self, days: int = 30) -> List[Dict[str, Any]]:
        query = """
            WITH DailyHours AS (
                SELECT
                    u.id as user_id,
                    u.name,
                    u.position,
                    DATE(ar.created_at) as work_date,
                    MIN(CASE WHEN ar.type_access = 'entrada' AND ar.access_allowed = TRUE
                        THEN ar.created_at END) as first_entry,
                    MAX(CASE WHEN ar.type_access = 'saida' AND ar.access_allowed = TRUE
                        THEN ar.created_at END) as last_exit
                FROM users u
                INNER JOIN accessRegisters ar ON u.id = ar.user_id
                WHERE u.approved = TRUE
                AND ar.created_at >= DATE_SUB(CURDATE(), INTERVAL %s DAY)
                GROUP BY u.id, u.name, u.position, DATE(ar.created_at)
                HAVING first_entry IS NOT NULL AND last_exit IS NOT NULL
            ),
            HoursCalculated AS (
                SELECT
                    user_id,
                    name,
                    position,
                    work_date,
                    first_entry,
                    last_exit,
                    TIMESTAMPDIFF(MINUTE, first_entry, last_exit) / 60.0 as hours_worked,
                    GREATEST(0, (TIMESTAMPDIFF(MINUTE, first_entry, last_exit) / 60.0) - 8) as overtime_hours
                FROM DailyHours
            )
            SELECT
                user_id,
                name,
                position,
                COUNT(work_date) as days_worked,
                ROUND(SUM(hours_worked), 2) as total_hours_worked,
                ROUND(SUM(overtime_hours), 2) as total_overtime_hours
            FROM HoursCalculated
            WHERE overtime_hours > 0
            GROUP BY user_id, name, position
            HAVING total_overtime_hours > 0
            ORDER BY total_overtime_hours DESC
        """
        return self.executor.execute_query(query, (days,))

    def get_daily_overtime_detail(self, user_id: int, days: int = 30) -> List[Dict[str, Any]]:
        query = """
            WITH DailyHours AS (
                SELECT
                    DATE(ar.created_at) as work_date,
                    MIN(CASE WHEN ar.type_access = 'entrada' AND ar.access_allowed = TRUE
                        THEN ar.created_at END) as first_entry,
                    MAX(CASE WHEN ar.type_access = 'saida' AND ar.access_allowed = TRUE
                        THEN ar.created_at END) as last_exit
                FROM accessRegisters ar
                WHERE ar.user_id = %s
                AND ar.created_at >= DATE_SUB(CURDATE(), INTERVAL %s DAY)
                GROUP BY DATE(ar.created_at)
                HAVING first_entry IS NOT NULL AND last_exit IS NOT NULL
            )
            SELECT
                work_date,
                first_entry,
                last_exit,
                ROUND(TIMESTAMPDIFF(MINUTE, first_entry, last_exit) / 60.0, 2) as hours_worked,
                ROUND(GREATEST(0, (TIMESTAMPDIFF(MINUTE, first_entry, last_exit) / 60.0) - 8), 2) as overtime_hours
            FROM DailyHours
            WHERE TIMESTAMPDIFF(MINUTE, first_entry, last_exit) / 60.0 > 8
            ORDER BY work_date DESC
        """
        return self.executor.execute_query(query, (user_id, days))
