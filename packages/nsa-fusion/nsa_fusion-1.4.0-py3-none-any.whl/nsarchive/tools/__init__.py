import json
import os
import typing

from ..models.base import NSID
from .. import database as db

class Attribute():
	def __init__(self, name: str, _type: typing.Type, nullable: bool = False):
		self.name = name

		if _type.__name__ not in ('NSID', 'str', 'int', 'float', 'bool', 'list', 'dict'):
			raise ValueError(f"Invalid type: {_type}")

		self.type = _type.__name__
		self.nullable = nullable

def gendb(path: str, table: str, attrs: tuple[Attribute]):
	if not os.path.exists(path):
		os.makedirs(path)

	with open(os.path.join(path, f"{table}.json"), 'w') as _db:
		data = {
			'meta': {
				'table_name': table,
			},
			'attributes': [ attr.__dict__ for attr in attrs ],
			'idx': [],
			'items': []
		}

		json.dump(data, _db , indent = 4)

def setup(path: str, include_logs: bool = False, include_drive: bool = False):
	# Drive & Logs

	if include_drive:
		os.makedirs(os.path.join(path, 'drive'), exist_ok = True)

	if include_logs:
		os.makedirs(os.path.join(path, 'entities', 'logs'), exist_ok = True)
		os.makedirs(os.path.join(path, 'economy', 'logs'), exist_ok = True)
		os.makedirs(os.path.join(path, 'state', 'logs'), exist_ok = True)


	# Entités

	gendb(
		path = os.path.join(path, 'entities'),
		table = 'individuals',
		attrs = (
			Attribute('id', NSID),
			Attribute('name', str),
			Attribute('register_date', int),
			Attribute('position', str),
			Attribute('certifications', dict),
			Attribute('additional', dict),
			Attribute('xp', int),
			Attribute('boosts', dict),
		)
	)

	gendb(
		path = os.path.join(path, 'entities'),
		table = 'organizations',
		attrs = (
			Attribute('id', NSID),
			Attribute('name', str),
			Attribute('register_date', int),
			Attribute('position', str),
			Attribute('certifications', dict),
			Attribute('additional', dict),
			Attribute('owner_id', NSID),
			Attribute('members', dict)
		)
	)

	gendb(
		path = os.path.join(path, 'entities'),
		table = 'positions',
		attrs = (
			Attribute('id', str),
			Attribute('name', str),
			Attribute('role', int, nullable = True),
			Attribute('root', str, nullable = True),
			Attribute('level', int, nullable = True),
			Attribute('permissions', dict)
		)
	)

	gendb(
		path = os.path.join(path, 'entities'),
		table = 'certifications',
		attrs = (
			Attribute('id', str),
			Attribute('name', str),
			Attribute('owner', NSID),
			Attribute('parent', NSID),
			Attribute('duration', int)
		)
	)

	db.put_item(os.path.join(path, 'entities'), table = 'positions', item = {
		'id': 'member',
		'name': 'Membre',
		'role': None,
		'root': None,
		'level': None,
		'permissions': {}
	})

	db.put_item(os.path.join(path, 'entities'), table = 'positions', item = {
		'id': 'group',
		'name': 'Groupe',
		'role': None,
		'root': None,
		'level': None,
		'permissions': {}
	})


	# Économie

	gendb(
		path = os.path.join(path, 'economy'),
		table = 'accounts',
		attrs = (
			Attribute('id', NSID),
			Attribute('owner_id', NSID),
			Attribute('register_date', int),
			Attribute('tag', str, nullable = True),
			Attribute('amount', int),
			Attribute('income', int),
			Attribute('frozen', bool),
			Attribute('flagged', bool),
			Attribute('digicode', str)
		)
	)


	# Justice

	gendb(
		path = os.path.join(path, 'state'),
		table = 'reports',
		attrs = (
			Attribute('id', NSID),
			Attribute('target', NSID),
			Attribute('author', NSID),
			Attribute('date', int),
			Attribute('status', int),
			Attribute('reason', str, nullable = True),
			Attribute('details', str, nullable = True)
		)
	)

	gendb(
		path = os.path.join(path, 'state'),
		table = 'lawsuits',
		attrs = (
			Attribute('id', NSID),
			Attribute('target', NSID),
			Attribute('judge', NSID),
			Attribute('title', str),
			Attribute('date', int),
			Attribute('report', NSID, nullable = True),
			Attribute('is_private', bool),
			Attribute('is_open', bool)
		)
	)

	gendb(
		path = os.path.join(path, 'state'),
		table = 'sanctions',
		attrs = (
			Attribute('id', NSID),
			Attribute('target', NSID),
			Attribute('type', str),
			Attribute('date', int),
			Attribute('duration', int),
			Attribute('title', str),
			Attribute('lawsuit', NSID, nullable = True)
		)
	)


	# État & Politique

	gendb(
		path = os.path.join(path, 'state'),
		table = 'votes',
		attrs = (
			Attribute('id', NSID),
			Attribute('title', str),
			Attribute('author', NSID),
			Attribute('type', str),
			Attribute('anonymous', bool),
			Attribute('max_choices', int),
			Attribute('min_choices', int),
			Attribute('majority', int),
			Attribute('start', int),
			Attribute('end', int),
			Attribute('options', dict),
			Attribute('voters', list)
		)
	)

	gendb(
		path = os.path.join(path, 'state'),
		table = 'parties',
		attrs = (
			Attribute('id', NSID),
			Attribute('color', int, nullable = True),
			Attribute('motto', str, nullable = True)
		)
	)

	gendb(
		path = os.path.join(path, 'state'),
		table = 'candidates',
		attrs = (
			Attribute('id', NSID),
			Attribute('scale', dict, nullable = True),
			Attribute('party', NSID, nullable = True),
			Attribute('current', NSID, nullable = True),
			Attribute('history', dict, nullable = True)
		)
	)