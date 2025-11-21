# contexts/user_management/domain/entities/user.py
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class User:
    """Entidad de dominio que representa un usuario del sistema"""

    user_id: str  # UID de Firebase Authentication
    email: str
    full_name: str
    birth_date: datetime
    photo_url: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def to_dict(self) -> dict:
        """Convierte la entidad a diccionario para Firestore"""
        return {
            'email': self.email,
            'full_name': self.full_name,
            'birth_date': self.birth_date,
            'photo_url': self.photo_url,
            'created_at': self.created_at or datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }

    @staticmethod
    def from_dict(user_id: str, data: dict) -> 'User':
        """Crea una entidad User desde un diccionario de Firestore"""
        return User(
            user_id=user_id,
            email=data.get('email', ''),
            full_name=data.get('full_name', ''),
            birth_date=data.get('birth_date'),
            photo_url=data.get('photo_url'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )

    def update_profile(self, full_name: Optional[str] = None,
                      birth_date: Optional[datetime] = None,
                      photo_url: Optional[str] = None) -> None:
        """Actualiza los datos del perfil del usuario"""
        if full_name is not None:
            self.full_name = full_name
        if birth_date is not None:
            self.birth_date = birth_date
        if photo_url is not None:
            self.photo_url = photo_url
        self.updated_at = datetime.utcnow()
