# tests/utils/viseme_input_simulator.py

import json
import os
from contexts.avatar_management.application.use_cases.generate_viseme_sequence_use_case import TimedViseme


class VisemeInputSimulator:
    @staticmethod
    def load_from_json(json_path: str) -> list[TimedViseme]:
        """
        Carga visemas temporizados desde un archivo .json simulado.
        Cada entrada debe tener: viseme, start_time, duration
        """
        with open(json_path, 'r') as file:
            data = json.load(file)

        sequence = []
        for item in data:
            sequence.append(TimedViseme(
                viseme=item['viseme'],
                start_time=item['start_time'],
                duration=item['duration']
            ))
        return sequence
