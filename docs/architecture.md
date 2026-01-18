# Architecture

Le Blackbox Trading Robot est organisé en monorepo Python avec une séparation claire des responsabilités.

## Vue d'ensemble

```
com.nicodevelop.blackbox/
├── src/blackbox/           # Code source
│   ├── core/               # Logique métier trading
│   ├── data/               # Module données (calendrier économique)
│   │   └── scraper/        # Scrapers web
│   ├── cli/                # Interface ligne de commande
│   └── api/                # API REST FastAPI
├── tests/                  # Tests unitaires et d'intégration
├── docs/                   # Documentation MkDocs
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

Ce module est indépendant et peut être utilisé par le CLI et l'API.

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
├── models.py           # Modèles Pydantic
├── config.py           # Configuration scraper
├── exceptions.py       # Exceptions personnalisées
└── scraper/
    ├── base.py         # Classe abstraite BaseScraper
    ├── browser.py      # Gestion navigateur
    └── forex_factory.py # Implémentation Forex Factory
```

### CLI (`src/blackbox/cli/`)

Le module **CLI** fournit une interface ligne de commande basée sur [Click](https://click.palletsprojects.com/) :

- Commandes pour gérer le robot
- Configuration interactive
- Monitoring en temps réel

### API (`src/blackbox/api/`)

Le module **API** expose une API REST avec [FastAPI](https://fastapi.tiangolo.com/) :

- Endpoints pour contrôler le robot
- Documentation automatique (Swagger/OpenAPI)
- Authentification (à implémenter)

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
