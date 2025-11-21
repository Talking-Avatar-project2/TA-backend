import pytest
import sys
import os

# Agregar la raíz del proyecto al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@pytest.fixture
def mock_firestore_client():
    """Mock del cliente Firestore para pruebas."""
    class MockFirestoreClient:
        def __init__(self):
            self.documents = []
        
        def add_document(self, collection_path, data):
            doc_id = f"mock_doc_{len(self.documents)}"
            doc = {
                'name': f"{collection_path}/{doc_id}",
                'fields': self._convert_to_firestore_format(data)
            }
            self.documents.append(doc)
            return doc_id
        
        def get_documents(self, collection_path, order_by=None, limit=None):
            # Simular respuesta de Firestore
            return self.documents[-limit:] if limit else self.documents
        
        def _convert_to_firestore_format(self, data):
            firestore_data = {}
            for key, value in data.items():
                if isinstance(value, str):
                    firestore_data[key] = {'stringValue': value}
                elif isinstance(value, int):
                    firestore_data[key] = {'integerValue': str(value)}
            return firestore_data
    
    return MockFirestoreClient()

@pytest.fixture
def sample_messages():
    """Mensajes de muestra para las pruebas."""
    return {
        'positive_clear': "Estoy muy feliz hoy, todo me está saliendo genial",
        'negative_clear': "Estoy triste, me siento muy mal",
        'ambiguous': "Hoy es un día...",
        'mixed_emotions': "Me siento feliz pero a la vez estresado",
        'neutral': "¿Cómo funciona el clima?",
        'anxious': "Tengo mucha ansiedad por el examen de mañana",
        'excited': "¡No puedo esperar a ver a mis amigos!"
    }