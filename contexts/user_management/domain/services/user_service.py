# contexts/user_management/domain/services/user_service.py
from typing import Optional
from datetime import datetime
from contexts.user_management.domain.entities.user import User
from contexts.user_management.infrastructure.repositories.firestore_user_repository import FirestoreUserRepository


class UserService:
    """Servicio de dominio para gestionar usuarios"""

    def __init__(self):
        self.repository = FirestoreUserRepository()

    def create_user_profile(self, user_id: str, email: str, full_name: str,
                           birth_date: datetime, photo_url: Optional[str] = None) -> User:
        """
        Crea un nuevo perfil de usuario en Firestore

        Este método se llama después de que Firebase Auth crea el usuario

        Args:
            user_id: UID de Firebase Auth
            email: Email del usuario
            full_name: Nombre completo
            birth_date: Fecha de nacimiento
            photo_url: URL de foto de perfil (opcional)

        Returns:
            User: Usuario creado

        Raises:
            ValueError: Si el usuario ya existe
        """
        # Verificar que no exista
        if self.repository.exists(user_id):
            raise ValueError(f"Usuario {user_id} ya tiene un perfil")

        # Crear entidad
        user = User(
            user_id=user_id,
            email=email,
            full_name=full_name,
            birth_date=birth_date,
            photo_url=photo_url,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        # Guardar en Firestore
        return self.repository.create(user)

    def get_user_profile(self, user_id: str) -> Optional[User]:
        """
        Obtiene el perfil de un usuario

        Args:
            user_id: ID del usuario

        Returns:
            User si existe, None si no
        """
        return self.repository.get_by_id(user_id)

    def update_user_profile(self, user_id: str, full_name: Optional[str] = None,
                           birth_date: Optional[datetime] = None,
                           photo_url: Optional[str] = None) -> User:
        """
        Actualiza el perfil de un usuario

        Args:
            user_id: ID del usuario
            full_name: Nuevo nombre (opcional)
            birth_date: Nueva fecha de nacimiento (opcional)
            photo_url: Nueva URL de foto (opcional)

        Returns:
            User: Usuario actualizado

        Raises:
            ValueError: Si el usuario no existe
        """
        # Obtener usuario actual
        user = self.repository.get_by_id(user_id)
        if not user:
            raise ValueError(f"Usuario {user_id} no existe")

        # Actualizar campos
        user.update_profile(full_name, birth_date, photo_url)

        # Guardar cambios
        return self.repository.update(user)

    def update_photo_url(self, user_id: str, photo_url: str) -> bool:
        """
        Actualiza solo la URL de la foto de perfil

        Args:
            user_id: ID del usuario
            photo_url: Nueva URL de la foto

        Returns:
            bool: True si se actualizó, False si el usuario no existe
        """
        return self.repository.update_photo_url(user_id, photo_url)

    def delete_user_profile(self, user_id: str) -> bool:
        """
        Elimina el perfil de un usuario de Firestore

        Nota: Esto NO elimina el usuario de Firebase Auth

        Args:
            user_id: ID del usuario

        Returns:
            bool: True si se eliminó, False si no existía
        """
        return self.repository.delete(user_id)

    def user_exists(self, user_id: str) -> bool:
        """
        Verifica si un usuario tiene perfil

        Args:
            user_id: ID del usuario

        Returns:
            bool: True si existe, False si no
        """
        return self.repository.exists(user_id)
