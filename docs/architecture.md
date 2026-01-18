# Architecture

Le Blackbox Trading Robot est organisé en monorepo Python avec une séparation claire des responsabilités.

## Vue d'ensemble

```
com.nicodevelop.blackbox/
├── src/blackbox/           # Code source
│   ├── core/               # Logique métier trading
│   ├── data/               # Module données (calendrier économique)
│   │   ├── scraper/        # Scrapers web
│   │   └── storage/        # Persistance PostgreSQL + migrations
│   ├── cli/                # Interface ligne de commande
│   └── api/                # API REST FastAPI
├── tests/                  # Tests unitaires et d'intégration
├── docs/                   # Documentation MkDocs
├── alembic.ini             # Configuration Alembic
└── scripts/                # Scripts utilitaires
```

## Modules

### Core (`src/blackbox/core/`)

Le module **core** contient toute la logique métier du trading :

- Stratégies de trading
- Gestion des signaux d'achat/vente
- Gestion du portefeuille
- Calculs de risque
- Connecteurs aux exchanges
- **Scoring fondamental** : Analyse des événements économiques

Ce module est indépendant et peut être utilisé par le CLI et l'API.

#### Scoring (`src/blackbox/core/scoring/`)

Le sous-module **scoring** calcule des scores fondamentaux par devise et des biais directionnels par paire :

```
scoring/
├── __init__.py       # Exports du module
├── config.py         # ScoringConfig (dataclass avec paramètres)
├── calculator.py     # Fonctions de calcul pures
└── service.py        # ScoringService (intégration repository)
```

**Composants principaux :**

- **ScoringConfig** : Configuration avec `half_life_hours`, `lookback_days`, `min_bias_threshold`
- **ScoringService** : Service principal qui intègre le repository d'événements
- **Fonctions de calcul** :
  - `calculate_decay()` : Décroissance temporelle exponentielle (0.5^(heures/demi-vie))
  - `calculate_event_force()` : Force d'un événement (surprise × poids × decay)
  - `calculate_currency_score()` : Score agrégé pour une devise
  - `calculate_pair_bias()` : Biais directionnel (base_score - quote_score)
  - `get_bias_signal()` : Signal BULLISH/BEARISH/NEUTRAL

**Flux de scoring :**

```
EventRepository → ScoringService → Scores par devise
                                 → Biais par paire
                                 → Signaux directionnels
```

### Data (`src/blackbox/data/`)

Le module **data** gère la récupération de données externes :

- **Calendrier économique** : Scraping des événements depuis Forex Factory
- **Modèles Pydantic** : `EconomicEvent`, `CalendarDay`, `CalendarMonth`
- **Configuration** : Gestion des délais, user-agents, timeouts
- **Browser Manager** : Utilise `undetected-chromedriver` pour éviter la détection bot

Structure du module :

```
data/
├── __init__.py
├── models.py             # Modèles Pydantic (EconomicEvent, EventType, etc.)
├── event_mapping.py      # Mapping événements → métadonnées (type, direction, poids)
├── scoring.py            # Calculs de scoring (surprise, etc.)
├── config.py             # Configuration scraper
├── exceptions.py         # Exceptions personnalisées
├── services.py           # CalendarService (orchestration scraper + DB)
├── scraper/
│   ├── base.py           # Classe abstraite BaseScraper
│   ├── browser.py        # Gestion navigateur
│   └── forex_factory.py  # Implémentation Forex Factory
└── storage/
    ├── database.py       # Connexion PostgreSQL + session factory
    ├── models.py         # Modèles SQLAlchemy (EconomicEventDB)
    ├── repository.py     # Pattern Repository (CRUD)
    └── migrations/       # Migrations Alembic
        ├── env.py
        ├── script.py.mako
        └── versions/     # Fichiers de migration versionnés
```

### Storage Layer

Le module **storage** gère la persistance des données :

- **SQLAlchemy 2.0+** : ORM moderne avec support des types Python natifs
- **Alembic** : Migrations de schéma versionnées
- **PostgreSQL** : Base de données cible
- **Pattern Repository** : Abstraction des opérations CRUD

Flux de données :

```
Scraper → Pydantic Models → Repository → SQLAlchemy → PostgreSQL
                ↑                            ↓
           (enrichissement)            (persistance)
           event_mapping.py
```

### CLI (`src/blackbox/cli/`)

Le module **CLI** fournit une interface ligne de commande basée sur [Click](https://click.palletsprojects.com/) :

- Commandes pour gérer le robot
- Configuration interactive
- Monitoring en temps réel

### API (`src/blackbox/api/`)

Le module **API** expose une API REST avec [FastAPI](https://fastapi.tiangolo.com/) :

- Documentation automatique (Swagger/OpenAPI) sur `/docs`
- CORS activé pour le développement

#### Endpoints disponibles

**Calendrier économique :**

| Endpoint | Description |
|----------|-------------|
| `GET /api/v1/calendar/month` | Événements d'un mois |
| `GET /api/v1/calendar/today` | Événements du jour |
| `POST /api/v1/calendar/refresh` | Rafraîchir les données |
| `GET /api/v1/calendar/stats` | Statistiques de la base |

**Scoring fondamental :**

| Endpoint | Description |
|----------|-------------|
| `GET /api/v1/scoring/currency/{currency}` | Score d'une devise |
| `GET /api/v1/scoring/pair/{base}/{quote}` | Biais d'une paire |
| `GET /api/v1/scoring/signal/{base}/{quote}` | Signal BULLISH/BEARISH/NEUTRAL |

**Paramètres de scoring :**

- `half_life_hours` (défaut: 48) - Demi-vie pour la décroissance temporelle
- `lookback_days` (défaut: 7) - Nombre de jours à analyser
- `min_bias_threshold` (défaut: 1.0) - Seuil pour générer un signal directionnel

**Exemple d'appel :**

```bash
# Score EUR avec décroissance de 24h sur 14 jours
curl "http://localhost:8000/api/v1/scoring/currency/EUR?half_life_hours=24&lookback_days=14"

# Signal EUR/USD avec seuil de 2.0
curl "http://localhost:8000/api/v1/scoring/signal/EUR/USD?min_bias_threshold=2.0"
```

## Flux de données

```
┌─────────────────────────────────────────────────────┐
│                    Utilisateur                       │
└─────────────────────────────────────────────────────┘
                    │                │
                    ▼                ▼
            ┌───────────┐    ┌───────────┐
            │    CLI    │    │    API    │
            └───────────┘    └───────────┘
                    │                │
                    └────────┬───────┘
                             ▼
                    ┌───────────────┐
                    │     Core      │
                    │  (Trading)    │
                    └───────────────┘
                             │
                             ▼
                    ┌───────────────┐
                    │   Exchange    │
                    │   (Externe)   │
                    └───────────────┘
```

## Technologies

| Composant | Technologie |
|-----------|-------------|
| Langage | Python 3.11+ |
| CLI | Click |
| API | FastAPI + Uvicorn |
| Modèles données | Pydantic |
| Base de données | PostgreSQL |
| ORM | SQLAlchemy 2.0+ |
| Migrations | Alembic |
| Scraping | Selenium + undetected-chromedriver |
| Parsing HTML | BeautifulSoup + lxml |
| Retry | Tenacity |
| Tests | Pytest |
| Linting | Ruff |
| Documentation | MkDocs Material |

## Principes de conception

### Séparation des préoccupations

Chaque module a une responsabilité unique :

- **Core** : Logique métier pure
- **CLI** : Présentation en ligne de commande
- **API** : Présentation HTTP/REST

### Testabilité

Le code est conçu pour être facilement testable :

- Injection de dépendances
- Interfaces claires entre modules
- Mocks pour les services externes

### Extensibilité

L'architecture permet d'ajouter facilement :

- Nouvelles stratégies de trading
- Nouveaux connecteurs d'exchange
- Nouvelles interfaces (Web, mobile, etc.)
