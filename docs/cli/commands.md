# Commandes CLI

Le Blackbox Trading Robot dispose d'une interface ligne de commande complète.

## Installation

Après installation du projet, la commande `blackbox` est disponible :

```bash
# Avec le venv activé
blackbox --help

# Ou via Make
make run-cli
```

## Commandes disponibles

### `blackbox --help`

Affiche l'aide générale et la liste des commandes.

```bash
$ blackbox --help
Usage: blackbox [OPTIONS] COMMAND [ARGS]...

  Blackbox Trading Robot CLI.

  A command-line interface for managing and running trading strategies.

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.

Commands:
  backtest  Run backtesting for a strategy.
  calendar  Economic calendar commands.
  run       Start the trading robot.
  status    Display the current status of the trading robot.
```

### `blackbox --version`

Affiche la version du robot.

```bash
$ blackbox --version
blackbox, version 0.1.0
```

### `blackbox status`

Affiche le statut actuel du robot.

```bash
$ blackbox status
Blackbox Trading Robot
Version: 0.1.0
Status: Ready
```

### `blackbox run`

Lance le robot de trading.

**Options :**

| Option | Description | Défaut |
|--------|-------------|--------|
| `-s, --symbol` | Paire de trading | `BTC/USDT` |
| `--dry-run` | Mode simulation | `false` |

**Exemples :**

```bash
# Mode simulation avec BTC/USDT
blackbox run --dry-run

# Mode simulation avec ETH/USDT
blackbox run --symbol ETH/USDT --dry-run

# Mode live (attention !)
blackbox run --symbol BTC/USDT
```

### `blackbox backtest`

Lance un backtest sur une stratégie.

**Arguments :**

| Argument | Description |
|----------|-------------|
| `STRATEGY_NAME` | Nom de la stratégie à tester |

**Exemple :**

```bash
blackbox backtest ma_strategie
```

## Calendrier économique

Le groupe de commandes `calendar` permet de récupérer les événements économiques depuis Forex Factory.

### `blackbox calendar fetch`

Récupère le calendrier économique pour un mois donné.

**Options :**

| Option | Description | Défaut |
|--------|-------------|--------|
| `-y, --year` | Année à récupérer | Année courante |
| `-m, --month` | Mois à récupérer (1-12) | Mois courant |
| `-c, --currency` | Filtrer par devise (peut être répété) | Toutes |
| `-i, --impact` | Niveau d'impact minimum (`low`, `medium`, `high`) | Tous |
| `--headless/--no-headless` | Mode navigateur sans interface | `true` |
| `-j, --json-output` | Sortie au format JSON | `false` |

**Exemples :**

```bash
# Récupérer le mois courant
blackbox calendar fetch

# Récupérer janvier 2026
blackbox calendar fetch --year 2026 --month 1

# Filtrer par devises USD et EUR
blackbox calendar fetch -c USD -c EUR

# Uniquement les événements à fort impact
blackbox calendar fetch --impact high

# Sortie JSON
blackbox calendar fetch -j
```

**Exemple de sortie :**

```
Fetching calendar for 2026-01...

Found 45 events:

[2026-01-02] [08:30] [USD] [!!!] Non-Farm Employment Change | A:223K F:215K P:212K
[2026-01-02] [10:00] [EUR] [!!] ECB President Speech | A:- F:- P:-
[2026-01-03] [14:00] [USD] [!] Treasury Budget Statement | A:-50B F:-45B P:-40B
...
```

### `blackbox calendar today`

Récupère les événements économiques du jour.

**Options :**

| Option | Description | Défaut |
|--------|-------------|--------|
| `-c, --currency` | Filtrer par devise | Toutes |
| `-H, --high-impact-only` | Uniquement les événements à fort impact | `false` |
| `--headless/--no-headless` | Mode navigateur sans interface | `true` |
| `-j, --json-output` | Sortie au format JSON | `false` |

**Exemples :**

```bash
# Événements du jour
blackbox calendar today

# Uniquement USD avec fort impact
blackbox calendar today -c USD --high-impact-only

# Sortie JSON
blackbox calendar today -j
```

**Légende des impacts :**

| Symbole | Impact |
|---------|--------|
| `!!!` | Fort (High) |
| `!!` | Moyen (Medium) |
| `!` | Faible (Low) |
| `H` | Jour férié |
| `?` | Inconnu |

## Codes de retour

| Code | Signification |
|------|---------------|
| 0 | Succès |
| 1 | Erreur générale |
| 2 | Erreur de configuration |

## Variables d'environnement

Le CLI respecte les variables d'environnement définies dans `.env` :

```bash
# Activer le mode debug
DEBUG=true

# Autres configurations à venir
```
