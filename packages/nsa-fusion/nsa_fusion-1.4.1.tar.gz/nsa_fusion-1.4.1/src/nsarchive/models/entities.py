from __future__ import annotations

import time
import typing

from ..functions.commons import merge_permissions
from .base import NSID

from .. import database as db

def _load_position(id: str, path: str) -> dict:
    position = db.get_item(path, 'positions', id)

    if position is None:
        return

    if position['root']:
        root = _load_position(position['root'], path)

        p1 = position['permissions']
        p2 = root['permissions']

        position['permissions'] = merge_permissions(p1, p2)

    return position


class PositionPermissions:
    """
    Permissions d'une position à l'échelle du serveur. Certaines sont attribuées selon l'appartenance à divers groupes ayant une position précise
    """

    def __init__(self, _data: list | dict[str, bool] = None) -> None:
        self.create_certifications: bool = False # Créer des certifications
        self.create_entities: bool = False # Créer des entités
        self.create_groups: bool = False # Créer des groupes
        self.create_parties: bool = False # Créer un parti
        self.debit_accounts: bool = False # Débiter les comptes bancaires
        self.edit_constitution: bool = False # Proposer des lois constitutionnelles
        self.edit_laws: bool = False # Proposer des lois
        self.handle_reports: bool = False # Accepter ou refuser les signalements
        self.investigate: bool = False # Accéder aux logs
        self.manage_accounts: bool = False # Gérer les comptes bancaires
        self.manage_bots: bool = False # Gérer la config des bots
        self.manage_certifications: bool = False # Gérer et distribuer les certifications
        self.manage_elections: bool = False # Planifier ou annuler des élections, gérer des candidatures...
        self.manage_entities: bool = False # Gérer les entités
        self.manage_government: bool = False # Créer des minisètres, destituer des ministres, etc.
        self.manage_groups: bool = False # Gérer les groupes
        self.manage_lawsuits: bool = False # Gérer ou ouvrir des poursuites judiciaires
        self.manage_officers: bool = False # Gérer les officiers et agents
        self.manage_parties: bool = False # Gérer les partis
        self.manage_positions: bool = False # Gérer les positions
        self.manage_votes: bool = False # Gérer les élections
        self.moderate_entities: bool = False # Modérer les entités
        self.moderate_groups: bool = False # Modérer les groupes
        self.use_aliases: bool = False # Faire une requête au nom d'une autre entité
        self.vote: bool = False # Voter
        self.vote_laws: bool = False # Voter les lois

        if _data:
            if isinstance(_data, list):
                self.merge(dict(zip(_data, [ True ] * len(_data))))
            elif isinstance(_data, dict):
                self.merge(_data)
            else:
                raise TypeError("Invalid data format for PositionPermissions.")

    def __repr__(self):
        return self.__dict__.__repr__()

    def merge(self, permissions: dict[str, bool] | typing.Self):
        if isinstance(permissions, PositionPermissions):
            permissions: dict[str, bool] = permissions.__dict__

        for key, val in permissions.items():
            perm: bool = self.__getattribute__(key)
            self.__setattr__(key, bool(perm or val))

class Position:
    """
    Position légale d'une entité

    ## Attributs
    - id: `str`\n
        Identifiant de la position
    - name: `str`\n
        Titre de la position
    - root: `str`\n
        Catégorie de la position (officier, citoyen)
    - level: `int`\n
        Grade de la position dans cette catégorie
    - permissions: `.PositionPermissions`\n
        Permissions accordées à l'utilisateur
    """

    def __init__(self, id: str = 'member') -> None:
        self._path: str = ""

        self.id = id
        self.name: str = "Membre"
        self.role: int = None
        self.root: str = None
        self.level: int = None
        self.permissions: PositionPermissions = PositionPermissions()


    def __repr__(self):
        return self.id

    def __eq__(self, value: Position):
        if not isinstance(value, Position):
            return NotImplemented

        return self.id == value.id

    def _lt_(self, value: Position):
        if not isinstance(value, Position):
            return NotImplemented

        a, b = self._compare(value)

        return a < b

    def _le_(self, value: Position):
        if not isinstance(value, Position):
            return NotImplemented

        a, b = self._compare(value)

        return a <= b

    def _gt_(self, value: Position):
        if not isinstance(value, Position):
            return NotImplemented

        a, b = self._compare(value)

        return a > b

    def _ge_(self, value: Position):
        if not isinstance(value, Position):
            return NotImplemented

        a, b = self._compare(value)

        return a >= b

    def _compare(self, value: Position) -> tuple[int, int]:
        if not isinstance(value, Position):
            return NotImplemented

        if self.root == value.root:
            return self.level, value.level
        else:
            _ROOTS = [
                None,
                'member',
                'citizen',
                'officer',
                'admin'
            ]

            _ROOTS_GROUPS = [
                None,
                'group',
                'agency',
                'department'
            ]

            if self.root in _ROOTS:
                if value.root in _ROOTS:
                    return _ROOTS.index(self.root), _ROOTS.index(value.root)
                else:
                    raise ValueError("Cannot compare user and group")
            elif self.root in _ROOTS_GROUPS:
                if value.root in _ROOTS_GROUPS:
                    return _ROOTS_GROUPS.index(self.root), _ROOTS_GROUPS.index(value.root)
                else:
                    raise ValueError("Cannot compare user and group")


    def _load(self, _data: dict, path: str) -> None:
        self._path = path

        self.id = _data['id']
        self.name = _data['name']
        self.role = _data['role']
        self.root = _data['root']
        self.level = _data['level']
        self.permissions.merge(_data['permissions'])

    def _to_dict(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'role': self.role,
            'root': self.root,
            'level': self.level,
            'permissions': self.permissions.__dict__
        }

    def save(self):
        db.put_item(self._path, 'positions', self._to_dict(), True)


class Certification:
    """
    Classe de référence pour les certifications
    """

    def __init__(self, id: NSID) -> None:
        self._path: str = '' # Chemin de la db

        self.id: NSID = NSID(id) # ID hexadécimal de la certification
        self.name: str = "Certification Inconnue"
        self.owner: NSID = NSID() # Entreprise propriétaire de la certification
        self.parent: NSID = NSID() # Certification mère (nécessaire à l'entité qui voudra délivrer celle-ci)
        self.duration: int = 0

    def _load(self, _data: dict, path: str):
        self._path = path

        self.id = NSID(_data['id'])
        self.name = _data['name']
        self.owner = NSID(_data['owner'])
        self.parent = NSID(_data['parent'])
        self.duration = _data['duration']

    def _to_dict(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'owner': self.owner,
            'parent': self.parent,
            'duration': self.duration
        }

    def save(self):
        db.put_item(self._path, 'certifications', self._to_dict(), True)


class Entity:
    """
    Classe de référence pour les entités

    ## Attributs
    - id: `NSID`\n
        Identifiant NSID
    - name: `str`\n
        Nom d'usage
    - register_date: `int`\n
        Date d'enregistrement
    - position: `.Position`\n
        Position civile
    - certifications: `dict`\n
        Titres délivrables par les groupes
    - additional: `dict`\n
        Infos supplémentaires exploitables par différents services
    """

    def __init__(self, id: NSID) -> None:
        self._path: str = '' # Chemin de la db

        self.id: NSID = NSID(id) # ID hexadécimal de l'entité
        self.name: str = "Entité Inconnue"
        self.register_date: int = 0
        self.position: Position = Position()
        self.certifications: dict[NSID, int] = {}
        self.additional: dict = {}

    def __eq__(self, value: Entity):
        if not isinstance(value, Entity):
            return NotImplemented

        return self.id == value.id

    def __lt__(self, value: Entity):
        if not isinstance(value, Entity):
            return NotImplemented

        return self.position < value.position

    def __le__(self, value: Entity):
        if not isinstance(value, Entity):
            return NotImplemented

        return self.position <= value.position

    def __gt__(self, value: Entity):
        if not isinstance(value, Entity):
            return NotImplemented

        return self.position > value.position

    def __ge__(self, value: Entity):
        if not isinstance(value, Entity):
            return NotImplemented

        return self.position >= value.position


    def _load(self, _data: dict, path: str):
        self._path = path

        self.id = NSID(_data['id'])
        self.name = _data['name']
        self.register_date = _data['register_date']
        self.certifications = { NSID(id): exp for id, exp in _data['certifications'].items() }

        position = _load_position(_data['position'], path)
        if position: self.position._load(position, path)

        for  key, value in _data.get('additional', {}).items():
            if isinstance(value, str) and value.startswith('\n'):
                self.additional[key] = int(value[1:])
            else:
                self.additional[key] = value

    def save(self):
        pass

    def set_name(self, name: str) -> None:
        self.name = name
        self.save()

    def set_position(self, position: Position) -> None:
        self.position = position
        self.save()

    def add_certification(self, certification: Certification, __expires: int = 2419200) -> None:
        self.certifications[certification.id] = int(round(time.time()) + __expires)
        self.save()

    def has_certification(self, certification: Certification) -> bool:
        _start = self.certifications.get(certification.id)

        if _start:
            if _start + certification.duration < int(round(time.time())):
                return True
            else:
                self.remove_certification(certification.id)

        return False

    def remove_certification(self, certification: NSID) -> None:
        del self.certifications[certification]
        self.save()

    def add_link(self, key: str, value: str | int) -> None:
        self.additional[key] = value
        self.save()

    def unlink(self, key: str) -> None:
        del self.additional[key]
        self.save()

class User(Entity):
    """
    Entité individuelle

    ## Attributs
    - Tous les attributs de la classe `.Entity`
    - xp: `int`\n
        Points d'expérience de l'entité
    - boosts: `dict[str, int]`\n
        Ensemble des boosts dont bénéficie l'entité
    """

    def __init__(self, id: NSID) -> None:
        super().__init__(NSID(id))

        self.xp: int = 0
        self.boosts: dict[str, int] = {}

    def _load(self, _data: dict, path: str):
        self._path = path

        self.id = NSID(_data['id'])
        self.name = _data['name']
        self.register_date = _data['register_date']
        self.certifications = { NSID(id): exp for id, exp in _data['certifications'].items() }

        position = _load_position(_data['position'], path)
        if position: self.position._load(position, path)

        for  key, value in _data.get('additional', {}).items():
            if isinstance(value, str) and value.startswith('\n'):
                self.additional[key] = int(value[1:])
            else:
                self.additional[key] = value

        self.xp = _data['xp']
        self.boosts = _data['boosts']

    def _to_dict(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'position': self.position.id,
            'register_date': self.register_date,
            'certifications': self.certifications,
            'xp': self.xp,
            'boosts': self.boosts,
            'additional': self.additional
        }

    def save(self):
        db.put_item(self._path, 'individuals', self._to_dict(), True)


    def get_level(self) -> None:
        i = 0
        while self.xp > int(round(25 * (i * 2.5) ** 2, -2)):
            i += 1

        return i

    def add_xp(self, amount: int) -> None:
        boost = 0 if 0 in self.boosts.values() or amount <= 0 else max(list(self.boosts.values()) + [ 1 ])
        self.xp += amount * boost

        self.save()

    def edit_boost(self, name: str, multiplier: int = -1) -> None:
        if multiplier >= 0:
            self.boosts[name] = multiplier
        else:
            del self.boosts[name]

        self.save()

    def get_groups(self) -> list[Entity]:
        res = db.fetch(f"{self._path}:organizations")

        data = []

        for grp in res:
            if grp is None:
                continue

            if grp['owner_id'] == str(self.id):
                data.append(grp)
                continue

            if str(self.id) in grp['members'].keys():
                data.append(grp)
                continue

        groups = []

        for grp in data:
            if grp is None: continue

            group = Organization(NSID(grp['id']))
            group._load(grp, self._path)

            groups.append(group)

        return groups


class GroupMember:
    """
    Membre au sein d'une entité collective

    ## Attributs
    - level: `int`\n
        Niveau d'accréditation d'un membre au sein d'un groupe
    - manager: `bool`\n
        Permission ou non de modifier le groupe
    """

    def __init__(self, id: NSID) -> None:
        self._path: str = ''
        self._group_id: NSID = NSID(0x0)

        self.id = id
        self.level: int = 1 # Plus un level est haut, plus il a de pouvoir sur les autres membres
        self.manager: bool = False

    def __repr__(self):
        return f"level: {self.level}, manager: {self.manager}"

    def __eq__(self, value):
        if not isinstance(value, GroupMember):
            return NotImplemented

        return self.id == value.id

    def __lt__(self, value):
        if not isinstance(value, GroupMember):
            return NotImplemented

        if self.level == value.level:
            return value.manager and not self.manager

        return self.level < value.level

    def __le__(self, value):
        if not isinstance(value, GroupMember):
            return NotImplemented

        if self.level == value.level:
            return value.manager

        return self.level < value.level

    def __gt__(self, value):
        if not isinstance(value, GroupMember):
            return NotImplemented

        if self.level == value.level:
            return self.manager and not value.manager

        return self.level > value.level

    def __ge__(self, value):
        if not isinstance(value, GroupMember):
            return NotImplemented

        if self.level == value.level:
            return self.manager

        return self.level > value.level

    def _load(self, _data: dict, path: str, group: NSID):
        self._path = path
        self._group_id = group

        self.level = _data['level']
        self.manager = _data['manager']

    def _to_dict(self) -> dict:
        return {
            'level': self.level,
            'manager': self.manager
        }

    def save(self):
        data = db.get_item(self._path, 'organizations', self._group_id)

        group = data.copy()
        group['id'] = NSID(group['id'])
        group['owner_id'] = NSID(group['owner_id'])

        group['members'] = {}

        for id, m in data['members'].items():
            if m['level'] > 0:
                group['members'][id] = m

        db.put_item(self._path, 'organizations', group, True)

    def edit(self, level: int = None, manager: bool = None) -> None:
        if level:
            self.level = level
        else:
            return

        if manager is not None:
            self.manager = manager

        self.save()

    def promote(self, level: int = None):
        if level is None:
            level = self.level + 1

        self.edit(level = level)

    def demote(self, level: int = None):
        if level is None:
            level = self.level - 1

        self.edit(level = level)


class Organization(Entity):
    """
    Entité collective

    ## Attributs
    - Tous les attributs de la classe `.Entity`
    - owner: `.Entity`\n
        Utilisateur ou entreprise propriétaire de l'entité collective
    - members: `list[.GroupMember]`\n
        Liste des membres de l'entreprise
    """

    def __init__(self, id: NSID) -> None:
        super().__init__(NSID(id))

        self.owner: Entity = User(NSID(0x0))
        self.avatar_path: str = ''

        self.members: dict[NSID, GroupMember] = {}

    def _load(self, _data: dict, path: str):
        self._path = path

        self.id = NSID(_data['id'])
        self.name = _data['name']
        self.register_date = _data['register_date']
        self.certifications = { NSID(id): exp for id, exp in _data['certifications'].items() }

        position = _load_position(_data['position'], path)
        if position: self.position._load(position, path)

        for  key, value in _data.get('additional', {}).items():
            if isinstance(value, str) and value.startswith('\n'):
                self.additional[key] = int(value[1:])
            else:
                self.additional[key] = value


        _owner = db.get_item(path, 'individuals', _data['owner_id'])
        _class = 'user'

        if _owner is None:
            _owner = db.get_item(path, 'organizations', _data['owner_id'])
            _class = 'group'

        if _owner:
            if _class == 'user':
                self.owner = User(_owner['id'])
            elif _class == 'group':
                self.owner = Organization(_owner['id'])
            else:
                self.owner = Entity(_owner['id'])

            self.owner._load(_owner, path)
        else:
            self.owner = None

        for _id, _member in _data['members'].items():
            member = GroupMember(NSID(_id))
            member._load(_member, path, self.id)

            self.members[NSID(member.id)] = member

    def _to_dict(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'position': self.position.id,
            'register_date': self.register_date,
            'owner_id': self.owner.id,
            'members': { id: member._to_dict() for id, member in self.members.items() },
            'certifications': self.certifications,
            'additional': self.additional
        }

    def save(self):
        db.put_item(self._path, 'organizations', self._to_dict(), True)

    def add_member(self, member: NSID) -> GroupMember:
        if not isinstance(member, NSID):
            raise TypeError("L'entrée membre doit être de type NSID")

        member = GroupMember(member)
        member._group_id = self.id
        member._path = self._path

        self.members[member.id] = member

        self.save()
        return member

    def remove_member(self, member: GroupMember) -> None:
        member.demote(level = 0)

    def set_owner(self, member: User) -> None:
        self.owner = member
        self.save()

    def get_member(self, id: NSID) -> GroupMember:
        return self.members.get(id)

    def get_members_by_attr(self, attribute: str = "id") -> list[str]:
        return [ member.__getattribute__(attribute) for member in self.members.values() ]

    def save_avatar(self, data: bytes = None):
        pass