from __future__ import annotations

import json
import time

from .base import NSID
from .scale import Scale
from .. import database as db


class VoteOption:
    """
    Option disponible lors d'un vote

    ## Attributs
    - title: `str`\n
        Label de l'option
    - count: `int`\n
        Nombre de sympathisants pour cette option
    """

    def __init__(self, title: str):
        self.title: str = title
        self.count: int = 0
        self.voters: list = []

    def __repr__(self) -> dict:
        return json.dumps(self.__dict__)

    def _load(self, _data: dict):
        self.title = str(_data['title'])
        self.count = int(_data['count'])
        self.voters = list(map(NSID, _data['voters']))

class Vote:
    """
    Classe de référence pour les différents votes du serveur

    ## Attributs
    - id: `NSID`\n
        Identifiant du vote
    - title: `str`\n
        Titre du vote
    - author: `NSID`\n
        Identifiant de l'auteur du vote
    - type: `str`\n
        Type du vote (`normal`, `partial`, `full`, `2pos`, `3pos`)
    - majority: `int` de 50 à 100 inclus\n
        Pourcentage nécessaire pour qu'une option soit retenue
    - min_choices: `int`\n
        Nombre minimum de choix possibles
    - max_choices: `int`\n
        Nombre maximum de choix possibles
    - start_date: `int`\n
        Date de début du vote
    - end_date: `int`\n
        Date limite pour voter
    - options: dict[str, .VoteOption]\n
        Liste des choix disponibles
    """

    def __init__(self, id: NSID = None) -> None:
        self._path: str = ''

        self.id: NSID = id if id else NSID(0)
        self.title: str = ""
        self.author: NSID = NSID(0)

        self.anonymous: bool = True
        self.type: str = 'normal'
        
        """
        ## Types de vote

        - Vote normal: `normal`
        - Législatives: `partial`
        - Présidentielles: `full`
        - Pour/Contre: `2pos`
        - Pour/Contre/Blanc: `3pos`
        """

        self.min_choices: int = 1
        self.max_choices: int = 1
        self.majority: int = 50 # Entre 50% et 100% inclus

        self.start_date: int = round(time.time())
        self.end_date: int = 0
        self.voters: list[NSID] = []

        self.options: dict[str, VoteOption] = {}

    def _load(self, _data: dict, path: str) -> None:
        self._path = path

        self.id = NSID(_data['id'])
        self.title = _data['title']
        self.author = NSID(_data['author'])

        self.anonymous = _data['anonymous']
        self.type = _data['type']

        self.max_choices = _data['max_choices']
        self.min_choices = _data['min_choices']
        self.majority = _data['majority']

        self.start_date = _data['start']
        self.end_date = _data['end']
        self.voters = list(map(NSID, _data['voters']))

        self.options = {}

        for _opt_id, opt in _data['options'].items():
            option = VoteOption(opt['title'])
            option._load(opt)

            self.options[_opt_id] = option

    def _to_dict(self) -> dict:
        if self.anonymous:
            for opt in self.options.values():
                opt.voters.clear()

        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'anonymous': self.anonymous,
            'type': self.type,
            'min_choices': self.min_choices,
            'max_choices': self.max_choices,
            'majority': self.majority,
            'start': self.start_date,
            'end': self.end_date,
            'voters': list(map(str, self.voters)),
            'options': { id: opt.__dict__ for id, opt in self.options.items() }
        }

    def save(self):
        db.put_item(self._path, 'votes', self._to_dict(), True)


    def get(self, id: str) -> VoteOption:
        if id in self.options.keys():
            return self.options[id]
        else:
            raise KeyError(f"Option {id} not found in vote {self.id}")

    def add_vote(self, id: str, author: NSID, _save: bool = True):
        """
        Ajoute un vote à l'option spécifiée
        """

        self.get(id).count += 1
        self.get(id).voters.append(author)
        self.voters.append(author)

        if _save:
            self.save()

    def add_votes(self, author: NSID, *ids: str):
        """
        Ajoute un vote aux loptions spécifiées
        """

        for id in ids:
            self.add_vote(id, author, _save = False)

        self.save()

    def close(self):
        """
        Ferme le vote
        """

        self.end_date = round(time.time())
        self.save()


class Party:
    def __init__(self, id: NSID):
        self._path: str = ''

        self.id = id
        self.color: int = 0x000000
        self.motto: str = None

    def _load(self, _data: dict, path: str):
        self._path = path

        self.id = NSID(_data['id'])

        self.color = _data['color']
        self.motto = _data['motto']

    def _to_dict(self) -> dict:
        return {
            'id': self.id,
            'color': self.color,
            'motto': self.motto
        }

    def save(self):
        db.put_item(self._path, 'parties', self._to_dict(), True)


class Candidate:
    def __init__(self, id: NSID):
        self._path: str = ''

        self.id: NSID = id
        self.scale: Scale = Scale()
        self.party: Party = None
        self.current: NSID = None
        self.history: dict = {}

    def _load(self, _data: dict, path: str):
        self._path = path

        self.id = NSID(_data['id'])
        self.scale._load(_data['scale'])

        _party = db.get_item(path, 'parties', _data['party'])

        if _party:
            self.party = Party(NSID(_data['party']))
            self.party._load(_party, path)

        self.current = NSID(_data['current']) if _data['current'] else None
        self.history = _data['history']

    def _to_dict(self) -> dict:
        return {
            'id': self.id,
            'scale': self.scale._to_dict(),
            'party': self.party.id if self.party else None,
            'current': self.current,
            'history': self.history
        }

    def save(self):
        db.put_item(self._path, 'candidates', self._to_dict(), True)