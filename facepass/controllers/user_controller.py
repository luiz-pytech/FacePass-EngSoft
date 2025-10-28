from typing import Dict, List, Optional
from facepass.models.user import Usuario
from facepass.services.user_service import UsuarioService
from datetime import datetime
from facepass.validators.input_validator import InputValidator


class UserController:
    """
    Controller para operações relacionadas a usuários.

    Responsabilidades:
    - Validar inputs do usuário (UI)
    - Transformar dados de entrada em objetos de domínio
    - Orquestrar chamadas aos services
    - Tratar exceções e retornar respostas padronizadas
    - Formatar dados para apresentação na UI
    """

    def __init__(self, user_service: UsuarioService):
        self.user_service = user_service
        self.validator = InputValidator()

    def create_user(self, name: str, email: str, cpf: str, position: str, photo: bytes, terms_accepted: bool) -> Dict:
        """Processa o cadastro de um novo usuário

         Arguments:
            name (str): Nome completo do usuário
            email (str): Endereço de email
            cpf (str): CPF do usuário
            position (str): Cargo ou posição do usuário
            photo (bytes): Foto do usuário em bytes
            terms_accepted (bool): Indica se os termos foram aceitos

        Returns:
            Dict com formato:
            {
                'success': bool,
                'message': str,
                'data': Usuario | None
                'errors': List[str]
            }
        """
        errors = []

        if not self.validator.validar_name(name):
            errors.append("Nome inválido. Deve ter entre 3 e 100 caracteres.")
        if not self.validator.validar_email(email):
            errors.append("Email inválido.")
        if not self.validator.validar_cpf(cpf):
            errors.append("CPF inválido.")
        if not self.validator.validar_position(position):
            errors.append(
                "Cargo inválido. Deve ser 'Desenvolvedor', 'Analista de Dados' ou 'Gerente'.")
        if not self.validator.validar_photo(photo):
            errors.append("Foto inválida. Deve ser um arquivo não vazio.")
        if not self.validator.validar_terms_accepted(terms_accepted):
            errors.append("Os termos devem ser aceitos.")

        if errors:
            return {
                'success': False,
                'message': "Erro na validação dos dados.",
                'data': None,
                'errors': errors
            }
        try:
            usuario = Usuario(
                id=0,
                name=name.strip(),
                email=email.strip(),
                cpf=cpf.strip(),
                photo_recognition=photo,
                position=position.strip(),
            )
            usuario_criado = self.user_service.create_user(
                usuario, manager_id=1)
            return {
                'success': True,
                'message': "✅ **Cadastro enviado com sucesso!**",
                'data': usuario_criado,
                'errors': []
            }
        except Exception as e:
            return {
                'success': False,
                'message': "Erro ao criar usuário.",
                'data': None,
                'errors': [str(e)]
            }

    def approve_user(self, user_id: int, approved: bool, motivo: Optional[str] = None) -> Dict:
        """Processa a aprovação ou rejeição de um usuário pendente.

        Arguments:
            user_id (int): ID do usuário a ser aprovado ou rejeitado
            approved (bool): Indica se o usuário deve ser aprovado (True) ou rejeitado (False)
            motivo (Optional[str]): Motivo da rejeição, se aplicável

        Returns:
            Dict com formato:
            {
                'success': bool,
                'message': str,
                'data': Usuario | None
                'errors': List[str]
            }
        """
        try:
            if approved:
                self.user_service.approve_user(user_id)
                usuario = self.user_service.get_user_by_id(user_id)

                return {
                    'success': True,
                    'message': "Usuário aprovado com sucesso.",
                    'data': usuario,
                    'errors': []
                }
            else:
                # Rejeitar usuário (remove do sistema)
                self.user_service.reject_user(user_id)
                return {
                    'success': True,
                    'message': "Usuário rejeitado e removido do sistema.",
                    'data': None,
                    'errors': []
                }
        except Exception as e:
            return {
                'success': False,
                'message': 'Erro ao processar aprovação',
                'data': None,
                'errors': [str(e)]
            }

    def list_pending_users(self) -> Dict:
        """
        Lista usuários pendentes de aprovação.

        Returns:
            Dict padronizado
        """
        try:
            usuarios = self.user_service.list_pending_approvals()
            return {
                'success': True,
                'message': f'{len(usuarios)} usuário(s) pendente(s)',
                'data': usuarios,
                'errors': []
            }
        except Exception as e:
            return {
                'success': False,
                'message': 'Erro ao listar usuários',
                'data': [],
                'errors': [str(e)]
            }

    def get_user_status(self, email: str) -> Dict:
        """
        Consulta o status de cadastro de um usuário pelo email.

        Args:
            email: Email do usuário

        Returns:
            Dict com informações do status
        """
        try:
            usuario_dict = self.user_service.get_user_by_email(email)

            if not usuario_dict:
                return {
                    'success': False,
                    'message': 'Usuário não encontrado',
                    'data': None,
                    'errors': ['Email não cadastrado no sistema']
                }

            status_texto = "Aprovado" if usuario_dict['approved'] else "Aguardando Aprovação"

            return {
                'success': True,
                'message': f'Status: {status_texto}',
                'data': {
                    'nome': usuario_dict['name'],
                    'email': usuario_dict['email'],
                    'cargo': usuario_dict['position'],
                    'aprovado': usuario_dict['approved'],
                    'status_texto': status_texto
                },
                'errors': []
            }

        except Exception as e:
            return {
                'success': False,
                'message': 'Erro ao consultar status',
                'data': None,
                'errors': [str(e)]
            }

    def get_stats(self) -> Dict:
        """
        Obtém estatísticas gerais sobre os usuários.

        Returns:
            Dict com estatísticas
        """
        try:
            statistics = self.user_service.get_statistics()
            approved_users = statistics.get('approved', 0)
            pending_users = statistics.get('pending', 0)
            total_users = statistics.get('total', 0)

            stats = {
                'total_users': total_users,
                'approved_users': approved_users,
                'pending_users': pending_users,
                'approval_rate': (approved_users / total_users * 100) if total_users > 0 else 0
            }

            return {
                'success': True,
                'message': 'Estatísticas obtidas com sucesso',
                'data': stats,
                'errors': []
            }
        except Exception as e:
            return {
                'success': False,
                'message': 'Erro ao obter estatísticas',
                'data': None,
                'errors': [str(e)]
            }

    def list_all_users(self) -> Dict:
        """
        Lista todos os usuários do sistema.

        Returns:
            Dict padronizado com lista de usuários
        """
        try:
            usuarios = self.user_service.list_all_users()
            return {
                'success': True,
                'message': f'{len(usuarios)} usuário(s) encontrado(s)',
                'data': usuarios,
                'errors': []
            }
        except Exception as e:
            return {
                'success': False,
                'message': 'Erro ao listar usuários',
                'data': [],
                'errors': [str(e)]
            }

    def remove_user(self, user_id: int) -> Dict:
        """
        Remove um usuário do sistema.

        Arguments:
            user_id (int): ID do usuário a ser removido

        Returns:
            Dict padronizado
        """
        try:
            self.user_service.remove_user(user_id)
            return {
                'success': True,
                'message': 'Usuário removido com sucesso.',
                'data': None,
                'errors': []
            }
        except ValueError as e:
            return {
                'success': False,
                'message': 'Usuário não encontrado.',
                'data': None,
                'errors': [str(e)]
            }
        except Exception as e:
            return {
                'success': False,
                'message': 'Erro ao remover usuário.',
                'data': None,
                'errors': [str(e)]
            }

    def update_user(self, user_id: int, name: str, email: str, cpf: str, position: str, approved: bool) -> Dict:
        """
        Atualiza os dados de um usuário.

        Arguments:
            user_id (int): ID do usuário
            name (str): Nome completo
            email (str): Email
            cpf (str): CPF
            position (str): Cargo
            approved (bool): Status de aprovação

        Returns:
            Dict padronizado
        """
        errors = []

        # Validações
        if not self.validator.validar_name(name):
            errors.append("Nome inválido. Deve ter entre 3 e 100 caracteres.")
        if not self.validator.validar_email(email):
            errors.append("Email inválido.")
        if not self.validator.validar_cpf(cpf):
            errors.append("CPF inválido.")
        if not self.validator.validar_position(position):
            errors.append("Cargo inválido. Deve ser 'Desenvolvedor', 'Analista de Dados' ou 'Gerente'.")

        if errors:
            return {
                'success': False,
                'message': 'Erro na validação dos dados.',
                'data': None,
                'errors': errors
            }

        try:
            # Buscar usuário existente para pegar a foto
            usuario_existente_dict = self.user_service.get_user_by_id(user_id)

            if not usuario_existente_dict:
                return {
                    'success': False,
                    'message': 'Usuário não encontrado.',
                    'data': None,
                    'errors': ['ID inválido']
                }

            # Criar objeto Usuario atualizado
            usuario = Usuario(
                id=user_id,
                name=name.strip(),
                email=email.strip(),
                cpf=cpf.strip(),
                photo_recognition=usuario_existente_dict['photo_recognition'],
                position=position.strip()
            )
            usuario.approved = approved
            usuario.created_at = usuario_existente_dict['created_at']

            # Atualizar no banco
            self.user_service.update_user(usuario)

            return {
                'success': True,
                'message': 'Usuário atualizado com sucesso.',
                'data': usuario,
                'errors': []
            }

        except ValueError as e:
            return {
                'success': False,
                'message': 'Erro de validação.',
                'data': None,
                'errors': [str(e)]
            }
        except Exception as e:
            return {
                'success': False,
                'message': 'Erro ao atualizar usuário.',
                'data': None,
                'errors': [str(e)]
            }
