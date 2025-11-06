"""
Dashboard Service - Lógica de negócio para o dashboard de gestão
"""


class DashboardService:
    """Service para gerenciar lógica de negócio do dashboard"""

    def __init__(self, dashboard_repository, user_service, notification_service):
        """
        Inicializa o service com os repositories necessários

        Args:
            dashboard_repository: Repository do dashboard
            user_service: Service de usuários (para estatísticas)
            notification_service: Service de notificações
        """
        self.dashboard_repository = dashboard_repository
        self.user_service = user_service
        self.notification_service = notification_service

    def get_quick_stats(self):
        """
        Retorna estatísticas rápidas para os quick cards

        Returns:
            dict: Dicionário com todas as estatísticas
        """
        try:
            # Obter estatísticas de usuários
            user_stats_result = self.user_service.get_stats()
            user_stats = user_stats_result.get('data', {}) if user_stats_result.get('success') else {}

            # Obter estatísticas de acessos
            today_total = self.dashboard_repository.get_today_accesses_count()
            today_allowed = self.dashboard_repository.get_today_allowed_count()
            today_denied = self.dashboard_repository.get_today_denied_count()
            unread_notifications = self.dashboard_repository.get_unread_notifications_count()

            return {
                'success': True,
                'data': {
                    'total_users': user_stats.get('total_users', 0),
                    'approved_users': user_stats.get('approved_users', 0),
                    'pending_users': user_stats.get('pending_users', 0),
                    'approval_rate': user_stats.get('approval_rate', 0.0),
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
        """
        Retorna lista de usuários atualmente presentes

        Returns:
            dict: Lista de usuários presentes com informações adicionais
        """
        try:
            users = self.dashboard_repository.get_present_users()

            # Adicionar status 'present' para todos
            for user in users:
                user['status'] = 'present'

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
        """
        Retorna dados para o gráfico de linha temporal de acessos

        Args:
            days: Número de dias para análise

        Returns:
            dict: Dados formatados para o gráfico
        """
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
        """
        Retorna distribuição de acessos por hora (hoje)

        Returns:
            dict: Dados formatados para o gráfico
        """
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
        """
        Retorna tendência de taxa de sucesso

        Args:
            days: Número de dias para análise

        Returns:
            dict: Dados formatados para o gráfico
        """
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
        """
        Retorna ranking de usuários mais ativos

        Args:
            limit: Número de usuários a retornar

        Returns:
            dict: Lista de top usuários
        """
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
        """
        Retorna distribuição de notificações por tipo

        Args:
            days: Número de dias para análise

        Returns:
            dict: Dados de notificações agrupadas por tipo
        """
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

    def get_all_dashboard_data(self):
        """
        Retorna todos os dados do dashboard de uma vez (otimização)

        Returns:
            dict: Todos os dados necessários para renderizar o dashboard
        """
        try:
            return {
                'success': True,
                'data': {
                    'quick_stats': self.get_quick_stats(),
                    'present_users': self.get_present_users(),
                    'access_timeline': self.get_access_timeline(30),
                    'hourly_distribution': self.get_hourly_access_distribution(),
                    'success_rate': self.get_success_rate_trend(30),
                    'top_users': self.get_top_active_users(10),
                    'notifications': self.get_notification_distribution(30)
                }
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro ao obter dados do dashboard: {str(e)}',
                'data': {}
            }