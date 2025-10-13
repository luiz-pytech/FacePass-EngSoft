class Usuario:
    "Classe que representa usuários do sistema."
    id: int = None
    nome: str = None
    email: str = None
    cpf: str = None
    foto_reconhecimento: Optional[bytes] = None
    aprovado: bool = False
    ativo: bool = False
    cargo: str =  None

    