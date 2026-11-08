# Log Analysis Pipeline

## 1. Présentation du projet

Ce projet est un programme développé en Python qui permet de lire et d'analyser des fichiers de logs d'authentification.

Ces logs contiennent des informations sur les tentatives de connexion à un système, notamment les utilisateurs concernés, le statut des connexions et les adresses IP utilisées.

## 2. Objectif du projet

Le but est de transformer des logs bruts, parfois difficiles à lire, en statistiques claires et faciles à comprendre.

Le programme permet de :

- Voir le nombre de connexions réussies pour chaque utilisateur.
- Identifier les pays d'origine des tentatives de connexion échouées.
- Compter les tentatives effectuées avec un utilisateur invalide.
- Afficher les résultats sous forme de graphiques.

## 3. Organisation des fichiers

```text
log_analysis/
│
├── data/
│   ├── auth.log.1
│   ├── auth.log.2
│   ├── auth.log.3.gz
│   └── auth.log.4.gz
│
├── ingestion/
│   └── read.py
│
├── processing/
│   ├── analysis.py
│   ├── dashboard.py
│   ├── extract_transfrom.py
│   └── geolocation.py
│
├── main.py
├── README.md
├── pyproject.toml
└── uv.lock
```

J'ai séparé le projet en plusieurs parties pour que chaque fichier ait un rôle précis :

- **data/** : contient les fichiers de logs à analyser. Certains fichiers sont compressés au format `.gz`.
- **ingestion/** : contient `read.py`, qui s'occupe de lire les fichiers de logs, qu'ils soient compressés ou non.
- **processing/** : contient les modules responsables du traitement des données :
  - `extract_transfrom.py` : extrait les informations utiles de chaque ligne de log.
  - `geolocation.py` : détermine le pays associé à une adresse IP publique et conserve les résultats dans un cache.
  - `analysis.py` : analyse les données et calcule les statistiques.
  - `dashboard.py` : crée les graphiques à partir des résultats obtenus.
- **main.py** : lance l'ensemble du pipeline, de la lecture des fichiers jusqu'à l'affichage des graphiques.
- **pyproject.toml** : contient les informations du projet et ses dépendances.
- **uv.lock** : contient les versions verrouillées des dépendances.

## 4. Bibliothèques utilisées

- **gzip** : permet de lire les fichiers compressés au format `.gz`.
- **os** : permet de gérer les fichiers et les dossiers.
- **re** : permet d'extraire les informations des lignes de log à l'aide des expressions régulières.
- **logging** : permet d'afficher des messages d'information et d'erreur pendant l'exécution.
- **json** : permet de sauvegarder et de relire le cache de géolocalisation.
- **requests** : permet d'interroger le service de géolocalisation des adresses IP.
- **ipaddress** : permet de vérifier la validité des adresses IP.
- **matplotlib** : permet de créer et d'afficher les graphiques.

## 5. Comment lancer le projet

### Avant de commencer

Il faut avoir Python installé sur sa machine ainsi que les outils nécessaires pour installer les dépendances du projet.

### Installation

Activer d'abord l'environnement virtuel :

```powershell
.\.venv\Scripts\Activate.ps1
```

Ensuite, installer les dépendances :

```powershell
uv sync
```

### Lancement

Depuis le dossier principal du projet, exécuter :

```powershell
python main.py
```

Le programme lit les fichiers de logs, effectue les différentes analyses, affiche les statistiques obtenues et génère les trois graphiques du dashboard.