# Guide de Démarrage

Ce guide vous accompagne dans l'installation et la configuration du Blackbox Trading Robot.

## Prérequis

- Python 3.11 ou supérieur
- pip (gestionnaire de paquets Python)
- Git
- PostgreSQL 14+ (pour la persistance des données)
- Google Chrome (pour le scraping)

## Installation

### 1. Cloner le repository

```bash
git clone https://github.com/nicodevelop/blackbox.git
cd blackbox
```

### 2. Installation pour le développement

```bash
# Créer le venv et installer les dépendances dev
make install-dev
```

Cette commande :

- Crée un environnement virtuel `.venv`
- Installe toutes les dépendances (production + développement)
- Installe le package en mode éditable
- Configure les hooks pre-commit

### 3. Installation production uniquement

```bash
make install
```

## Vérification de l'installation

### Lancer les tests

```bash
make test
```

### Vérifier le linting

```bash
make lint
```

### Tester le CLI

```bash
# Activer le venv si ce n'est pas fait
source .venv/bin/activate

# Afficher l'aide
blackbox --help

# Vérifier le statut
blackbox status
```

### Tester l'API

```bash
# Démarrer le serveur
make run-api

# Dans un autre terminal, tester
curl http://localhost:8000/health
```

## Commandes Make disponibles

| Commande | Description |
|----------|-------------|
| `make install` | Installe les dépendances production |
| `make install-dev` | Installe les dépendances développement |
| `make test` | Lance les tests avec couverture |
| `make lint` | Vérifie le code avec ruff |
| `make format` | Formate le code |
| `make run-api` | Lance le serveur API |
| `make run-cli` | Lance le CLI |
| `make docs` | Sert la documentation localement |
| `make clean` | Nettoie les fichiers générés |

## Configuration

### Variables d'environnement

Créez un fichier `.env` à la racine du projet :

```bash
# Mode debug
DEBUG=true

# Configuration API
API_HOST=0.0.0.0
API_PORT=8000

# Base de données PostgreSQL
DATABASE_URL_SYNC=postgresql+psycopg2://blackbox:blackbox_dev@localhost:5432/blackbox

# Configuration trading (à venir)
# EXCHANGE_API_KEY=your_key
# EXCHANGE_SECRET=your_secret
```

### Configuration PostgreSQL

1. **Créer la base de données :**

```bash
# Se connecter à PostgreSQL
psql -U postgres

# Créer l'utilisateur et la base
CREATE USER blackbox WITH PASSWORD 'blackbox_dev';
CREATE DATABASE blackbox OWNER blackbox;
\q
```

2. **Exécuter les migrations :**

```bash
# Appliquer toutes les migrations
blackbox db migrate

# Vérifier le statut
blackbox db migrate-status
```

> **Note :** Les migrations utilisent [Alembic](https://alembic.sqlalchemy.org/) et sont versionnées dans `src/blackbox/data/storage/migrations/`.

### Première exécution

Après l'installation et la configuration de la base de données :

```bash
# Récupérer les événements du mois en cours
blackbox calendar fetch

# Vérifier les données stockées
blackbox db stats
```

## Prochaines étapes

- Consultez l'[Architecture](architecture.md) pour comprendre la structure du projet
- Explorez les [Commandes CLI](cli/commands.md)
- Découvrez les [Endpoints API](api/endpoints.md)
