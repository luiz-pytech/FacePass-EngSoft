from typing import Optional
import io
import numpy as np

class FaceEncoding:
    """Modelo responsável por representar o vetor de distâncias do rosto do usuário"""
    def __init__(self, user_id: int, encoding, id: Optional[int] = None):
        self.id: Optional[int] = id
        self.user_id: int = user_id
        self.encoding = encoding

    def to_bytes(self) -> bytes:
        """converte o encoding para bytes para armazenamento"""

        buffer = io.BytesIO()
        np.save(buffer, self.encoding, allow_pickle=False)
        return buffer.getvalue()
    
    @classmethod
    def from_bytes(cls, data: bytes) -> np.ndarray:
        """Reconstrói o encoding a partir dos bytes"""
        
        buffer = io.BytesIO(data)
        return np.load(buffer, allow_pickle=False)