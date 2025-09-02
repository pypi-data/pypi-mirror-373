# Fichier

`fichier` est un outil en ligne de commande Python pour afficher la structure des fichiers et répertoires, similaire à la commande `tree -a`. Il est conçu pour être modulaire et extensible, avec chaque option gérée par un module séparé.

## Installation

Depuis le dossier du projet :

```bash
pip install fichierfr
````

## Utilisation

```bash
# Affiche la structure du répertoire courant
fichier -structure
fichier -s

# Affiche la structure d'un répertoire spécifique
fichier -s /chemin/vers/repertoire
```

## Structure du projet

```
fichier/
├── fichier/
│   ├── __init__.py
│   ├── cli.py
│   └── structure.py
├── pyproject.toml
└── README.md
```

## Modules

* `structure` : gère l'affichage de l'arborescence comme `tree -a`.
* `cli.py` : point d'entrée de l'application, parse les arguments et appelle les modules appropriés.

## Licence

Ce projet est sous licence Personnaliser. Voir le fichier [LICENSE](LICENSE) pour plus de détails.
