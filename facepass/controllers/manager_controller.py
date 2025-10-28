from typing import Dict
from facepass.services.manager_service import ManagerService
from facepass.validators.input_validator import InputValidator


class ManagerController:
    """
    Controller para operações relacionadas a gestores.

    Responsabilidades:
    - Validar inputs de autenticação usando InputValidator
    - Orquestrar login e logout
    - Tratar exceções e retornar respostas padronizadas
    - Formatar dados para apresentação na UI
    """

    def __init__(self, manager_service: ManagerService):
        self.manager_service = manager_service
        self.validator = InputValidator()

    def authenticate(self, email: str, password: str) -> Dict:
        """
        Processa a autenticação de um gestor.

        Arguments:
            email (str): Email do gestor
            password (str): Senha em texto plano

        Returns:
            Dict com formato:
            {
                'success': bool,
                'message': str,
                'data': {
                    'id': int,
                    'name': str,
                    'email': str
                } | None
                'errors': List[str]
            }
        """
        errors = []

        # Validação usando InputValidator
        if not email or not email.strip():
            errors.append("Email é obrigatório.")
        elif not self.validator.validar_email(email):
            errors.append("Email inválido.")

        if not password or not password.strip():
            errors.append("Senha é obrigatória.")

        if errors:
            return {
                'success': False,
                'message': "Erro na validação dos dados.",
                'data': None,
                'errors': errors
            }

        try:
            # Autenticar via service
            gestor = self.manager_service.authenticate(
                email.strip(), password.strip())

            if not gestor:
                return {
                    'success': False,
                    'message': "Email ou senha incorretos.",
                    'data': None,
                    'errors': ["Credenciais inválidas"]
                }

            # Login bem-sucedido
            return {
                'success': True,
                'message': f"Bem-vindo, {gestor.name}!",
                'data': {
                    'id': gestor.id,
                    'name': gestor.name,
                    'email': gestor.email
                },
                'errors': []
            }

        except ValueError as e:
            return {
                'success': False,
                'message': "Erro de validação.",
                'data': None,
                'errors': [str(e)]
            }
        except Exception as e:
            return {
                'success': False,
                'message': "Erro ao realizar login.",
                'data': None,
                'errors': [str(e)]
            }

    def get_manager_info(self, manager_id: int) -> Dict:
        """
        Obtém informações de um gestor por ID.

        Arguments:
            manager_id (int): ID do gestor

        Returns:
            Dict padronizado
        """
        try:
            gestor = self.manager_service.get_manager_by_id(manager_id)

            if not gestor:
                return {
                    'success': False,
                    'message': 'Gestor não encontrado.',
                    'data': None,
                    'errors': ['ID inválido']
                }

            return {
                'success': True,
                'message': 'Gestor encontrado.',
                'data': {
                    'id': gestor.id,
                    'name': gestor.name,
                    'email': gestor.email
                },
                'errors': []
            }

        except Exception as e:
            return {
                'success': False,
                'message': 'Erro ao buscar gestor.',
                'data': None,
                'errors': [str(e)]
            }

    def create_manager(self, name: str, email: str, password: str) -> Dict:
        """
        Cria um novo gestor.

        Arguments:
            name (str): Nome do gestor
            email (str): Email do gestor
            password (str): Senha em texto plano

        Returns:
            Dict padronizado
        """
        errors = []

        # Validação usando InputValidator
        if not self.validator.validar_name(name):
            errors.append("Nome inválido. Deve ter entre 3 e 100 caracteres.")

        if not self.validator.validar_email(email):
            errors.append("Email inválido.")

        if not self.validator.validar_password(password):
            errors.append("Senha inválida. Deve ter pelo menos 6 caracteres.")

        if errors:
            return {
                'success': False,
                'message': "Erro na validação dos dados.",
                'data': None,
                'errors': errors
            }

        try:
            gestor = self.manager_service.create_manager(
                name.strip(),
                email.strip(),
                password
            )

            return {
                'success': True,
                'message': "Gestor criado com sucesso.",
                'data': {
                    'id': gestor.id,
                    'name': gestor.name,
                    'email': gestor.email
                },
                'errors': []
            }

        except ValueError as e:
            return {
                'success': False,
                'message': "Erro de validação.",
                'data': None,
                'errors': [str(e)]
            }
        except Exception as e:
            return {
                'success': False,
                'message': "Erro ao criar gestor.",
                'data': None,
                'errors': [str(e)]
            }

    def list_all_managers(self) -> Dict:
        """
        Lista todos os gestores.

        Returns:
            Dict padronizado
        """
        try:
            gestores = self.manager_service.list_all_managers()

            managers_data = [
                {
                    'id': g.id,
                    'name': g.name,
                    'email': g.email
                }
                for g in gestores
            ]

            return {
                'success': True,
                'message': f'{len(gestores)} gestor(es) encontrado(s).',
                'data': managers_data,
                'errors': []
            }

        except Exception as e:
            return {
                'success': False,
                'message': 'Erro ao listar gestores.',
                'data': [],
                'errors': [str(e)]
            }

    def get_stats(self) -> Dict:
        """
        Obtém estatísticas de gestores.

        Returns:
            Dict padronizado
        """
        try:
            stats = self.manager_service.get_statistics()

            return {
                'success': True,
                'message': 'Estatísticas obtidas.',
                'data': stats,
                'errors': []
            }

        except Exception as e:
            return {
                'success': False,
                'message': 'Erro ao obter estatísticas.',
                'data': None,
                'errors': [str(e)]
            }
