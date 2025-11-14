# contexts/avatar_management/domain/services/viseme_mapping_service.py

class VisemeMappingService:
    """
    Mapea fonemas/caracteres a visemas compatibles con el AtlasRenderer.

    NOTA: El atlas usa nombres como: A, E, I, O, U, MBP, FV, L, TH, SH, R, REST
    """

    # Mapeo fonema → visema (nombres del atlas)
    _phoneme_to_viseme = {
        # Vocales
        'a': 'A',
        'á': 'A',
        'e': 'E',
        'é': 'E',
        'i': 'I',
        'í': 'I',
        'o': 'O',
        'ó': 'O',
        'u': 'U',
        'ú': 'U',

        # Bilabiales (cierre de labios)
        'm': 'MBP',
        'b': 'MBP',
        'p': 'MBP',

        # Labiodentales
        'f': 'FV',
        'v': 'FV',

        # Alveolares (lengua en dientes/paladar)
        't': 'TH',
        'd': 'TH',
        's': 'TH',
        'z': 'TH',
        'n': 'TH',
        'l': 'L',
        'r': 'R',

        # Palatales y fricativas
        'sh': 'SH',
        'ch': 'SH',
        'j': 'SH',
        'x': 'SH',

        # Guturales
        'g': 'TH',
        'k': 'TH',

        # Semivocales
        'y': 'I',
        'w': 'U',

        'ñ': 'TH',
        'q': 'TH',
        'ü': 'U',

        # Silencio
        'h': 'REST',
        ' ': 'REST',
        '': 'REST',
    }

    _default_viseme = 'REST'

    @classmethod
    def map_phoneme(cls, phoneme: str) -> str:
        """
        Mapea un fonema/carácter a su visema correspondiente.

        Args:
            phoneme: Carácter o fonema (ej: 'a', 'm', 'sh')

        Returns:
            Nombre del visema (ej: 'A', 'MBP', 'REST')
        """
        p = str(phoneme).lower().strip()
        return cls._phoneme_to_viseme.get(p, cls._default_viseme)

    @staticmethod
    def viseme_ratio(viseme: str) -> float:
        """
        Devuelve el ratio de apertura de labios para cada visema.
        Usado solo en el sistema antiguo de warping (v2.0).
        En v3.0 con atlas, este valor NO se usa.
        """
        table = {
            "A": 0.85,
            "E": 0.60,
            "I": 0.45,
            "O": 0.75,
            "U": 0.55,
            "MBP": 0.30,
            "FV": 0.40,
            "L": 0.50,
            "TH": 0.50,
            "SH": 0.55,
            "R": 0.50,
            "REST": 0.20,
        }
        return table.get(viseme.upper(), 0.35)