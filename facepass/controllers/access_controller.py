from typing import Dict, List
from facepass.services.access_service import AccessService
from datetime import datetime


class AccessController:
    """
    Controller para gerenciar registros de acesso.

    Responsabilidades:
    - Orquestrar chamadas aos services
    - Tratar exceções e retornar respostas padronizadas
    - Formatar dados para apresentação na UI
    """

    def __init__(self, access_service: AccessService):
        self.access_service = access_service

    def get_registers_with_filters(self, user_name: str = "", status: str = "Todos",
                                   location: str = "", start_date: str = "", end_date: str = "") -> Dict:
        """
        Busca registros de acesso com filtros

        Args:
            user_name: Nome do usu�rio (parcial)
            status: "Todos", "Permitido" ou "Negado"
            location: Local/C�mera (ainda n�o implementado no banco)
            start_date: Data inicial (YYYY-MM-DD)
            end_date: Data final (YYYY-MM-DD)

        Returns:
            Dict com formato:
            {
                'success': bool,
                'message': str,
                'data': List[Dict],
                'errors': List[str]
            }
        """
        try:
            filters = {
                'user_name': user_name,
                'status': status,
                'location': location,
                'start_date': start_date,
                'end_date': end_date
            }

            registers = self.access_service.get_registers_by_filters(filters)

            return {
                'success': True,
                'message': f'{len(registers)} registro(s) encontrado(s)',
                'data': registers,
                'errors': []
            }
        except Exception as e:
            return {
                'success': False,
                'message': 'Erro ao buscar registros',
                'data': [],
                'errors': [str(e)]
            }

    def get_statistics_by_period(self, start_date: str = "", end_date: str = "") -> Dict:
        """
        Obt�m estat�sticas do per�odo

        Args:
            start_date: Data inicial (YYYY-MM-DD)
            end_date: Data final (YYYY-MM-DD)

        Returns:
            Dict com estat�sticas do per�odo
        """
        try:
            stats = self.access_service.get_statistics_by_period(
                start_date, end_date)

            return {
                'success': True,
                'message': 'Estat�sticas obtidas com sucesso',
                'data': stats,
                'errors': []
            }
        except Exception as e:
            return {
                'success': False,
                'message': 'Erro ao obter estat�sticas',
                'data': {
                    'total': 0,
                    'permitidos': 0,
                    'negados': 0,
                    'taxa_sucesso': 0.0
                },
                'errors': [str(e)]
            }

    def get_all_registers(self) -> Dict:
        """
        Retorna todos os registros de acesso

        Returns:
            Dict padronizado com lista de registros
        """
        try:
            registers = self.access_service.list_all_access_records()

            return {
                'success': True,
                'message': f'{len(registers)} registro(s) encontrado(s)',
                'data': registers,
                'errors': []
            }
        except Exception as e:
            return {
                'success': False,
                'message': 'Erro ao listar registros',
                'data': [],
                'errors': [str(e)]
            }

    def export_registers_csv(self, registers: List[Dict]) -> str:
        """
        Exporta registros para formato CSV

        Args:
            registers: Lista de registros a exportar

        Returns:
            String com conte�do CSV
        """
        if not registers:
            return "Nenhum registro dispon�vel"

        # Cabe�alho
        csv_lines = [
            "ID,Usuario,Data/Hora,Status,Tipo Acesso,Motivo Negacao\n"]

        # Dados
        for reg in registers:
            linha = f"{reg.get('id', '')},"
            linha += f"{reg.get('user_name', 'Desconhecido')},"

            # Formatar data
            created_at = reg.get('created_at', '')
            if isinstance(created_at, datetime):
                linha += f"{created_at.strftime('%d/%m/%Y %H:%M:%S')},"
            else:
                linha += f"{created_at},"

            linha += f"{'Permitido' if reg.get('access_allowed') else 'Negado'},"
            linha += f"{reg.get('type_access', '')},"
            linha += f"{reg.get('reason_denied', '')}\n"
            csv_lines.append(linha)

        return "".join(csv_lines)
