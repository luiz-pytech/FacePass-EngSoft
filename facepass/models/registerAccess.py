import datetime
from typing import Optional


class RegistroAcesso:
    """Model class representing an access register in the FacePass system."""

    def __init__(self, id: int, user_id: int, created_at: datetime.datetime, type_access: str, access_allowed: bool):
        self.id: int = id
        self.user_id: int = user_id
        self.created_at: datetime.datetime = created_at
        self.type_access: str = type_access
        self.access_allowed: bool = access_allowed
        self.reason_denied: Optional[str] = None
        self.captured_image: Optional[bytes] = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat(),
            "type_access": self.type_access,
            "access_allowed": self.access_allowed,
            "reason_denied": self.reason_denied,
            "captured_image": self.captured_image,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'RegistroAcesso':
        registro = cls(
            id=data["id"],
            user_id=data["user_id"],
            created_at=datetime.datetime.fromisoformat(data["created_at"]),
            type_access=data["type_access"],
            access_allowed=data["access_allowed"]
        )
        registro.reason_denied = data.get("reason_denied")
        registro.captured_image = data.get("captured_image")
        return registro
