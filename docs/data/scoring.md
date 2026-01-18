# Scoring

Le module de scoring fournit des fonctions pour calculer des scores liés aux événements économiques, notamment le **score de surprise**.

## Score de Surprise

Le score de surprise mesure l'écart entre le résultat réel (`actual`) et les attentes du marché (`forecast`), normalisé par la valeur du forecast.

### Formule

$$
\text{surprise} = \text{direction} \times \frac{\text{actual} - \text{forecast}}{|\text{forecast}|}
$$

Où :

- **actual** : Valeur réelle publiée
- **forecast** : Prévision du marché
- **direction** : Direction d'impact (+1 ou -1)

### Interprétation

| Valeur | Interprétation |
|--------|----------------|
| `> 0` | Surprise positive (bullish pour la devise si direction=+1) |
| `= 0` | Aucune surprise (actual = forecast) |
| `< 0` | Surprise négative (bearish pour la devise si direction=+1) |
| `None` | Calcul impossible (actual, forecast ou forecast=0) |

### Exemples

| actual | forecast | direction | surprise | Explication |
|--------|----------|-----------|----------|-------------|
| 300000 | 200000 | +1 | +0.50 | 50% au-dessus des attentes |
| 0.04 | 0.035 | -1 | -0.143 | Plus élevé = bearish (ex: inflation) |
| 0.002 | 0.003 | +1 | -0.333 | 33% en-dessous des attentes |
| None | 0.003 | +1 | None | actual non disponible |
| 0.002 | None | +1 | None | forecast non disponible |
| 0.002 | 0 | +1 | None | Division par zéro impossible |

## Utilisation

### Calcul automatique

Le score de surprise est **calculé automatiquement** lors de la création d'un `EconomicEvent` :

```python
from blackbox.data.models import EconomicEvent
from datetime import date

event = EconomicEvent(
    date=date(2026, 1, 15),
    currency="USD",
    event_name="Non-Farm Employment Change",
    actual=300000,
    forecast=200000,
    direction=+1,
    weight=10,
)

print(event.surprise)  # 0.5 (50% au-dessus des attentes)
```

### Fonction utilitaire

Le module `scoring` expose également la fonction de calcul directement :

```python
from blackbox.data.scoring import calculate_surprise

# Calcul manuel
surprise = calculate_surprise(
    actual=300000,
    forecast=200000,
    direction=+1
)
print(surprise)  # 0.5

# Cas où le calcul est impossible
surprise = calculate_surprise(actual=None, forecast=200000, direction=+1)
print(surprise)  # None

surprise = calculate_surprise(actual=100, forecast=0, direction=+1)
print(surprise)  # None (division par zéro)
```

### Filtrage par surprise

Exemple pour filtrer les événements avec une forte surprise :

```python
from blackbox.data import ForexFactoryScraper

with ForexFactoryScraper() as scraper:
    events = scraper.fetch_today()

    # Événements avec surprise > 10%
    big_surprises = [
        e for e in events
        if e.surprise is not None and abs(e.surprise) > 0.10
    ]

    for event in big_surprises:
        direction = "+" if event.surprise > 0 else ""
        print(f"{event.currency} {event.event_name}: {direction}{event.surprise:.1%}")
```

## Persistance

Le score de surprise est persisté en base de données dans la colonne `surprise` de la table `economic_events`.

### Migration

La migration `003_add_surprise_column` :

1. Ajoute la colonne `surprise` (FLOAT, nullable)
2. Calcule automatiquement le score pour les événements existants

```sql
-- Formule appliquée lors de la migration
UPDATE economic_events
SET surprise = direction * (actual - forecast) / ABS(forecast)
WHERE actual IS NOT NULL
  AND forecast IS NOT NULL
  AND forecast != 0;
```

### Mise à jour automatique

Lors de l'insertion ou de la mise à jour d'un événement via le repository, le score de surprise est :

1. Calculé automatiquement par le modèle Pydantic
2. Persisté dans la colonne `surprise`
3. Mis à jour si `actual` ou `forecast` change

## Cas d'utilisation

### Trading sur les surprises économiques

```python
def should_trade(event: EconomicEvent) -> bool:
    """Détermine si un événement justifie une action de trading."""
    if event.surprise is None:
        return False

    # Seuil de 20% de surprise
    if abs(event.surprise) < 0.20:
        return False

    # Événements à fort impact uniquement
    if event.weight < 8:
        return False

    return True
```

### Analyse des tendances

```python
def analyze_currency_surprises(events: list[EconomicEvent], currency: str) -> dict:
    """Analyse les surprises pour une devise."""
    currency_events = [e for e in events if e.currency == currency]
    surprises = [e.surprise for e in currency_events if e.surprise is not None]

    if not surprises:
        return {"count": 0, "avg": None, "positive_ratio": None}

    return {
        "count": len(surprises),
        "avg": sum(surprises) / len(surprises),
        "positive_ratio": sum(1 for s in surprises if s > 0) / len(surprises),
    }
```

## API Reference

### `calculate_surprise`

```python
def calculate_surprise(
    actual: float | None,
    forecast: float | None,
    direction: int,
) -> float | None:
    """
    Calcule le score de surprise normalisé.

    Args:
        actual: Valeur réelle publiée.
        forecast: Prévision du marché.
        direction: Direction d'impact (+1 ou -1).

    Returns:
        Score de surprise normalisé, ou None si le calcul est impossible.
    """
```

## Voir aussi

- [Calendrier Économique](calendar.md) - Modèle `EconomicEvent`
- [Architecture](../architecture.md) - Structure du module `data`
