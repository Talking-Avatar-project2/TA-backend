from contexts.avatar_management.domain.services.avatar_animation_service import AvatarAnimationService
from contexts.avatar_management.infrastructure.repositories.avatar_repository import AvatarRepository

class AnimateAvatarUseCase:
    @staticmethod
    def execute(emotion: str) -> dict:
        """
        Ejecuta la animación del avatar basada en la emoción detectada.
        :param emotion: Emoción detectada.
        :return: Mensaje de confirmación o error.
        """
        animation_result = AvatarAnimationService.animate(emotion)
        if animation_result["success"]:
            AvatarRepository.save_animation_log(emotion)  # Guarda la animación en el repositorio
            return {"message": f"Avatar animado con éxito para la emoción: {emotion}"}
        return {"error": animation_result["error"]}
