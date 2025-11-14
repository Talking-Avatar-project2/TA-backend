import os
import json

class AvatarAdapter:
    LOG_FILE = "contexts/avatar-management/infrastructure/repositories/avatar_animation_log.json"

    @staticmethod
    def save_log(emotion: str):
        """
        Guarda en un archivo JSON el registro de la animación del avatar.
        :param emotion: Emoción que se animó.
        """
        log_entry = {"emotion": emotion}

        if not os.path.exists(AvatarAdapter.LOG_FILE):
            with open(AvatarAdapter.LOG_FILE, "w") as file:
                json.dump([], file)

        with open(AvatarAdapter.LOG_FILE, "r") as file:
            data = json.load(file)

        data.append(log_entry)
        with open(AvatarAdapter.LOG_FILE, "w") as file:
            json.dump(data, file, indent=4)
