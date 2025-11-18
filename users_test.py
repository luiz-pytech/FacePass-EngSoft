import pytest
import datetime
from users import Usuario  

class TestUsuario:
    """Testes para a classe Usuario"""

    def test_init(self):
        """Testa o método construtor __init__"""
        # Arrange
        user_data = {
            "id": 1,
            "name": "Caio Silva",
            "email": "caio@email.com", 
            "cpf": "123.456.789-00",
            "photo_recognition": b"fake_photo_data",
            "position": "Developer"
        }
        
        # Act
        usuario = Usuario(**user_data)
        
        # Assert
        assert usuario.id == 1
        assert usuario.name == "Caio Silva"
        assert usuario.email == "caio@email.com"
        assert usuario.cpf == "123.456.789-00"
        assert usuario.photo_recognition == b"fake_photo_data"
        assert usuario.position == "Developer"
        assert usuario.approved is False
        assert isinstance(usuario.created_at, datetime.datetime)

    def test_to_dict(self):
        """Testa APENAS o método to_dict()"""
        # Arrange
        usuario = Usuario(
            id=1,
            name="Maria Santos",
            email="maria@email.com",
            cpf="999.888.777-66", 
            photo_recognition=b"photo_bytes",
            position="Manager"
        )
        
        # Act
        result = usuario.to_dict()
        
        # Assert
        assert result["id"] == 1
        assert result["name"] == "Maria Santos"
        assert result["email"] == "maria@email.com"
        assert result["cpf"] == "999.888.777-66"
        assert result["photo_recognition"] == b"photo_bytes"
        assert result["position"] == "Manager"
        assert result["approved"] is False
        assert isinstance(result["created_at"], str)

    def test_from_dict(self):
        """Testa APENAS o método from_dict()"""
        # Arrange
        data = {
            "id": 1,
            "name": "Carlos Oliveira",
            "email": "carlos@email.com",
            "cpf": "555.444.333-22",
            "photo_recognition": b"original_photo",
            "position": "Analyst",
            "approved": True
        }
        
        # Act
        usuario = Usuario.from_dict(data)
        
        # Assert
        assert usuario.id == 1
        assert usuario.name == "Carlos Oliveira"
        assert usuario.email == "carlos@email.com"
        assert usuario.cpf == "555.444.333-22"
        assert usuario.photo_recognition == b"original_photo"
        assert usuario.position == "Analyst"
        assert usuario.approved is True