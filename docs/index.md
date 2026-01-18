# Blackbox Trading Robot

Bienvenue dans la documentation du **Blackbox Trading Robot**, un projet Python monorepo pour le trading algorithmique.

## Fonctionnalités

- **Core** : Logique métier du trading (stratégies, signaux, gestion de portefeuille)
- **CLI** : Interface ligne de commande pour piloter le robot
- **API** : API REST FastAPI pour l'intégration avec d'autres systèmes
- **Documentation** : Documentation complète avec MkDocs

## Installation rapide

```bash
# Cloner le repository
git clone https://github.com/nicodevelop/blackbox.git
cd blackbox

# Installer les dépendances
make install-dev

# Vérifier l'installation
make test
```

## Utilisation

### CLI

```bash
# Afficher l'aide
blackbox --help

# Vérifier le statut
blackbox status

# Lancer en mode simulation
blackbox run --dry-run --symbol BTC/USDT
```

### API

```bash
# Démarrer le serveur
make run-api

# Accéder à la documentation
# http://localhost:8000/docs
```

## Structure du projet

```
blackbox/
├── src/blackbox/
│   ├── core/       # Logique trading
│   ├── cli/        # Interface CLI
│   └── api/        # API REST
├── tests/          # Tests unitaires
└── docs/           # Documentation
```

## Liens utiles

- [Guide de démarrage](getting-started.md)
- [Architecture](architecture.md)
- [Commandes CLI](cli/commands.md)
- [Endpoints API](api/endpoints.md)
