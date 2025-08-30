import os
import random

def get_in_drive(path: str) -> bytes:
	with open(path, 'rb') as _buffer:
		return _buffer.read()

def merge_permissions(d1: dict[str, str], d2: dict[str, str]) -> dict[str, str]:
	new_dict: dict[str, str] = d1.copy()

	for key, val in d2.items():
		new_dict[key] = bool(val or new_dict.get(key, False))

	return new_dict

def shorten(text: str, length: int, dots: bool = True) -> str:
	if dots:
		return text[:length - 3] + "..."
	else:
		return text[:length]


# Sécurité

def adjust_path(path: str) -> str:
	path = os.path.normpath(path)
	path = path.replace('\\', '/')

	newpath = []
	for component in path.split('/'):
		if component not in ('..',):
			newpath.append(component)

	return '/'.join(newpath)


# Banque

def gen_digicode(length: int = 6) -> str:
	return hex(random.randint(0, 16 ** length - 1))[2:].upper().zfill(length)

# Impôts

TAXATIONS = {
	'taxe_ega': "105",
	'taxe_dc': "106"
}

BONUSES = {
	'aide_ega': "105",
	'benevolat': "105",
	'campagnes': "6"
}

def calculate_amount(amount: int = 0, specs: dict = {},history: dict = {}) -> dict:
	sheet = {
		"aide_ega": 0,
		"benevolat": 0,
		"campagnes": 0,
		"taxe_ega": 0,
		"taxe_dc": 0
	}

	# Taxe égalitaire
	if amount < 2000:
		percentage = 0
	elif 2000 <= amount < 5000:
		percentage = .01
	elif 5000 <= amount < 20000:
		percentage = .025
	elif 20000 <= amount < 50000:
		percentage = .045
	else:
		percentage = .05
		e = amount

		while e >= 150000 and percentage < .2:
			percentage += .01
			e -= 100000

	sheet['taxe_ega'] += int(round(amount * percentage))

	# Taxe double compte
	if specs.get('DC'):
		if amount < 2000:
			percentage = .01
		elif 2000 <= amount < 5000:
			percentage = .025
		elif 5000 <= amount < 20000:
			percentage = .045
		elif 20000 <= amount < 50000:
			percentage = .05
		else:
			percentage = .1
			e = amount

			while e >= 150000 and percentage < .3:
				percentage += .05
				e -= 100000

		sheet['taxe_dc'] += int(round(amount * percentage))


	"""
	AIDES & BONUS
	"""

	# Aide égalitaire
	if amount < 2000:
		sheet['aide_ega'] -= 2000 - amount

	# Bonus de dons aux assos et de participation aux campagnes
	if amount != 0:
		dons = history.get('dons', 0)

		if dons / amount < .05:
			sheet['benevolat'] -= .1 * dons
		elif .05 <= dons / amount < .1:
			sheet['benevolat'] -= .25 * dons
		elif .1 <= dons / amount < .25:
			sheet['benevolat'] -= .4 * dons
		elif .25 <= dons / amount < .4:
			sheet['benevolat'] -= .6 * dons
		elif .4 <= dons / amount < .6:
			sheet['benevolat'] -= .75 * dons
		elif .6 <= dons / amount < 1:
			sheet['benevolat'] -= dons

	campagnes = history.get('campagnes', 0)

	if campagnes >= 0:
		sheet['campagnes'] -= campagnes

	return sheet