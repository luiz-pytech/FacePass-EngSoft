from typing import Optional
import datetime


class Usuario:
    """Model class representing a user in the FacePass system."""

    def __init__(self, id: int, name: str, email: str, cpf: str, photo_recognition: bytes, position: str):
        self.id: int = id
        self.name: str = name
        self.email: str = email
        self.cpf: str = cpf
        self.created_at: datetime.datetime = datetime.datetime.now()
        self.photo_recognition: bytes = photo_recognition
        self.position: str = position
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
        usuario = cls(
            id=data.get("id"),
            name=data.get("name"),
            email=data.get("email"),
            cpf=data.get("cpf"),
            photo_recognition=data.get("photo_recognition"),
            position=data.get("position"),
        )
        if "approved" in data:
            usuario.approved = bool(data.get("approved"))
        if "created_at" in data:
            usuario.created_at = data.get("created_at")
        return usuario
