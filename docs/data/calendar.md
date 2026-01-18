# Calendrier Économique

Le module de calendrier économique permet de récupérer les événements économiques majeurs depuis [Forex Factory](https://www.forexfactory.com/calendar).

## Fonctionnalités

- Récupération des événements passés et futurs
- Filtrage par devise (USD, EUR, GBP, etc.)
- Filtrage par niveau d'impact (low, medium, high)
- Valeurs actual, forecast et previous
- Mode headless pour l'exécution en arrière-plan
- Gestion anti-détection bot (undetected-chromedriver)
- Délais aléatoires pour simuler un comportement humain

## Utilisation

### En Python

```python
from datetime import date
from blackbox.data import ForexFactoryScraper, Impact
from blackbox.data.config import ForexFactoryConfig, BrowserConfig

# Configuration personnalisée (optionnel)
config = ForexFactoryConfig(
    browser=BrowserConfig(headless=True),
)

# Utilisation avec context manager (recommandé)
with ForexFactoryScraper(config) as scraper:
    # Récupérer les événements du jour
    events = scraper.fetch_today()

    # Récupérer un mois complet
    calendar = scraper.fetch_month(2026, 1)

    # Filtrer par devise
    usd_events = calendar.filter_by_currency(["USD", "EUR"])

    # Filtrer par impact
    high_impact = calendar.filter_by_impact(Impact.HIGH)

    for event in high_impact:
        print(f"{event.date} {event.time} - {event.currency}: {event.event_name}")
        print(f"  Actual: {event.actual}, Forecast: {event.forecast}, Previous: {event.previous}")
```

### Via CLI

```bash
# Événements du jour
blackbox calendar today

# Mois complet
blackbox calendar fetch --year 2026 --month 1

# Filtres
blackbox calendar fetch -c USD -c EUR --impact high

# Sortie JSON
blackbox calendar today -j
```

### Via API

```bash
# Événements du jour
curl "http://localhost:8000/api/v1/calendar/today"

# Mois complet avec filtres
curl "http://localhost:8000/api/v1/calendar/month?year=2026&month=1&currencies=USD,EUR&high_impact_only=true"
```

## Modèles de données

### EconomicEvent

Représente un événement économique unique.

| Champ | Type | Description |
|-------|------|-------------|
| `date` | `date` | Date de l'événement |
| `time` | `time \| None` | Heure (None si "All Day") |
| `currency` | `str` | Devise concernée (2-5 caractères) |
| `impact` | `Impact` | Niveau d'impact |
| `event_name` | `str` | Nom de l'événement |
| `actual` | `float \| None` | Valeur réelle publiée (normalisée) |
| `forecast` | `float \| None` | Prévision (normalisée) |
| `previous` | `float \| None` | Valeur précédente (normalisée) |

## Normalisation des valeurs

Les valeurs économiques (`actual`, `forecast`, `previous`) sont automatiquement normalisées lors du parsing. Cela permet de manipuler directement des nombres pour les calculs de surprise ou d'analyse.

### Formats supportés

| Format brut | Valeur normalisée | Description |
|-------------|-------------------|-------------|
| `"223K"` | `223000.0` | Milliers |
| `"1.5M"` | `1500000.0` | Millions |
| `"-50B"` | `-50000000000.0` | Milliards (négatif) |
| `"2T"` | `2000000000000.0` | Trillions |
| `"2.5%"` | `0.025` | Pourcentage → décimal |
| `"-1.5%"` | `-0.015` | Pourcentage négatif |
| `"1,234.56"` | `1234.56` | Séparateurs de milliers |
| `"<0.1%"` | `0.001` | Opérateurs de comparaison ignorés |

### Utilisation

```python
from blackbox.data import ForexFactoryScraper

with ForexFactoryScraper() as scraper:
    events = scraper.fetch_today()

    for event in events:
        if event.actual is not None and event.forecast is not None:
            # Calcul de la surprise économique
            surprise = event.actual - event.forecast
            print(f"{event.event_name}: Surprise = {surprise}")
```

### Fonction utilitaire

Le module `normalizer` expose également des fonctions utilitaires :

```python
from blackbox.data.normalizer import normalize_value, format_normalized_value

# Normalisation
value = normalize_value("223K")  # -> 223000.0
value = normalize_value("2.5%")  # -> 0.025

# Formatage inverse
text = format_normalized_value(223000.0)  # -> "223.00K"
text = format_normalized_value(1500000.0, precision=1)  # -> "1.5M"
```

### Impact

Enum des niveaux d'impact :

| Valeur | Description |
|--------|-------------|
| `Impact.LOW` | Faible impact |
| `Impact.MEDIUM` | Impact moyen |
| `Impact.HIGH` | Fort impact |
| `Impact.HOLIDAY` | Jour férié |
| `Impact.UNKNOWN` | Non défini |

### CalendarDay

Événements d'une journée.

| Propriété | Type | Description |
|-----------|------|-------------|
| `date` | `date` | Date |
| `events` | `list[EconomicEvent]` | Liste des événements |
| `high_impact_events` | `list[EconomicEvent]` | Événements à fort impact |
| `has_high_impact` | `bool` | A des événements à fort impact |

### CalendarMonth

Calendrier mensuel complet.

| Propriété/Méthode | Type | Description |
|-------------------|------|-------------|
| `year` | `int` | Année |
| `month` | `int` | Mois (1-12) |
| `days` | `list[CalendarDay]` | Jours du mois |
| `all_events` | `list[EconomicEvent]` | Tous les événements |
| `high_impact_events` | `list[EconomicEvent]` | Événements à fort impact |
| `filter_by_currency(currencies)` | `list[EconomicEvent]` | Filtre par devise |
| `filter_by_impact(min_impact)` | `list[EconomicEvent]` | Filtre par impact minimum |

## Configuration

### ForexFactoryConfig

| Option | Type | Défaut | Description |
|--------|------|--------|-------------|
| `base_url` | `str` | `https://www.forexfactory.com/calendar` | URL de base |
| `max_retries` | `int` | `3` | Nombre de tentatives |
| `retry_delay` | `float` | `5.0` | Délai entre tentatives (secondes) |
| `cache_ttl` | `int` | `300` | Durée du cache (secondes) |
| `browser` | `BrowserConfig` | - | Configuration navigateur |
| `delays` | `ScraperDelays` | - | Configuration des délais |

### BrowserConfig

| Option | Type | Défaut | Description |
|--------|------|--------|-------------|
| `headless` | `bool` | `True` | Mode sans interface |
| `user_agent` | `str \| None` | `None` | User-agent personnalisé |
| `page_load_timeout` | `int` | `30` | Timeout chargement page (s) |
| `implicit_wait` | `int` | `10` | Attente implicite (s) |
| `window_width` | `int` | `1920` | Largeur fenêtre |
| `window_height` | `int` | `1080` | Hauteur fenêtre |

### ScraperDelays

Délais aléatoires pour simuler un comportement humain :

| Option | Type | Défaut | Description |
|--------|------|--------|-------------|
| `page_load_min/max` | `float` | `2.0/4.0` | Délai après chargement |
| `action_min/max` | `float` | `0.5/1.5` | Délai entre actions |
| `pagination_min/max` | `float` | `3.0/6.0` | Délai entre pages |

## Gestion des erreurs

Le module définit des exceptions spécifiques :

| Exception | Description |
|-----------|-------------|
| `ScraperError` | Erreur générique de scraping |
| `BrowserError` | Erreur liée au navigateur |
| `BrowserInitializationError` | Échec d'initialisation du navigateur |
| `PageLoadError` | Échec de chargement de page |
| `ParsingError` | Échec de parsing HTML |
| `BlockedError` | Requête bloquée (Cloudflare, etc.) |

## Prérequis

- Google Chrome installé sur le système
- ChromeDriver compatible (géré automatiquement par undetected-chromedriver)

## Notes techniques

### Anti-détection

Le scraper utilise plusieurs techniques pour éviter la détection :

1. **undetected-chromedriver** : Masque les signatures d'automatisation
2. **Rotation des user-agents** : Pool de user-agents réalistes
3. **Délais aléatoires** : Simule un comportement humain
4. **Options Chrome** : Désactive les fonctionnalités de détection

### Performance

- Le scraping d'un mois complet peut prendre plusieurs minutes
- Utilisez l'API avec le endpoint `/refresh` pour les tâches en arrière-plan
- Les filtres côté scraper (`currencies` dans `fetch_month`) réduisent les données retournées mais pas le temps de scraping
