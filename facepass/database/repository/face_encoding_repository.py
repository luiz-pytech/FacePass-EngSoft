from typing import Optional, List, Any
from facepass.models.faceEncoding import FaceEncoding
from facepass.database.setup_database.executor_query import QueryExecutor


class FaceEncodingRepository:
    def __init__(self, connection):
        self.connection = connection
        self.executor = QueryExecutor(connection)

    def save_encoding(self, face_encoding: FaceEncoding) -> FaceEncoding:
        """Armazena o encoding no Banco de Dados"""

        query = """
            INSERT INTO face_encoding (user_id, encoding)
            VALUES (%s, %s);
        """

        params = (face_encoding.user_id, face_encoding.to_bytes())

        encoding_id = self.executor.execute_insert(query, params)
        face_encoding.id = encoding_id

        return face_encoding
    
    def get_encoding_by_user_id(self, user_id: int) -> Optional[FaceEncoding]:
        query = """
            SELECT id, user_id, encoding
            FROM face_encoding
            WHERE user_id = %s;
        """
        params = (user_id,)
        result = self.executor.execute_query(query, params)
        
        if result and len(result) > 0:
            row = result[0]
            encoding_array = FaceEncoding.from_bytes(row['encoding'])
            return FaceEncoding(
                id=row['id'],
                user_id=row['user_id'],
                encoding=encoding_array
            )
        return None
    
    def get_all_encodings(self) -> List[FaceEncoding]:
        query = """
            SELECT id, user_id, encoding
            FROM face_encoding;
        """
        result = self.executor.execute_query(query)
        
        encodings = []
        for row in result:
            encoding_array = FaceEncoding.from_bytes(row['encoding'])
            encoding = FaceEncoding(
                id=row['id'],
                user_id=row['user_id'],
                encoding=encoding_array
            )
            encodings.append(encoding)
        
        return encodings