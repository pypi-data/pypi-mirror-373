import os
import time
import typing

from ..models.base import NSID, Interface
from ..models.entities import _load_position, Entity, User, Organization, Position, PositionPermissions, Certification

from .. import database as db


class EntityInterface(Interface):
    """
    Interface qui vous permettra d'interagir avec les profils des membres ainsi que les différents métiers et secteurs d'activité.

    ## Informations disponibles
    - Profil des membres et des entreprises: `.User | .Organization`
    - Appartenance et permissions d'un membre dans un groupe: `.GroupMember.MemberPermissions`
    - Position légale et permissions d'une entité: `.Position.Permissions`
    """

    def __init__(self, path: str) -> None:
        super().__init__(os.path.join(path, 'entities'))

    """
    ---- ENTITÉS ----
    """

    def get_entity(self, id: NSID, _class: typing.Type) -> User | Organization | None:
        """
        Fonction permettant de récupérer le profil public d'une entité.\n

        ## Paramètres
        - id: `NSID`\n
            ID héxadécimal de l'entité à récupérer
        - _class: `Type`\n
            Classe du modèle à prendre (`.User` ou `.Organization`)

        ## Renvoie
        - `.User` dans le cas où l'entité choisie est un membre
        - `.Organization` dans le cas où c'est un groupe
        - `None` dans le cas où c'est indéterminé ou l'entité n'existe pas
        """

        id = NSID(id)

        if _class == User:
            data = db.get_item(self.path, 'individuals', id)
        elif _class == Organization:
            data = db.get_item(self.path, 'organizations', id)
        elif _class is None:
            data = db.get_item(self.path, 'individuals', id)
            _class = User

            if not data:
                data = db.get_item(self.path, 'organizations', id)
                _class = Organization

            if not data:
                _class = None
        else:
            raise ValueError(f"Invalid class type: {_class.__name__}")

        if not data:
            return


        # TRAITEMENT

        if _class == User:
            entity = User(id)
        elif _class == Organization:
            entity = Organization(id)
        else:
            return


        entity._load(data, self.path)

        return entity

    def create_entity(self, id: NSID, name: str, _class: typing.Type, position: str = None):
        """
        Fonction permettant de créer ou modifier une entité.

        ## Paramètres
        - id (`NSID`): Identifiant NSID
        - name (`str`): Nom d'usage
        - _class (`.User` ou `.Organization`): Type de l'entité
        - position (`str`, optionnel): ID de la position civile
        """

        id = NSID(id)

        if _class == Organization:
            data = {
                'id': id,
                'name': name,
                'position': position if position else 'group',
                'register_date': round(time.time()),
                'owner_id': NSID(0x100), # self.session.author, | TODO: Implémenter les Sessions
                'certifications': {}, # Implémenter les Certifications
                'members': {},
                'additional': {}
            }
        elif _class == User:
            data = {
                'id': id,
                'name': name,
                'position': position if position else 'member',
                'register_date': round(time.time()),
                'certifications': {},
                'xp': 0,
                'boosts': {},
                'additional': {}
            }
        else:
            raise ValueError(f"Class '{_class.__name__}' not recognized.")

        db.put_item(self.path, 'individuals' if _class == User else 'organizations', data, True)


        # TRAITEMENT

        entity = User(id) if _class == User else Organization(id)
        entity._load(data, self.path)

        return entity

    def delete_entity(self, id: NSID):
        """
        Fonction permettant de supprimer le profil d'une entité

        ## Paramètres
        id: `NSID`\n
            L'ID de l'entité à supprimer
        """

        try:
            db.delete_item(self.path, 'individuals', NSID(id))
        except KeyError:
            db.delete_item(self.path, 'organizations', NSID(id))

    def fetch_entities(self, _class: typing.Type, **query: typing.Any) -> list[User] | list[Organization]:
        """
        Récupère une liste d'entités en fonction d'une requête.

        ## Paramètres
        - _class (`.User` ou `.Organization`):\n
            Table dans laquelle chercher les utilisateurs
        - query: `**dict`\n
            La requête pour filtrer les entités.

        ## Renvoie
        - `list[.User | .Organization]`
        """

        if _class == User:
            table = 'individuals'
        elif _class == Organization:
            table = 'organizations'
        else:
            raise ValueError(f"Class '{_class.__name__}' is not recognized.")

        _res = db.fetch(f"{self.path}:{table}", **query)


        res = []

        for _entity in _res:
            if _entity is None: continue

            if _class == User:
                entity = User(_entity["id"])
            elif _class == Organization:
                entity = Organization(_entity["id"])
            else:
                entity = Entity(_entity["id"])

            entity._load(_entity, self.path)

            res.append(entity)

        return res



    def get_position(self, id: str) -> Position:
        """
        Récupère une position légale (métier, domaine professionnel).

        ## Paramètres
        id: `str`\n
            ID de la position (SENSIBLE À LA CASSE !)

        ## Renvoie
        - `.Position`
        """

        data = _load_position(id, self.path)

        if not data:
            return

        # TRAITEMENT

        position = Position(id)
        pos = _load_position(id, self.path)
        position._load(pos, self.path)

        return position

    def get_position_tree(self, id: str, tree: tuple = ()) -> tuple:
        position = self.get_position(id)

        if position.root:
            return self.get_position_tree(position.root, tree + position.id,)
        else:
            return tree + position.id,

    def permission_herit(self, id: str, permissions: PositionPermissions = PositionPermissions()) -> tuple:
        position = self.get_position(id)

        permissions.merge(position.permissions)

        if position.root:
            self.permission_herit(position.root, permissions)

    def create_position(
        self,
        id: str,
        title: str,
        permissions: PositionPermissions = PositionPermissions(),
        root: Position = None,
        level: int = None
    ) -> Position:
        """
        Crée une position légale

        ## Paramètres
        - id: `str`\n
            ID de la position
        - title: `str`\n
            Titre de la position
        - root: `str`\n
            Catégorie de la position (officier, citoyen)
        - level: `int`\n
            Grade de la position dans cette catégorie
        - permissions: `.PositionPermissions` (optionnel)\n
            Permissions accordées à la position
        """

        if root and not level:
            raise ValueError("If 'root' is specified, 'level' must also be specified.")

        data = {
            'id': id,
            'name': title,
            'role': None,
            'root': root.id if root else None,
            'level': level,
            'permissions': permissions.__dict__
        }

        db.put_item(self.path, 'positions', data)


        position = Position(id)
        pos = _load_position(id, self.path)
        position._load(pos, self.path)

        return position

    def delete_position(self, id: str):
        db.delete_item(self.path, 'positions', id)

    def fetch_positions(self, **query: typing.Any) -> list[Position]:
        """
        Récupère une liste de positions en fonction d'une requête.

        ## Paramètres
        query: `**dict`\n
            La requête pour filtrer les positions.

        ## Renvoie
        - `list[.Position]`
        """

        _res = db.fetch('positions', **query)
        res = []

        for _data in _res:
            pos = Position()
            pos._load(_data, self.path)

            self.permission_herit(pos.id, pos.permissions)

            res.append(pos)

        return res


    def get_certification(self, id: str) -> Certification:
        """
        Récupère une certification.

        ## Paramètres
        id: `str`\n
            ID de la certification (SENSIBLE À LA CASSE !)

        ## Renvoie
        - `.Certification`
        """

        data = db.get_item(self.path, 'certifications', id)

        if not data:
            return

        # TRAITEMENT

        certification = Certification(id)
        certification._load(data, self.path)

        return certification

    def register_certification(self, id: str, title: str, owner: Organization, parent: Certification = None, duration: int = 2419200) -> Certification:
        """
        Crée une certification

        ## Paramètres
        - id: `str`\n
            ID de la certification
        - title: `str`\n
            Titre de la certification
        - owner: `Organization`\n
            Organisation propriétaire de la certification
        - parent: `Certification`\n
            Certification mère (nécessaire à l'entité qui voudra délivrer celle-ci)
        - duration: `int`\n
            Durée de la certification en secondes (par défaut 28 jours)
        """

        data = {
            'id': id,
            'name': title,
            'duration': duration,
            'parent': parent.id if parent else None,
            'owner': owner.id
        }

        db.put_item(self.path, 'certifications', data)


        certification = Certification(id)
        certification._load(data, self.path)

        return certification

    def delete_certification(self, id: str):
        db.delete_item(self.path, 'certifications', id)

    def fetch_certifications(self, **query: typing.Any) -> list[Certification]:
        """
        Récupère une liste de certifications en fonction d'une requête.

        ## Paramètres
        query: `**dict`\n
            La requête pour filtrer les certifications.

        ## Renvoie
        - `list[.Certification]`
        """

        _res = db.fetch('certifications', **query)
        res = []

        for _data in _res:
            cert = Certification()
            cert._load(_data, self.path)

            res.append(cert)

        return res


    # SHORTCUTS

    def get_user(self, id: NSID) -> User | None:
        return self.get_entity(id, User)

    def get_group(self, id: NSID) -> Organization | None:
        return self.get_entity(id, Organization)

    def create_user(self, id: NSID, name: str, position: str = None) -> User:
        return self.create_entity(id, name, User, position)

    def create_group(self, id: NSID, name: str, position: str = None) -> Organization:
        return self.create_entity(id, name, Organization, position)

    def fetch_users(self, **query: typing.Any) -> list[User]:
        """
        Récupère une liste d'utilisateurs en fonction d'une requête.

        ## Paramètres
        query: `**dict`\n
            La requête pour filtrer les utilisateurs.

        ## Renvoie
        - `list[.User]`
        """

        return self.fetch_entities(User, **query)

    def fetch_groups(self, **query: typing.Any) -> list[Organization]:
        """
        Récupère une liste d'organisations en fonction d'une requête.

        ## Paramètres
        query: `**dict`\n
            La requête pour filtrer les organisations.

        ## Renvoie
        - `list[.Organization]`
        """

        return self.fetch_entities(Organization, **query)