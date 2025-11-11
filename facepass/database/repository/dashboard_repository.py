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

    def get_present_users(self) -> List[Dict[str, Any]]:
        """Retorna apenas usuários presentes (última ação foi entrada)"""
        query = """
            SELECT
                u.name,
                u.position,
                last_access.created_at as last_entry_time
            FROM users u
            INNER JOIN (
                SELECT
                    ar.user_id,
                    ar.type_access,
                    ar.created_at,
                    ar.access_allowed
                FROM accessRegisters ar
                INNER JOIN (
                    SELECT user_id, MAX(created_at) as max_time
                    FROM accessRegisters
                    WHERE access_allowed = TRUE
                    GROUP BY user_id
                ) latest ON ar.user_id = latest.user_id AND ar.created_at = latest.max_time
            ) last_access ON u.id = last_access.user_id
            WHERE u.approved = TRUE
            AND last_access.type_access = 'entrada'
            ORDER BY u.name
        """
        return self.executor.execute_query(query)

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
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute(query, (limit,))
        results = cursor.fetchall()
        cursor.close()
        return results

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
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute(query, (days,))
        results = cursor.fetchall()
        cursor.close()
        return results
