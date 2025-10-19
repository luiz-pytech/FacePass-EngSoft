import datetime
from typing import Optional


class RegistroAcesso:
    def __init__(self, id: int, usuario_id: int, data_hora: datetime.datetime, tipo_acesso: str, acesso_permitido: bool):
        self.id: int = id
        self.usuario_id: int = usuario_id
        self.data_hora: datetime.datetime = data_hora
        self.tipo_acesso: str = tipo_acesso
        self.acesso_permitido: bool = acesso_permitido
        self.motivo_negacao: Optional[str] = None
        self.imagem_capturada: Optional[bytes] = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "usuario_id": self.usuario_id,
            "data_hora": self.data_hora.isoformat(),
            "tipo_acesso": self.tipo_acesso,
            "acesso_permitido": self.acesso_permitido,
            "motivo_negacao": self.motivo_negacao,
            "imagem_capturada": self.imagem_capturada,
        }
