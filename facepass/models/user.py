from typing import Optional
import datetime


class Usuario:
    """Model class representing a user in the FacePass system."""

    def __init__(self, id: int, name: str, email: str, cpf: str, photo_recognition: bytes):
        self.id: int = id
        self.name: str = name
        self.email: str = email
        self.cpf: str = cpf
        self.created_at: datetime.datetime = datetime.datetime.now()
        self.photo_recognition: bytes = photo_recognition
        self.position: str = ""
        self.approved: bool = False

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "cpf": self.cpf,
            "created_at": self.created_at.isoformat(),
            "photo_recognition": self.photo_recognition,
            "position": self.position,
            "approved": self.approved,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data.get("id"),
            name=data.get("name"),
            email=data.get("email"),
            cpf=data.get("cpf"),
            photo_recognition=data.get("photo_recognition"),
        )
