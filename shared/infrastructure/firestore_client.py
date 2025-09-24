import requests
import json
import os
from google.auth.transport.requests import Request
from google.oauth2 import service_account
from datetime import datetime

class FirestoreClient:
    def __init__(self):
        self.project_id = None
        self.access_token = None
        self._initialize_auth()
    
    def _initialize_auth(self):
        """Inicializa la autenticación con Google Cloud."""
        cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH", "firebase-credentials.json")
        
        if not os.path.exists(cred_path):
            raise FileNotFoundError(f"Archivo de credenciales no encontrado: {cred_path}")
        
        # Cargar credenciales
        with open(cred_path, 'r') as f:
            cred_data = json.load(f)
        
        self.project_id = cred_data['project_id']
        
        # Crear credenciales de servicio
        credentials = service_account.Credentials.from_service_account_file(
            cred_path,
            scopes=['https://www.googleapis.com/auth/datastore']
        )
        
        # Obtener token de acceso
        credentials.refresh(Request())
        self.access_token = credentials.token
    
    def _get_headers(self):
        """Obtiene headers para las peticiones."""
        return {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
    
    def add_document(self, collection_path, data):
        """
        Agrega un documento a una colección.
        :param collection_path: Ruta de la colección (ej: 'users/user123/conversations')
        :param data: Datos del documento
        :return: ID del documento creado
        """
        url = f'https://firestore.googleapis.com/v1/projects/{self.project_id}/databases/(default)/documents/{collection_path}'
        
        # Convertir datos al formato de Firestore
        firestore_data = self._convert_to_firestore_format(data)
        
        response = requests.post(url, headers=self._get_headers(), json={'fields': firestore_data})
        
        if response.status_code == 200:
            result = response.json()
            doc_id = result['name'].split('/')[-1]
            return doc_id
        else:
            raise Exception(f"Error creando documento: {response.text}")
    
    def get_documents(self, collection_path, order_by=None, limit=None):
        """
        Obtiene documentos de una colección.
        :param collection_path: Ruta de la colección
        :param order_by: Campo para ordenar (opcional)
        :param limit: Límite de documentos (opcional)
        :return: Lista de documentos
        """
        url = f'https://firestore.googleapis.com/v1/projects/{self.project_id}/databases/(default)/documents/{collection_path}'
        
        params = {}
        if order_by:
            params['orderBy'] = f'{order_by} desc'
        if limit:
            params['pageSize'] = limit
        
        response = requests.get(url, headers=self._get_headers(), params=params)
        
        if response.status_code == 200:
            result = response.json()
            documents = result.get('documents', [])
            return [self._convert_from_firestore_format(doc) for doc in documents]
        else:
            raise Exception(f"Error obteniendo documentos: {response.text}")
    
    def _convert_to_firestore_format(self, data):
        """Convierte datos Python al formato de Firestore."""
        firestore_data = {}
        
        for key, value in data.items():
            if isinstance(value, str):
                firestore_data[key] = {'stringValue': value}
            elif isinstance(value, int):
                firestore_data[key] = {'integerValue': str(value)}
            elif isinstance(value, datetime):
                firestore_data[key] = {'timestampValue': value.isoformat() + 'Z'}
            elif isinstance(value, bool):
                firestore_data[key] = {'booleanValue': value}
        
        return firestore_data
    
    def _convert_from_firestore_format(self, doc):
        """Convierte documento de Firestore a formato Python."""
        data = {'_id': doc['name'].split('/')[-1]}
        
        for key, value in doc.get('fields', {}).items():
            if 'stringValue' in value:
                data[key] = value['stringValue']
            elif 'integerValue' in value:
                data[key] = int(value['integerValue'])
            elif 'timestampValue' in value:
                data[key] = datetime.fromisoformat(value['timestampValue'].replace('Z', '+00:00'))
            elif 'booleanValue' in value:
                data[key] = value['booleanValue']
        
        return data