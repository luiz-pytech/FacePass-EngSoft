
class DashboardRepository:
    """Repository para queries relacionadas ao dashboard de gestão"""

    def __init__(self, connection):
        """
        Inicializa o repository com uma conexão ao banco de dados

        Args:
            connection: Conexão MySQL ativa
        """
        self.connection = connection

    def get_today_accesses_count(self):
        """Retorna o total de acessos hoje"""
        query = """
            SELECT COUNT(*) as count
            FROM accessRegisters
            WHERE DATE(created_at) = CURDATE()
        """
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute(query)
        result = cursor.fetchone()
        cursor.close()
        return result['count'] if result else 0

    def get_today_allowed_count(self):
        """Retorna o total de acessos permitidos hoje"""
        query = """
            SELECT COUNT(*) as count
            FROM accessRegisters
            WHERE DATE(created_at) = CURDATE()
            AND access_allowed = TRUE
        """
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute(query)
        result = cursor.fetchone()
        cursor.close()
        return result['count'] if result else 0

    def get_today_denied_count(self):
        """Retorna o total de acessos negados hoje"""
        query = """
            SELECT COUNT(*) as count
            FROM accessRegisters
            WHERE DATE(created_at) = CURDATE()
            AND access_allowed = FALSE
        """
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute(query)
        result = cursor.fetchone()
        cursor.close()
        return result['count'] if result else 0

    def get_unread_notifications_count(self):
        """Retorna o total de notificações não lidas"""
        query = """
            SELECT COUNT(*) as count
            FROM notifications
            WHERE is_read = FALSE
        """
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute(query)
        result = cursor.fetchone()
        cursor.close()
        return result['count'] if result else 0

    def get_present_users(self):
        """Retorna lista de usuários atualmente presentes"""
        query = """
            SELECT
                u.id,
                u.name,
                u.email,
                u.position,
                last_access.type_access as last_action,
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
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()
        return results

    def get_accesses_by_day(self, days=30):
        """
        Retorna acessos agrupados por dia

        Args:
            days: Número de dias para retornar (padrão: 30)
        """
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
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute(query, (days,))
        results = cursor.fetchall()
        cursor.close()
        return results

    def get_accesses_by_hour(self):
        """Retorna acessos agrupados por hora (hoje)"""
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
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()
        return results

    def get_success_rate_by_day(self, days=30):
        """
        Retorna taxa de sucesso por dia

        Args:
            days: Número de dias para retornar (padrão: 30)
        """
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
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute(query, (days,))
        results = cursor.fetchall()
        cursor.close()
        return results

    def get_top_users(self, limit=10):
        """
        Retorna top usuários com mais acessos

        Args:
            limit: Número de usuários a retornar (padrão: 10)
        """
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
        """
        Retorna notificações agrupadas por tipo

        Args:
            days: Número de dias para retornar (padrão: 30)
        """
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