from typing import Optional
import datetime


class Usuario:
    def __init__(self, id: int, nome: str, email: str, cpf: str, foto_reconhecimento: bytes):
        self.id: int = id
        self.nome: str = nome
        self.email: str = email
        self.cpf: str = cpf
        self.data_cadastro: datetime.datetime = datetime.datetime.now()
        self.foto_reconhecimento: bytes = foto_reconhecimento
        self.cargo: str = ""
        self.aprovado: bool = False

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "nome": self.nome,
            "email": self.email,
            "cpf": self.cpf,
            "data_cadastro": self.data_cadastro.isoformat(),
            "foto_reconhecimento": self.foto_reconhecimento,
            "cargo": self.cargo,
            "aprovado": self.aprovado,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data.get("id"),
            nome=data.get("nome"),
            email=data.get("email"),
            cpf=data.get("cpf"),
            foto_reconhecimento=data.get("foto_reconhecimento"),
        )
