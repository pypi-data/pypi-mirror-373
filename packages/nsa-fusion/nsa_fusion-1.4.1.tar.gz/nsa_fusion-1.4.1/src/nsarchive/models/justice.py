import time

from .base import NSID

from .. import database as db

class Report:
    def __init__(self, id: NSID):
        self._path: str = ''

        self.id: NSID = id
        self.author: NSID = NSID('0')
        self.target: NSID = NSID('0')
        self.date: int = round(time.time())
        self.status: int = 0 # 0: En attente, 1: Accepté, 2: Rejeté
        self.reason: str = None # Raison proposée par le bot
        self.details:str = None # Description des faits

    def _load(self, _data: dict, path: str) -> None:
        self._path = path

        self.id = NSID(_data['id'])
        self.author = NSID(_data['author'])
        self.target = NSID(_data['target'])
        self.date = _data['date']
        self.status = _data['status']
        self.reason = _data.get('reason', None)
        self.details = _data.get('details', None)

    def _to_dict(self) -> dict:
        return {
            'id': self.id,
            'target': self.target,
            'author': self.author,
            'date': self.date,
            'status': self.status,
            'reason': self.reason,
            'details': self.details
        }

    def save(self):
        db.put_item(self._path, 'reports', self._to_dict())

    def update(self, status: str | int):
        __statuses = [
            'pending',
            'accepted',
            'rejected'
        ]

        if status not in __statuses:
            if isinstance(status, int) and 0 <= status <= 2:
                status = __statuses[status]
            else:
                raise ValueError(f"Invalid status: {status}. Must be one of {__statuses} or an integer between 0 and 2.")

        self.status = __statuses.index(status)
        self.save()

class Sanction:
    def __init__(self, id: NSID):
        self._path: str = ''

        self.id: NSID = id
        self.target: NSID = NSID('0')
        self.type: str = None
        self.date: int = round(time.time())
        self.duration: int = 0
        self.title: str = None
        self.lawsuit: Lawsuit = None

    def _load(self, _data: dict, path: str,) -> None:
        self._path = path

        self.id = NSID(_data['id'])
        self.target = NSID(_data['target'])
        self.type = _data['type']
        self.date = _data['date']
        self.duration = _data['duration']
        self.title = _data['title']

        lawsuit = db.get_item(path, 'lawsuits', _data['lawsuit'])

        if lawsuit:
            self.lawsuit = Lawsuit(NSID(lawsuit))
            self.lawsuit._load(lawsuit, path)

    def _to_dict(self) -> dict:
        return {
            'id': self.id,
            'target': self.target,
            'type': self.type,
            'date': self.date,
            'duration': self.duration,
            'title': self.title,
            'lawsuit': self.lawsuit if self.lawsuit else None
        }

    def save(self):
        db.put_item(self._path, 'sanctions', self._to_dict())

class Lawsuit:
    def __init__(self, id: NSID):
        self._path: str = ''

        self.id: NSID = id
        self.target: NSID = NSID('0')
        self.judge: NSID = NSID('0')
        self.title: str = None
        self.date: int = round(time.time())
        self.report: Report = None
        self.is_private: bool = False
        self.is_open: bool = False

    def _load(self, _data: dict, path: str) -> None:
        self._path = path

        self.id = NSID(_data['id'])
        self.target = NSID(_data['target'])
        self.judge = NSID(_data['judge'])
        self.title = _data.get('title')
        self.date = _data.get('date', round(time.time()))

        report = db.get_item(path, 'reports', _data['report'])

        if report: 
            self.report = Report(NSID(report))
            self.report._load(report, path)

        self.is_private = bool(_data.get('private', 0))
        self.is_open = _data.get('status', 0) == 0

    def _to_dict(self) -> dict:
        return {
            'id': self.id,
            'target': self.target,
            'judge': self.judge,
            'title': self.title,
            'date': self.date,
            'report': self.report.id if self.report else None,
            'is_private': self.is_private,
            'is_open': self.is_open
        }

    def save(self):
        db.put_item(self._path, 'reports', self._to_dict())