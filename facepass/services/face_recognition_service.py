from typing import Optional, List, Tuple
import io
import face_recognition
import numpy as np
from facepass.models.faceEncoding import FaceEncoding
from facepass.database.repository.face_encoding_repository import FaceEncodingRepository


class FaceRecognitionService:
    """Serviço responsável pelo reconhecimento facial"""

    def __init__(self, face_encoding_repository: FaceEncodingRepository):
        self.repository = face_encoding_repository
        self.tolerance = 0.6  # Limiar de similaridade para considerar match

    def generate_face_encoding(self, image_bytes: bytes):
        """Gera o encoding facial a partir de uma imagem"""
        try:
            # Suporte para diferentes tipos de entrada:
            # - bytes/bytearray: dados brutos da imagem
            # - file-like: um objeto com .read()
            # - str: caminho de arquivo
            if isinstance(image_bytes, (bytes, bytearray)):
                image_file = io.BytesIO(image_bytes)
                image = face_recognition.load_image_file(image_file)
            elif hasattr(image_bytes, "read"):
                # file-like object (ex: uploaded file)
                image = face_recognition.load_image_file(image_bytes)
            else:
                # assume path-like (str)
                image = face_recognition.load_image_file(image_bytes)
            
            # Detectar faces na imagem
            face_locations = face_recognition.face_locations(image)
            
            if not face_locations:
                return None  # Nenhum rosto detectado
            
            # Gerar encoding para o primeiro rosto encontrado
            face_encodings = face_recognition.face_encodings(image, face_locations)
            
            if not face_encodings:
                return None
                
            return face_encodings[0]  # Converter numpy array para list
            
        except Exception as e:
            print(f"Erro ao gerar encoding facial: {str(e)}")
            return None
        

    def save_user_face(self, user_id: int, image_bytes: bytes) -> Optional[FaceEncoding]:
        """Gera e salva o encoding facial de um usuário
        
        Retorna Objeto atualizado se sucesso
        Retorna None se houver falha"""
        
        encoding = self.generate_face_encoding(image_bytes)
        
        if encoding is None:
            return None
            
        face_encoding = FaceEncoding(user_id, encoding)
        return self.repository.save_encoding(face_encoding)

    def identify_face(self, image_bytes: bytes) -> Optional[Tuple[int, float]]:
        """
        Identifica um rosto comparando com os encodings salvos
        Retorna uma tupla com (user_id, confidence) ou None se não encontrar match
        """
        # Gerar encoding da imagem fornecida
        unknown_encoding = self.generate_face_encoding(image_bytes)
        if unknown_encoding is None:
            return None
            
        # Buscar todos os encodings salvos
        saved_encodings = self.repository.get_all_encodings()
        if not saved_encodings:
            return None
            
        # Preparar arrays para comparação
        known_encodings = [enc.encoding for enc in saved_encodings]
        known_user_ids = [enc.user_id for enc in saved_encodings]
        
        # Calcular distâncias entre o encoding desconhecido e todos os salvos
        distances = face_recognition.face_distance(known_encodings, unknown_encoding)
        
        # Encontrar o match mais próximo
        best_match_index = np.argmin(distances)
        min_distance = distances[best_match_index]
        
        # Se a distância for menor que o limiar, retorna o user_id e a confiança
        if min_distance <= self.tolerance:
            confidence = 1 - min_distance  # Converter distância em confiança (0-1)
            return (known_user_ids[best_match_index], confidence)
            
        return None

    def verify_face_match(self, user_id: int, image_bytes: bytes) -> Optional[float]:
        """
        Verifica se uma imagem corresponde ao usuário específico
        Retorna o nível de confiança (0-1) ou None se não houver match
        """
        # Gerar encoding da imagem fornecida
        unknown_encoding = self.generate_face_encoding(image_bytes)
        if unknown_encoding is None:
            return None
            
        # Buscar encoding do usuário específico
        saved_encoding = self.repository.get_encoding_by_user_id(user_id)
        if saved_encoding is None:
            return None
            
        # Calcular distância entre os encodings
        distance = face_recognition.face_distance([saved_encoding.encoding], unknown_encoding)[0]
        
        # Se a distância for menor que o limiar, retorna a confiança
        if distance <= self.tolerance:
            return 1 - distance  # Converter distância em confiança (0-1)
            
        return None