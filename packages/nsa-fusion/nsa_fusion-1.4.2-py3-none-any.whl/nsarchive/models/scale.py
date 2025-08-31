class Scale:
    def __init__(self, _data: dict = None):
        self.democratie: float = 0.0
        self.coertition: float = 0.0
        self.liberte: float = 0.0
        self.integration: float = 0.0
        self.ouverture: float = 0.0
        self.diplomatie: float = 0.0
        self.revolution: float = 0.0

        if _data:
            self._load(_data)

    def _load(self, _data: dict):
        self.democratie = _data.get('DEM', 0.0)
        self.coertition = _data.get('SRV', 0.0)
        self.liberte = _data.get('LIB', 0.0)
        self.integration = _data.get('INT', 0.0)
        self.ouverture = _data.get('MDE', 0.0)
        self.diplomatie = _data.get('PAZ', 0.0)
        self.revolution = _data.get('REV', 0.0)

    def _to_dict(self) -> dict:
        return {
            'DEM': self.democratie,
            'SRV': self.coertition,
            'LIB': self.liberte,
            'INT': self.integration,
            'MDE': self.ouverture,
            'PAZ': self.diplomatie,
            'REV': self.revolution
        }

    def calc_score(self) -> float:
        x = sum({
            'DEM': 12 * self.democratie,
            'SRV': 14 * self.coertition,
            'LIB': 14 * self.liberte,
            'INT': 20 * self.integration,
            'MDE': 12 * self.ouverture, # Ouverture au monde
            'PAZ': 10 * self.diplomatie, # Paix (dans le sens évitement de la guerre)
            'REV': 18 * self.revolution
        }.values())

        return round(x / 40, 2)


REFERENCE = {
    "Anarchie": Scale({
        "DEM": 40,
        "SRV": 40,
        "LIB": 40,
        "INT": 40,
        "MDE": 40,
        "PAZ": 40,
        "REV": 40
    }),
    "Révolution": Scale({
        "DEM": 40,
        "SRV": 25,
        "LIB": 35,
        "INT": 36,
        "MDE": 40,
        "PAZ": 40,
        "REV": 25
    }),
    "Passivité": Scale({
        "DEM": 35,
        "SRV": 10,
        "LIB": 36,
        "INT": 32,
        "MDE": 40,
        "PAZ": 40,
        "REV": 7
    }),
    "Insurrection": Scale({
        "DEM": 30,
        "SRV": 8,
        "LIB": 32,
        "INT": 10,
        "MDE": 20,
        "PAZ": 30,
        "REV": 7
    }),
    "Taoxisme": Scale({
        "DEM": 10,
        "SRV": 5,
        "LIB": 28,
        "INT": 12,
        "MDE": 20,
        "PAZ": 20,
        "REV": 5
    }),
    "Dictature": Scale()
}

def get_positions(score: Scale, ref: dict[str, Scale] = REFERENCE) -> list[str]:
    dist = sorted(
        ref.items(),
        key = lambda r : abs(r[1].calc_score() - score.calc_score())
    )

    items = []

    for item in dist:
        if abs(item[1].calc_score() - score.calc_score()) < 15:
            items.append(item[0])

    return items