"""Tests d'intégration pour l'API du Triangulator."""

import struct
import uuid
from unittest.mock import Mock, patch

import pytest
import requests
from app import app


@pytest.fixture
def client():
    """Fixture pour créer un client de test."""
    with app.test_client() as client:
        yield client

def test_get_triangulation_success(client):
    """Test le cas nominal (happy path) de l'endpoint de triangulation."""
    # Création d'un UUID valide
    valid_uuid = str(uuid.uuid4())
    
    # Mock des données de test (3 points formant un triangle)
    test_data = struct.pack('<L', 3)  # 3 points
    test_data += struct.pack('<ff', 0.0, 0.0)  # (0,0)
    test_data += struct.pack('<ff', 1.0, 0.0)  # (1,0)
    test_data += struct.pack('<ff', 0.0, 1.0)  # (0,1)
    
    # Simulation de la réponse du PointSetManager
    with patch('app.requests.get') as mock_get:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = test_data
        mock_get.return_value = mock_response
        
        # Appel de l'endpoint
        response = client.get(f'/triangulation/{valid_uuid}')
        
        # Vérifications
        assert response.status_code == 200
        assert response.mimetype == 'application/octet-stream'
        
        # Vérifier le format des triangles dans la réponse
        binary_data = response.data
        num_points = struct.unpack('<L', binary_data[:4])[0]
        assert num_points == 3
        
        # Vérifier qu'il y a au moins un triangle
        offset = 4 + (num_points * 8)
        num_triangles = struct.unpack('<L', binary_data[offset:offset+4])[0]
        assert num_triangles >= 1

def test_get_triangulation_invalid_uuid(client):
    """Test avec un UUID invalide."""
    response = client.get('/triangulation/not-a-uuid')
    assert response.status_code == 400
    assert response.is_json
    assert response.json['code'] == 'BAD_REQUEST'

def test_get_triangulation_manager_404(client):
    """Test quand le PointSetManager répond 404."""
    valid_uuid = str(uuid.uuid4())
    
    with patch('app.requests.get') as mock_get:
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        response = client.get(f'/triangulation/{valid_uuid}')
        assert response.status_code == 404
        assert response.is_json
        assert response.json['code'] == 'NOT_FOUND'

def test_get_triangulation_manager_503(client):
    """Test quand le PointSetManager est indisponible."""
    valid_uuid = str(uuid.uuid4())
    
    with patch('app.requests.get') as mock_get:
        mock_get.side_effect = requests.exceptions.ConnectionError()
        
        response = client.get(f'/triangulation/{valid_uuid}')
        assert response.status_code == 503
        assert response.is_json
        assert response.json['code'] == 'SERVICE_UNAVAILABLE'

def test_get_triangulation_manager_400(client):
    """Test quand le PointSetManager répond 400."""
    valid_uuid = str(uuid.uuid4())
    
    with patch('app.requests.get') as mock_get:
        mock_response = Mock()
        mock_response.status_code = 400
        mock_get.return_value = mock_response
        
        response = client.get(f'/triangulation/{valid_uuid}')
        assert response.status_code == 400
        assert response.is_json
        assert response.json['code'] == 'BAD_REQUEST'

def test_get_triangulation_manager_500(client):
    """Test quand le PointSetManager répond 500."""
    valid_uuid = str(uuid.uuid4())
    
    with patch('app.requests.get') as mock_get:
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response
        
        response = client.get(f'/triangulation/{valid_uuid}')
        assert response.status_code == 503
        assert response.is_json
        assert response.json['code'] == 'SERVICE_UNAVAILABLE'

def test_get_triangulation_timeout(client):
    """Test quand le PointSetManager timeout."""
    valid_uuid = str(uuid.uuid4())
    
    with patch('app.requests.get') as mock_get:
        mock_get.side_effect = requests.exceptions.Timeout()
        
        response = client.get(f'/triangulation/{valid_uuid}')
        assert response.status_code == 503
        assert response.is_json
        assert response.json['code'] == 'SERVICE_UNAVAILABLE'

def test_get_triangulation_request_exception(client):
    """Test quand une RequestException autre que ConnectionError/Timeout."""
    valid_uuid = str(uuid.uuid4())
    
    with patch('app.requests.get') as mock_get:
        mock_get.side_effect = requests.exceptions.RequestException("Erreur générique")
        
        response = client.get(f'/triangulation/{valid_uuid}')
        assert response.status_code == 503
        assert response.is_json
        assert response.json['code'] == 'SERVICE_UNAVAILABLE'

def test_get_triangulation_parse_error(client):
    """Test quand le parsing du PointSet échoue."""
    valid_uuid = str(uuid.uuid4())
    
    # Données binaires invalides
    invalid_data = b'invalid binary data'
    
    with patch('app.requests.get') as mock_get:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = invalid_data
        mock_get.return_value = mock_response
        
        response = client.get(f'/triangulation/{valid_uuid}')
        assert response.status_code == 500
        assert response.is_json
        assert response.json['code'] == 'INTERNAL_ERROR'

def test_get_triangulation_value_error(client):
    """Test quand la triangulation lève une ValueError."""
    valid_uuid = str(uuid.uuid4())
    
    # Données valides mais qui causeront une ValueError (points dupliqués)
    test_data = struct.pack('<L', 3)  # 3 points
    test_data += struct.pack('<ff', 0.0, 0.0)
    test_data += struct.pack('<ff', 0.0, 0.0)  # Point dupliqué
    test_data += struct.pack('<ff', 1.0, 1.0)
    
    with patch('app.requests.get') as mock_get:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = test_data
        mock_get.return_value = mock_response
        
        response = client.get(f'/triangulation/{valid_uuid}')
        assert response.status_code == 500
        assert response.is_json
        assert response.json['code'] == 'INTERNAL_ERROR'

def test_get_triangulation_serialization_error(client):
    """Test quand la sérialisation échoue."""
    valid_uuid = str(uuid.uuid4())
    
    test_data = struct.pack('<L', 3)  # 3 points
    test_data += struct.pack('<ff', 0.0, 0.0)
    test_data += struct.pack('<ff', 1.0, 0.0)
    test_data += struct.pack('<ff', 0.0, 1.0)
    
    with patch('app.requests.get') as mock_get:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = test_data
        mock_get.return_value = mock_response
        
        # Mock de la sérialisation pour lever une ValueError
        with patch('app.serialize_triangles_binary') as mock_serialize:
            mock_serialize.side_effect = ValueError("Erreur sérialisation")
            
            response = client.get(f'/triangulation/{valid_uuid}')
            assert response.status_code == 500
            assert response.is_json
            assert response.json['code'] == 'INTERNAL_ERROR'

def test_get_triangulation_internal_error(client):
    """Test d'une erreur interne lors de la triangulation."""
    valid_uuid = str(uuid.uuid4())
    
    # Simulation d'une réponse valide du PointSetManager
    test_data = struct.pack('<L', 3)  # 3 points
    test_data += struct.pack('<ff', 0.0, 0.0)
    test_data += struct.pack('<ff', 1.0, 0.0)
    test_data += struct.pack('<ff', 0.0, 1.0)
    
    with patch('app.requests.get') as mock_get:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = test_data
        mock_get.return_value = mock_response
        
        # Simulation d'une erreur dans l'algorithme
        with patch('app.compute_triangulation') as mock_compute:
            mock_compute.side_effect = Exception("Erreur calcul")
            
            response = client.get(f'/triangulation/{valid_uuid}')
            assert response.status_code == 500
            assert response.is_json
            assert response.json['code'] == 'INTERNAL_ERROR'

def test_not_implemented_error_handler(client):
    """Test du handler NotImplementedError."""
    # On force une NotImplementedError via un mock
    with patch('app.get_triangulation') as mock_endpoint:
        mock_endpoint.side_effect = NotImplementedError("Test")
        
        # On appelle directement le handler via Flask
        from werkzeug.exceptions import InternalServerError
        
        # Simuler une erreur NotImplementedError
        with app.test_request_context('/triangulation/test-uuid'):
            from app import not_implemented
            error = InternalServerError()
            error.original_exception = NotImplementedError("Test")
            response = not_implemented(error)
            
            assert response[1] == 500
            data = response[0].get_json()
            assert data['code'] == 'NOT_IMPLEMENTED'