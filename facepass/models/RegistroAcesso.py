import datetime

class RegistroAcesso:
    "Classe que representa registros de acesso no sistema."
    def __init__ (self):
        self.id: int = None
        self.usuario_id: int = None
        self.data_hora: datetime.datetime = None
        self.tipo_acesso: str = None 
        self.acesso_permitido: bool = False
        self.confianca_reconhecimento: float = None
        self.motivo_negacao: str = None
        self.imagem_capturada: bytes = None