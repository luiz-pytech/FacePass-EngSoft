"""
Dashboard Service - Lógica de negócio para o dashboard de gestão
"""


class DashboardService:
    def __init__(self, dashboard_repository, user_service, notification_service):
        self.dashboard_repository = dashboard_repository
        self.user_service = user_service
        self.notification_service = notification_service

    def get_quick_stats(self):
        try:
            user_stats = self.user_service.get_statistics()

            today_total = self.dashboard_repository.get_today_accesses_count()
            today_allowed = self.dashboard_repository.get_today_allowed_count()
            today_denied = self.dashboard_repository.get_today_denied_count()
            unread_notifications = self.dashboard_repository.get_unread_notifications_count()

            total_users = user_stats.get('total', 0)
            approved_users = user_stats.get('approved', 0)
            approval_rate = (approved_users / total_users * 100) if total_users > 0 else 0.0

            return {
                'success': True,
                'data': {
                    'total_users': total_users,
                    'approved_users': approved_users,
                    'pending_users': user_stats.get('pending', 0),
                    'approval_rate': approval_rate,
                    'today_total': today_total,
                    'today_allowed': today_allowed,
                    'today_denied': today_denied,
                    'unread_notifications': unread_notifications
                }
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro ao obter estatísticas: {str(e)}',
                'data': {}
            }

    def get_present_users(self):
        try:
            users = self.dashboard_repository.get_present_users()

            return {
                'success': True,
                'data': users,
                'count': len(users)
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro ao obter usuários presentes: {str(e)}',
                'data': [],
                'count': 0
            }

    def get_access_timeline(self, days=30):
        try:
            data = self.dashboard_repository.get_accesses_by_day(days)

            return {
                'success': True,
                'data': data
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro ao obter timeline de acessos: {str(e)}',
                'data': []
            }

    def get_hourly_access_distribution(self):
        try:
            data = self.dashboard_repository.get_accesses_by_hour()

            return {
                'success': True,
                'data': data
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro ao obter distribuição horária: {str(e)}',
                'data': []
            }

    def get_success_rate_trend(self, days=30):
        try:
            data = self.dashboard_repository.get_success_rate_by_day(days)

            return {
                'success': True,
                'data': data
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro ao obter taxa de sucesso: {str(e)}',
                'data': []
            }

    def get_top_active_users(self, limit=10):
        try:
            data = self.dashboard_repository.get_top_users(limit)

            return {
                'success': True,
                'data': data
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro ao obter top usuários: {str(e)}',
                'data': []
            }

    def get_notification_distribution(self, days=30):
        try:
            data = self.dashboard_repository.get_notifications_by_type(days)

            return {
                'success': True,
                'data': data
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro ao obter distribuição de notificações: {str(e)}',
                'data': []
            }