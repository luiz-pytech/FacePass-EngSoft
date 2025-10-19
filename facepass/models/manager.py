
class Gestor:
    def __init__(self, id: int, nome: str, email: str, senha_hash: str):
        self.id = id
        self.nome = nome
        self.email = email
        self.senha_hash = senha_hash

    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "email": self.email,
            "senha_hash": self.senha_hash
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            id=data.get("id", 0),
            nome=data.get("nome", ""),
            email=data.get("email", ""),
            senha_hash=data.get("senha_hash", "")
        )
