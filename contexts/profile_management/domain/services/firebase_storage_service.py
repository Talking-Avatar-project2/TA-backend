# contexts/profile_management/domain/services/firebase_storage_service.py
import uuid
import os
from datetime import timedelta
from firebase_config import get_storage_bucket


class FirebaseStorageService:
    """Servicio de dominio para gestionar archivos en Firebase Storage"""

    # Configuración
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB
    PROFILE_PHOTOS_PATH = "profile_photos"

    @staticmethod
    def is_allowed_file(filename: str) -> bool:
        """Verifica si el archivo tiene una extensión permitida"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in FirebaseStorageService.ALLOWED_EXTENSIONS

    @staticmethod
    def validate_file_size(file) -> tuple[bool, int]:
        """
        Valida el tamaño del archivo

        Returns:
            tuple: (es_valido, tamaño_en_bytes)
        """
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)  # Volver al inicio

        is_valid = file_size <= FirebaseStorageService.MAX_FILE_SIZE
        return is_valid, file_size

    @staticmethod
    def upload_profile_photo(file, user_id: str, content_type: str) -> str:
        """
        Sube una foto de perfil a Firebase Storage

        Args:
            file: Archivo de imagen (FileStorage de Flask)
            user_id: ID del usuario
            content_type: Tipo MIME del archivo

        Returns:
            str: URL pública de la foto subida

        Raises:
            ValueError: Si el archivo no es válido
            Exception: Si hay error al subir
        """
        # Generar nombre único para el archivo
        file_extension = file.filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{FirebaseStorageService.PROFILE_PHOTOS_PATH}/{user_id}_{uuid.uuid4()}.{file_extension}"

        # Obtener bucket
        bucket = get_storage_bucket()
        blob = bucket.blob(unique_filename)

        # Configurar metadata
        blob.metadata = {
            'user_id': user_id,
            'content_type': content_type
        }

        # Subir el archivo
        blob.upload_from_file(file, content_type=content_type)

        # Hacer el archivo público y obtener URL
        blob.make_public()
        photo_url = blob.public_url

        # Eliminar fotos antiguas del usuario (excepto la nueva)
        FirebaseStorageService._delete_old_user_photos(user_id, unique_filename)

        return photo_url

    @staticmethod
    def delete_user_photos(user_id: str) -> int:
        """
        Elimina todas las fotos de perfil de un usuario

        Args:
            user_id: ID del usuario

        Returns:
            int: Cantidad de archivos eliminados
        """
        bucket = get_storage_bucket()
        blobs = bucket.list_blobs(prefix=f'{FirebaseStorageService.PROFILE_PHOTOS_PATH}/{user_id}_')

        deleted_count = 0
        for blob in blobs:
            blob.delete()
            deleted_count += 1

        return deleted_count

    @staticmethod
    def _delete_old_user_photos(user_id: str, except_filename: str = None):
        """
        Elimina fotos antiguas del usuario (helper interno)

        Args:
            user_id: ID del usuario
            except_filename: Nombre del archivo a excluir (la foto nueva)
        """
        try:
            bucket = get_storage_bucket()
            blobs = bucket.list_blobs(prefix=f'{FirebaseStorageService.PROFILE_PHOTOS_PATH}/{user_id}_')

            for blob in blobs:
                # No eliminar el archivo recién subido
                if except_filename and blob.name == except_filename:
                    continue
                blob.delete()
                print(f"🗑️  Foto antigua eliminada: {blob.name}")
        except Exception as e:
            print(f"⚠️  Error al eliminar fotos antiguas: {e}")

    @staticmethod
    def get_allowed_extensions_str() -> str:
        """Retorna las extensiones permitidas como string"""
        return ", ".join(FirebaseStorageService.ALLOWED_EXTENSIONS)
