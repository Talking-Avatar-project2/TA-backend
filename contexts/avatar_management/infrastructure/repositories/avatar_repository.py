from contexts.avatar_management.domain.repositories.avatar_repository_interface import AvatarRepositoryInterface
from contexts.avatar_management.infrastructure.adapters.avatar_adapter import AvatarAdapter

class AvatarRepository(AvatarRepositoryInterface):
    @staticmethod
    def save_animation_log(emotion: str):
        """
        Guarda un registro de la animación del avatar en el almacenamiento definido.
        :param emotion: Emoción animada.
        """
        AvatarAdapter.save_log(emotion)
