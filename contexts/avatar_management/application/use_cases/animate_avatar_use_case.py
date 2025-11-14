# contexts/avatar_management/application/use_cases/animate_avatar_use_case.py
from contexts.avatar_management.domain.services.avatar_animation_service import AvatarAnimationService
from contexts.avatar_management.infrastructure.repositories.avatar_repository import AvatarRepository

class AnimateAvatarUseCase:
    @staticmethod
    def execute(emotion: str) -> dict:
        animation_result = AvatarAnimationService.animate(emotion)
        if animation_result["success"]:
            AvatarRepository.save_animation_log(emotion)
            return {"message": f"Avatar animado con éxito para la emoción: {emotion}"}
        return {"error": animation_result["error"]}
