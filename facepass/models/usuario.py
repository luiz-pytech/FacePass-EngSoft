from typing import Optional
class Usuario:
    "Classe que representa usuários do sistema."
    def __init__ (self):
        self.id: int = None
        self.nome: str = None
        self.email: str = None
        self.cpf: str = None
        self.foto_reconhecimento: Optional[bytes] = None
        self.aprovado: bool = False
        self.ativo: bool = False
        self.cargo: str =  None

    