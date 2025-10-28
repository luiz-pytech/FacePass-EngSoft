# -*- coding: utf-8 -*-
from typing import Dict, Optional
from facepass.services.notification_service import NotificationService


class NotificationController:
    """
    Controller para operacoes relacionadas a notificacoes.

    Responsabilidades:
    - Orquestrar chamadas aos services de notificacao
    - Tratar excecoes e retornar respostas padronizadas
    - Formatar dados para apresentacao na UI
    """

    def __init__(self, notification_service: NotificationService):
        self.notification_service = notification_service

    def list_all_notifications(self, manager_id: Optional[int] = None) -> Dict:
        """
        Lista todas as notificacoes.

        Arguments:
            manager_id (Optional[int]): ID do gestor para filtrar notificacoes

        Returns:
            Dict padronizado com lista de notificacoes
        """
        try:
            notifications = self.notification_service.list_all_notifications(
                manager_id)

            return {
                'success': True,
                'message': f'{len(notifications)} notificacao(oes) encontrada(s)',
                'data': notifications,
                'errors': []
            }
        except Exception as e:
            return {
                'success': False,
                'message': 'Erro ao listar notificacoes',
                'data': [],
                'errors': [str(e)]
            }

    def list_unread_notifications(self, manager_id: Optional[int] = None) -> Dict:
        """
        Lista notificacoes nao lidas.

        Arguments:
            manager_id (Optional[int]): ID do gestor para filtrar notificacoes

        Returns:
            Dict padronizado com lista de notificacoes nao lidas
        """
        try:
            notifications = self.notification_service.list_unread_notifications(
                manager_id)

            return {
                'success': True,
                'message': f'{len(notifications)} notificacao(oes) nao lida(s)',
                'data': notifications,
                'errors': []
            }
        except Exception as e:
            return {
                'success': False,
                'message': 'Erro ao listar notificacoes nao lidas',
                'data': [],
                'errors': [str(e)]
            }

    def mark_as_read(self, notification_id: int) -> Dict:
        """
        Marca uma notificacao como lida.

        Arguments:
            notification_id (int): ID da notificacao

        Returns:
            Dict padronizado
        """
        try:
            self.notification_service.mark_as_read(notification_id)

            return {
                'success': True,
                'message': 'Notificacao marcada como lida',
                'data': None,
                'errors': []
            }
        except Exception as e:
            return {
                'success': False,
                'message': 'Erro ao marcar notificacao como lida',
                'data': None,
                'errors': [str(e)]
            }

    def delete_notification(self, notification_id: int) -> Dict:
        """
        Deleta uma notificacao.

        Arguments:
            notification_id (int): ID da notificacao

        Returns:
            Dict padronizado
        """
        try:
            self.notification_service.delete_notification(notification_id)

            return {
                'success': True,
                'message': 'Notificacao removida com sucesso',
                'data': None,
                'errors': []
            }
        except Exception as e:
            return {
                'success': False,
                'message': 'Erro ao remover notificacao',
                'data': None,
                'errors': [str(e)]
            }

    def get_statistics(self, manager_id: Optional[int] = None) -> Dict:
        """
        Obtem estatisticas de notificacoes.

        Arguments:
            manager_id (Optional[int]): ID do gestor para filtrar

        Returns:
            Dict com estatisticas
        """
        try:
            all_notifications = self.notification_service.list_all_notifications(
                manager_id)
            unread_notifications = self.notification_service.list_unread_notifications(
                manager_id)

            stats = {
                'total': len(all_notifications),
                'unread': len(unread_notifications),
                'read': len(all_notifications) - len(unread_notifications)
            }

            return {
                'success': True,
                'message': 'Estatisticas obtidas',
                'data': stats,
                'errors': []
            }
        except Exception as e:
            return {
                'success': False,
                'message': 'Erro ao obter estatisticas',
                'data': None,
                'errors': [str(e)]
            }
