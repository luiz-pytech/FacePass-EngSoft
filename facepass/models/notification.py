from datetime import datetime


class Notificacao:
    def __init__(self, id, gestor_id, registro_acesso_id, data_hora, tipo_notificacao, mensagem, lida=False):
        self.id = id
        self.gestor_id = gestor_id
        self.registro_acesso_id = registro_acesso_id
        self.data_hora = data_hora
        self.tipo_notificacao = tipo_notificacao
        self.mensagem = mensagem
        self.lida = lida

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "gestor_id": self.gestor_id,
            "registro_acesso_id": self.registro_acesso_id,
            "data_hora": self.data_hora,
            "tipo_notificacao": self.tipo_notificacao,
            "mensagem": self.mensagem,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data.get("id"),
            gestor_id=data.get("gestor_id"),
            registro_acesso_id=data.get("registro_acesso_id"),
            data_hora=data.get("data_hora"),
            tipo_notificacao=data.get("tipo_notificacao"),
            mensagem=data.get("mensagem"),
        )
