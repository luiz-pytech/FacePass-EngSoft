import re
from facepass.models.user import Usuario


class InputValidator:
    @staticmethod
    def validar_name(name: str) -> bool:
        if not name or len(name.strip()) < 3 or len(name) > 100:
            return False
        return True

    @staticmethod
    def validar_email(email: str) -> bool:
        regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(regex, email))

    @staticmethod
    def validar_cpf(cpf: str) -> bool:
        regex = r'^\d{3}\.\d{3}\.\d{3}-\d{2}$|^\d{11}$'
        return bool(re.match(regex, cpf))

    @staticmethod
    def validar_position(position: str) -> bool:
        positions_validas = {'Desenvolvedor', 'Analista de Dados', 'Gerente'}
        return position.lower() in (p.lower() for p in positions_validas)

    @staticmethod
    def validar_photo(photo: bytes) -> bool:
        return photo is not None and len(photo) > 0

    @staticmethod
    def validar_terms_accepted(terms_accepted: bool) -> bool:
        return terms_accepted is True

    @staticmethod
    def validar_password(password: str) -> bool:
        """Valida se a senha tem pelo menos 6 caracteres"""
        return password is not None and len(password.strip()) >= 6
