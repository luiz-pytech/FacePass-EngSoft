import re
from facepass.models.user import Usuario
from facepass.models.registerAcess import RegistroAcesso
from facepass.models.notification import Notificacao


class ValidatorService:
    @staticmethod
    def validar_nome(nome: str) -> bool:
        return bool(nome) and len(nome) <= 100

    @staticmethod
    def validar_email(email: str) -> bool:
        regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(regex, email))

    @staticmethod
    def validar_cpf(cpf: str) -> bool:
        regex = r'^\d{3}\.\d{3}\.\d{3}-\d{2}$|^\d{11}$'
        return bool(re.match(regex, cpf))

    @staticmethod
    def validar_usuario(usuario: Usuario) -> bool:
        return (ValidatorService.validar_nome(usuario.nome) and
                ValidatorService.validar_email(usuario.email) and
                ValidatorService.validar_cpf(usuario.cpf))
