
class Gestor:
    """Model class representing a manager in the FacePass system."""

    def __init__(self, id: int, name: str, email: str, password_hash: str):
        self.id: int = id
        self.name: str = name
        self.email: str = email
        self.password_hash: str = password_hash

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "password_hash": self.password_hash
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            id=data.get("id", 0),
            name=data.get("name", ""),
            email=data.get("email", ""),
            password_hash=data.get("password_hash", "")
        )
