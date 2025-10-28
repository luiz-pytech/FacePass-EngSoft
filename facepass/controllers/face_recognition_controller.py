# -*- coding: utf-8 -*-
from typing import Dict, Optional, Tuple
from datetime import datetime
from facepass.services.face_recognition_service import FaceRecognitionService
from facepass.services.user_service import UsuarioService
from facepass.services.access_service import AccessService
from facepass.models.user import Usuario
from facepass.models.registerAccess import RegistroAcesso


class FaceRecognitionController:
    """
    Controller para operações de reconhecimento facial.

    Responsabilidades:
    - Orquestrar chamadas aos services de reconhecimento facial, usuários e acesso
    - Tratar exceções e retornar respostas padronizadas
    - Integrar reconhecimento facial com sistema de registros e notificações
    - Validar aprovação de usuários antes de permitir acesso
    """

    def __init__(
        self,
        face_recognition_service: FaceRecognitionService,
        user_service: UsuarioService,
        access_service: AccessService
    ):
        self.face_recognition_service = face_recognition_service
        self.user_service = user_service
        self.access_service = access_service

    def process_access_attempt(self, image_bytes: bytes, manager_id: int, location: str = "Entrada Principal") -> Dict:
        """
        Processa uma tentativa de acesso via reconhecimento facial.

        Esta função:
        1. Identifica o rosto na imagem
        2. Valida se o usuário está aprovado
        3. Registra a tentativa de acesso
        4. Dispara notificações se acesso negado

        Arguments:
            image_bytes (bytes): Imagem capturada para reconhecimento
            manager_id (int): ID do gestor para notificações
            location (str): Local da tentativa de acesso

        Returns:
            Dict com resultado padronizado contendo:
            - success (bool): Se o processamento foi bem-sucedido
            - message (str): Mensagem descritiva
            - data (dict): Dados do resultado do acesso
            - errors (list): Lista de erros, se houver
        """
        try:
            # 1. Tentar identificar o rosto
            face_identify = self.face_recognition_service.identify_face(image_bytes)

            # Inicializar resultado padrão (acesso negado)
            result = {
                'acesso_permitido': False,
                'usuario_id': None,
                'usuario_nome': 'Desconhecido',
                'usuario_cargo': None,
                'confianca': 0.0,
                'motivo_negacao': 'Rosto não reconhecido no sistema',
                'data_hora': datetime.now(),
                'local': location
            }

            # 2. Se rosto foi identificado
            if face_identify:
                user_id, confidence = face_identify

                # 3. Buscar dados do usuário
                user_data = self.user_service.get_user_by_id(user_id)

                if user_data:
                    user = Usuario.from_dict(user_data)

                    # 4. Validar se usuário está aprovado
                    if user.approved:
                        # ACESSO PERMITIDO
                        result = {
                            'acesso_permitido': True,
                            'usuario_id': user.id,
                            'usuario_nome': user.name,
                            'usuario_cargo': user.position,
                            'confianca': confidence,
                            'motivo_negacao': None,
                            'data_hora': datetime.now(),
                            'local': location
                        }
                    else:
                        # ACESSO NEGADO - Usuário não aprovado
                        result = {
                            'acesso_permitido': False,
                            'usuario_id': user.id,
                            'usuario_nome': user.name,
                            'usuario_cargo': user.position,
                            'confianca': confidence,
                            'motivo_negacao': 'Usuário aguardando aprovação do gestor',
                            'data_hora': datetime.now(),
                            'local': location
                        }
                else:
                    # ACESSO NEGADO - Usuário não encontrado (caso raro)
                    result['motivo_negacao'] = 'Usuário não encontrado no sistema'

            # 5. Registrar a tentativa de acesso
            registro_acesso = RegistroAcesso(
                id=0,
                user_id=result['usuario_id'],
                created_at=result['data_hora'],
                type_access='Reconhecimento Facial',
                access_allowed=result['acesso_permitido'],
                reason_denied=result['motivo_negacao'],
                captured_image=image_bytes
            )

            # 6. Salvar registro e disparar notificações se necessário
            self.access_service.register_access_attempt(
                registro=registro_acesso,
                manager_id=manager_id,
                user_name=result['usuario_nome'] if result['usuario_id'] else None
            )

            # 7. Retornar resultado padronizado
            return {
                'success': True,
                'message': 'Acesso permitido' if result['acesso_permitido'] else 'Acesso negado',
                'data': result,
                'errors': []
            }

        except Exception as e:
            return {
                'success': False,
                'message': 'Erro ao processar reconhecimento facial',
                'data': {
                    'acesso_permitido': False,
                    'usuario_nome': 'Erro',
                    'motivo_negacao': 'Erro no sistema de reconhecimento',
                    'data_hora': datetime.now(),
                    'local': location
                },
                'errors': [str(e)]
            }

    def save_user_face_encoding(self, user_id: int, image_bytes: bytes) -> Dict:
        """
        Gera e salva o encoding facial de um usuário.

        Arguments:
            user_id (int): ID do usuário
            image_bytes (bytes): Imagem facial do usuário

        Returns:
            Dict padronizado com resultado
        """
        try:
            face_encoding = self.face_recognition_service.save_user_face(user_id, image_bytes)

            if face_encoding:
                return {
                    'success': True,
                    'message': 'Encoding facial salvo com sucesso',
                    'data': {'encoding_id': face_encoding.id},
                    'errors': []
                }
            else:
                return {
                    'success': False,
                    'message': 'Não foi possível detectar rosto na imagem',
                    'data': None,
                    'errors': ['Nenhum rosto detectado na imagem fornecida']
                }

        except Exception as e:
            return {
                'success': False,
                'message': 'Erro ao salvar encoding facial',
                'data': None,
                'errors': [str(e)]
            }

    def verify_user_face(self, user_id: int, image_bytes: bytes) -> Dict:
        """
        Verifica se uma imagem corresponde ao usuário específico.

        Arguments:
            user_id (int): ID do usuário
            image_bytes (bytes): Imagem para verificação

        Returns:
            Dict padronizado com nível de confiança
        """
        try:
            confidence = self.face_recognition_service.verify_face_match(user_id, image_bytes)

            if confidence is not None:
                return {
                    'success': True,
                    'message': f'Rosto corresponde ao usuário (confiança: {confidence*100:.1f}%)',
                    'data': {'match': True, 'confidence': confidence},
                    'errors': []
                }
            else:
                return {
                    'success': True,
                    'message': 'Rosto não corresponde ao usuário',
                    'data': {'match': False, 'confidence': 0.0},
                    'errors': []
                }

        except Exception as e:
            return {
                'success': False,
                'message': 'Erro ao verificar rosto',
                'data': None,
                'errors': [str(e)]
            }
