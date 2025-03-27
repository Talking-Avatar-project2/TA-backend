from abc import ABC, abstractmethod

class AvatarRepositoryInterface(ABC):
    @abstractmethod
    def save_animation_log(self, emotion: str):
        pass
