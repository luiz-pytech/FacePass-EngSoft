import bcrypt
from typing import Optional, Dict
from facepass.models.manager import Gestor
from facepass.database.repository.manager_repository import ManagerRepository


class ManagerService:
    def __init__(self, manager_repository: ManagerRepository):
        self.manager_repository = manager_repository

    @staticmethod
    def hash_password(password: str) -> str:
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

    def authenticate(self, email: str, password: str) -> Optional[Gestor]:
        if not email or not password:
            raise ValueError("Email e senha são obrigatórios.")

        manager_data = self.manager_repository.get_manager_by_email(email)

        if not manager_data:
            return None

        if not self.verify_password(password, manager_data['password_hash']):
            return None

        return Gestor.from_dict(manager_data)

    def get_manager_by_id(self, manager_id: int) -> Optional[Gestor]:
        manager_data = self.manager_repository.get_manager_by_id(manager_id)

        if not manager_data:
            return None

        return Gestor.from_dict(manager_data)

    def get_manager_by_email(self, email: str) -> Optional[Gestor]:
        manager_data = self.manager_repository.get_manager_by_email(email)

        if not manager_data:
            return None

        return Gestor.from_dict(manager_data)

    def create_manager(self, name: str, email: str, password: str) -> Gestor:
        if not name or not email or not password:
            raise ValueError("Nome, email e senha são obrigatórios.")

        existing = self.manager_repository.get_manager_by_email(email)
        if existing:
            raise ValueError("Email já cadastrado.")

        password_hash = self.hash_password(password)

        manager_data = {
            'name': name,
            'email': email,
            'password_hash': password_hash
        }

        manager_id = self.manager_repository.create_manager(manager_data)

        return Gestor(
            id=manager_id,
            name=name,
            email=email,
            password_hash=password_hash
        )

    def update_manager(self, manager_id: int, name: str, email: str, password: Optional[str] = None) -> None:
        existing = self.manager_repository.get_manager_by_id(manager_id)
        if not existing:
            raise ValueError("Gestor não encontrado.")

        if password:
            password_hash = self.hash_password(password)
        else:
            password_hash = existing['password_hash']

        manager_data = {
            'name': name,
            'email': email,
            'password_hash': password_hash
        }

        self.manager_repository.update_manager(manager_id, manager_data)

    def delete_manager(self, manager_id: int) -> None:
        existing = self.manager_repository.get_manager_by_id(manager_id)
        if not existing:
            raise ValueError("Gestor não encontrado.")

        self.manager_repository.delete_manager(manager_id)

    def list_all_managers(self) -> list[Gestor]:
        managers_data = self.manager_repository.list_all_managers()
        return [Gestor.from_dict(data) for data in managers_data]

    def get_statistics(self) -> Dict:
        total = self.manager_repository.get_manager_count()

        return {
            'total': total
        }
