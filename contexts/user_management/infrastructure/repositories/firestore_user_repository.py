# contexts/user_management/infrastructure/repositories/firestore_user_repository.py
from typing import Optional
from datetime import datetime
from firebase_admin import firestore
from contexts.user_management.domain.entities.user import User


class FirestoreUserRepository:
    """Repositorio para gestionar usuarios en Firestore"""

    COLLECTION_NAME = 'users'

    def __init__(self):
        self.db = firestore.client()

    def create(self, user: User) -> User:
        """
        Crea un nuevo usuario en Firestore

        Args:
            user: Entidad User a crear

        Returns:
            User: Usuario creado

        Raises:
            Exception: Si hay error al crear
        """
        user_ref = self.db.collection(self.COLLECTION_NAME).document(user.user_id)

        # Preparar datos
        user_data = user.to_dict()

        # Guardar en Firestore
        user_ref.set(user_data)

        return user

    def get_by_id(self, user_id: str) -> Optional[User]:
        """
        Obtiene un usuario por su ID

        Args:
            user_id: ID del usuario

        Returns:
            User si existe, None si no
        """
        user_ref = self.db.collection(self.COLLECTION_NAME).document(user_id)
        doc = user_ref.get()

        if not doc.exists:
            return None

        return User.from_dict(user_id, doc.to_dict())

    def update(self, user: User) -> User:
        """
        Actualiza un usuario existente

        Args:
            user: Entidad User con datos actualizados

        Returns:
            User: Usuario actualizado

        Raises:
            Exception: Si el usuario no existe o hay error
        """
        user_ref = self.db.collection(self.COLLECTION_NAME).document(user.user_id)

        # Verificar que existe
        if not user_ref.get().exists:
            raise ValueError(f"Usuario {user.user_id} no existe")

        # Actualizar
        user_data = user.to_dict()
        user_ref.update(user_data)

        return user

    def delete(self, user_id: str) -> bool:
        """
        Elimina un usuario

        Args:
            user_id: ID del usuario a eliminar

        Returns:
            bool: True si se eliminó, False si no existía
        """
        user_ref = self.db.collection(self.COLLECTION_NAME).document(user_id)

        if not user_ref.get().exists:
            return False

        user_ref.delete()
        return True

    def exists(self, user_id: str) -> bool:
        """
        Verifica si un usuario existe

        Args:
            user_id: ID del usuario

        Returns:
            bool: True si existe, False si no
        """
        user_ref = self.db.collection(self.COLLECTION_NAME).document(user_id)
        return user_ref.get().exists

    def update_photo_url(self, user_id: str, photo_url: str) -> bool:
        """
        Actualiza solo la URL de la foto de perfil

        Args:
            user_id: ID del usuario
            photo_url: Nueva URL de la foto

        Returns:
            bool: True si se actualizó, False si el usuario no existe
        """
        user_ref = self.db.collection(self.COLLECTION_NAME).document(user_id)

        if not user_ref.get().exists:
            return False

        user_ref.update({
            'photo_url': photo_url,
            'updated_at': datetime.utcnow()
        })

        return True
