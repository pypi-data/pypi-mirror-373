# ~~NSA~~ Fusion :fire:

## Pré-requis

- Python 3.10 ou + (Python 3.13 si possible)
- Deux barres de Twix ou une tasse de thé

> :tongue: Plus besoin de serveur distant


## Avant de démarrer

Dans la documentation, vous croiserez souvent des noms de classes comme `.User` ou autres similaires. Le «.» devant le nom de la classe signfie qu'elle appartient au module Fusion, et qu'il faut donc les interprêter comme `nsarchive.User`. La seule exception est `NSID` qui ne sera pas précédé d'un point mais devra être interprêté de la même manière.


## Installation

L'installation de Fusion se fait via pip:

```sh
pip install nsa-fusion
```

La dernière version de nsarchive devrait s'installer. La seule dépendance requise pour Fusion est `pillow` mais celle-ci devrait s'installer en même temps que le module. Vous pourriez également avoir besoin des modules `bcrypt` et `python-dotenv`, ceux-ci devront être installés manuellement.


### Bonus: Environnement virtuel

Il est recommandé mais non obligatoire d'avoir un environnement virtuel (venv) pour votre projet. Sa création se fait comme ceci:

```sh
python -m venv .venv
```

N'oubliez pas de l'activer via cette commande pour powershell...

```ps1
.venv\Scripts\Activate
```

...ou cette commande pour les terminaux type UNIX (Bash par exemple)

```sh
source .venv/bin/activate
```

## Prise en main

### Identifier les objets

Les objets sont tous identifiables sur NSAv3. Ils ont un identifiant commun appelé NSID (`from nsarchive import NSID`). Cet identifiant n'est rien de plus qu'un nombre hexadécimal. Il peut être utilisé comme un string, dans un print ou un f-string par exemple. Cet identifiant est communément basé sur plusieurs valeurs fixes ou universelles, dont les deux plus fréquentes sont:
- L'ID Discord de l'objet concerné, dans le cas d'un utilisateur par exemple
- Le timestamp (secondes depuis 1970) du moment où il a été créé, dans le cas de la plupart des autres objets


### Interfaces

Le module nsarchive est divisé en **4 interfaces**:
- **Entités** (membres, groupes, positions)
- **Économie** (comptes en banque, dettes)
- **Justice** (signalements, procès, sanctions)
- **État** (votes, élections)

> Les interfaces État et Justice peuvent être confondues et désignées comme République, comme c'était le cas dans les anciennes version de NSArchive.


Les interfaces ont toutes trois rôles en commun:
- Récupérer des objets
- Créer des objets
- Supprimer des objets (Entités uniquement)