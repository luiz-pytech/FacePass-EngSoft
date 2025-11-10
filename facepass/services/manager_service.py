import bcrypt
from typing import Optional, Dict
from facepass.models.manager import Gestor
from facepass.database.repository.manager_repository import ManagerRepository


class ManagerService:
    """
    Manager authentication and management service.

    Responsible for business logic related to:
    - Manager authentication (login/logout)
    - Password validation and hashing
    - Manager CRUD operations
    """

    def __init__(self, manager_repository: ManagerRepository):
        self.manager_repository = manager_repository

    @staticmethod
    def hash_password(password: str) -> str:
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

    def authenticate(self, email: str, password: str) -> Optional[Gestor]:
        """
        Authenticates a manager by email and password.

        Args:
            email: Manager's email
            password: Plain text password

        Returns:
            Gestor object if authentication successful, None otherwise

        Raises:
            ValueError: If email or password is empty
        """
        if not email or not password:
            raise ValueError("Email e senha são obrigatórios.")

        # Get manager from repository
        manager_data = self.manager_repository.get_manager_by_email(email)

        if not manager_data:
            return None

        # Verify password hash
        if not self.verify_password(password, manager_data['password_hash']):
            return None

        # Return Gestor object
        return Gestor.from_dict(manager_data)

    def get_manager_by_id(self, manager_id: int) -> Optional[Gestor]:
        """
        Gets a manager by ID.

        Args:
            manager_id: Manager's ID

        Returns:
            Gestor object or None if not found
        """
        manager_data = self.manager_repository.get_manager_by_id(manager_id)

        if not manager_data:
            return None

        return Gestor.from_dict(manager_data)

    def get_manager_by_email(self, email: str) -> Optional[Gestor]:
        """
        Gets a manager by email.

        Args:
            email: Manager's email

        Returns:
            Gestor object or None if not found
        """
        manager_data = self.manager_repository.get_manager_by_email(email)

        if not manager_data:
            return None

        return Gestor.from_dict(manager_data)

    def create_manager(self, name: str, email: str, password: str) -> Gestor:
        """
        Creates a new manager.

        Args:
            name: Manager's name
            email: Manager's email
            password: Plain text password

        Returns:
            Created Gestor object

        Raises:
            ValueError: If data is invalid or email already exists
        """
        if not name or not email or not password:
            raise ValueError("Nome, email e senha são obrigatórios.")

        # Check if email already exists
        existing = self.manager_repository.get_manager_by_email(email)
        if existing:
            raise ValueError("Email já cadastrado.")

        # Hash password
        password_hash = self.hash_password(password)

        # Create manager data
        manager_data = {
            'name': name,
            'email': email,
            'password_hash': password_hash
        }

        # Save to repository
        manager_id = self.manager_repository.create_manager(manager_data)

        # Return created manager
        return Gestor(
            id=manager_id,
            name=name,
            email=email,
            password_hash=password_hash
        )

    def update_manager(self, manager_id: int, name: str, email: str, password: Optional[str] = None) -> None:
        """
        Updates an existing manager.

        Args:
            manager_id: Manager's ID
            name: New name
            email: New email
            password: New password (optional, if None keeps current)

        Raises:
            ValueError: If manager not found or data invalid
        """
        existing = self.manager_repository.get_manager_by_id(manager_id)
        if not existing:
            raise ValueError("Gestor não encontrado.")

        # Use current password hash if no new password provided
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
        """
        Deletes a manager.

        Args:
            manager_id: Manager's ID

        Raises:
            ValueError: If manager not found
        """
        existing = self.manager_repository.get_manager_by_id(manager_id)
        if not existing:
            raise ValueError("Gestor não encontrado.")

        self.manager_repository.delete_manager(manager_id)

    def list_all_managers(self) -> list[Gestor]:
        """
        Lists all managers.

        Returns:
            List of Gestor objects
        """
        managers_data = self.manager_repository.list_all_managers()
        return [Gestor.from_dict(data) for data in managers_data]

    def get_statistics(self) -> Dict:
        """
        Returns manager statistics.

        Returns:
            Dictionary with total count
        """
        total = self.manager_repository.get_manager_count()

        return {
            'total': total
        }
