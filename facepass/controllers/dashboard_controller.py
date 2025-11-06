"""
Dashboard Controller - Interface entre o service e a UI
"""


class DashboardController:
    """Controller para gerenciar comunicação entre dashboard service e UI"""

    def __init__(self, dashboard_service):
        """
        Inicializa o controller

        Args:
            dashboard_service: Instância do DashboardService
        """
        self.dashboard_service = dashboard_service

    def get_quick_stats(self):
        """
        Obtém estatísticas rápidas para os quick cards

        Returns:
            dict: Resultado da operação com dados ou mensagem de erro
        """
        return self.dashboard_service.get_quick_stats()

    def get_present_users(self):
        """
        Obtém lista de usuários presentes

        Returns:
            dict: Resultado com lista de usuários presentes
        """
        return self.dashboard_service.get_present_users()

    def get_access_timeline_data(self, days=30):
        """
        Obtém dados para gráfico de linha temporal

        Args:
            days: Número de dias para análise

        Returns:
            dict: Dados formatados para o gráfico
        """
        return self.dashboard_service.get_access_timeline(days)

    def get_hourly_distribution_data(self):
        """
        Obtém dados para gráfico de distribuição horária

        Returns:
            dict: Dados formatados para o gráfico
        """
        return self.dashboard_service.get_hourly_access_distribution()

    def get_success_rate_data(self, days=30):
        """
        Obtém dados para gráfico de taxa de sucesso

        Args:
            days: Número de dias para análise

        Returns:
            dict: Dados formatados para o gráfico
        """
        return self.dashboard_service.get_success_rate_trend(days)

    def get_top_users_data(self, limit=10):
        """
        Obtém ranking de usuários mais ativos

        Args:
            limit: Número de usuários a retornar

        Returns:
            dict: Lista de top usuários
        """
        return self.dashboard_service.get_top_active_users(limit)

    def get_notification_distribution_data(self, days=30):
        """
        Obtém distribuição de notificações por tipo

        Args:
            days: Número de dias para análise

        Returns:
            dict: Dados de notificações
        """
        return self.dashboard_service.get_notification_distribution(days)

    def get_all_dashboard_data(self):
        """
        Obtém todos os dados necessários para o dashboard de uma vez

        Returns:
            dict: Todos os dados do dashboard
        """
        return self.dashboard_service.get_all_dashboard_data()