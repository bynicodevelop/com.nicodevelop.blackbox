# Endpoints API

L'API REST du Blackbox Trading Robot est construite avec FastAPI.

## Démarrage

```bash
# Via Make
make run-api

# Ou directement
uvicorn blackbox.api.main:app --reload --port 8000
```

L'API est accessible sur `http://localhost:8000`.

## Documentation interactive

FastAPI génère automatiquement une documentation interactive :

- **Swagger UI** : [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc** : [http://localhost:8000/redoc](http://localhost:8000/redoc)

## Endpoints

### Général

#### `GET /`

Retourne les informations de l'API.

**Réponse :**

```json
{
  "name": "Blackbox Trading Robot API",
  "version": "0.1.0",
  "status": "running"
}
```

#### `GET /health`

Vérifie que l'API est opérationnelle.

**Réponse :**

```json
{
  "status": "healthy"
}
```

### Statut

#### `GET /api/v1/status`

Retourne le statut détaillé du robot.

**Réponse :**

```json
{
  "status": "ready",
  "version": "0.1.0",
  "trading": false,
  "active_strategies": []
}
```

### Stratégies

#### `GET /api/v1/strategies`

Liste toutes les stratégies disponibles.

**Réponse :**

```json
{
  "strategies": [],
  "message": "No strategies configured yet"
}
```

#### `POST /api/v1/strategies/{strategy_name}/start`

Démarre une stratégie de trading.

**Paramètres :**

| Paramètre | Type | Description |
|-----------|------|-------------|
| `strategy_name` | path | Nom de la stratégie |
| `dry_run` | query | Mode simulation (défaut: `true`) |

**Exemple :**

```bash
curl -X POST "http://localhost:8000/api/v1/strategies/ma_strategie/start?dry_run=true"
```

**Réponse :**

```json
{
  "message": "Strategy 'ma_strategie' start requested",
  "dry_run": true,
  "status": "not_implemented"
}
```

#### `POST /api/v1/strategies/{strategy_name}/stop`

Arrête une stratégie en cours.

**Paramètres :**

| Paramètre | Type | Description |
|-----------|------|-------------|
| `strategy_name` | path | Nom de la stratégie |

**Exemple :**

```bash
curl -X POST "http://localhost:8000/api/v1/strategies/ma_strategie/stop"
```

**Réponse :**

```json
{
  "message": "Strategy 'ma_strategie' stop requested",
  "status": "not_implemented"
}
```

### Calendrier économique

Le module calendrier permet de récupérer les événements économiques depuis Forex Factory.

#### `GET /api/v1/calendar/month`

Récupère le calendrier économique pour un mois donné.

**Paramètres :**

| Paramètre | Type | Description | Requis |
|-----------|------|-------------|--------|
| `year` | query | Année (2000-2100) | Oui |
| `month` | query | Mois (1-12) | Oui |
| `currencies` | query | Devises séparées par des virgules (ex: `USD,EUR`) | Non |
| `high_impact_only` | query | Uniquement les événements à fort impact | Non (défaut: `false`) |

**Exemple :**

```bash
curl "http://localhost:8000/api/v1/calendar/month?year=2026&month=1"

# Avec filtres
curl "http://localhost:8000/api/v1/calendar/month?year=2026&month=1&currencies=USD,EUR&high_impact_only=true"
```

**Réponse :**

```json
{
  "year": 2026,
  "month": 1,
  "total_events": 45,
  "events": [
    {
      "date": "2026-01-02",
      "time": "08:30:00",
      "currency": "USD",
      "impact": "high",
      "event_name": "Non-Farm Employment Change",
      "actual": "223K",
      "forecast": "215K",
      "previous": "212K"
    },
    ...
  ]
}
```

#### `GET /api/v1/calendar/today`

Récupère les événements économiques du jour.

**Paramètres :**

| Paramètre | Type | Description | Requis |
|-----------|------|-------------|--------|
| `currencies` | query | Devises séparées par des virgules | Non |
| `high_impact_only` | query | Uniquement les événements à fort impact | Non (défaut: `false`) |

**Exemple :**

```bash
curl "http://localhost:8000/api/v1/calendar/today"

# Avec filtres
curl "http://localhost:8000/api/v1/calendar/today?currencies=USD&high_impact_only=true"
```

**Réponse :**

```json
{
  "date": "2026-01-18",
  "total_events": 5,
  "events": [
    {
      "date": "2026-01-18",
      "time": "08:30:00",
      "currency": "USD",
      "impact": "high",
      "event_name": "Building Permits",
      "actual": null,
      "forecast": "1.45M",
      "previous": "1.42M"
    },
    ...
  ]
}
```

#### `POST /api/v1/calendar/refresh`

Déclenche un rafraîchissement en arrière-plan des données du calendrier.

**Paramètres :**

| Paramètre | Type | Description | Requis |
|-----------|------|-------------|--------|
| `year` | query | Année à rafraîchir | Non (défaut: année courante) |
| `month` | query | Mois à rafraîchir | Non (défaut: mois courant) |

**Exemple :**

```bash
curl -X POST "http://localhost:8000/api/v1/calendar/refresh?year=2026&month=1"
```

**Réponse :**

```json
{
  "status": "started",
  "message": "Calendar refresh started for 2026-01"
}
```

#### `GET /api/v1/calendar/refresh/status`

Vérifie le statut du dernier rafraîchissement.

**Exemple :**

```bash
curl "http://localhost:8000/api/v1/calendar/refresh/status"
```

**Réponse :**

```json
{
  "status": "completed",
  "message": "Successfully refreshed 2026-01"
}
```

**Statuts possibles :**

| Statut | Description |
|--------|-------------|
| `idle` | Aucun rafraîchissement en cours |
| `running` | Rafraîchissement en cours |
| `completed` | Rafraîchissement terminé avec succès |
| `error` | Erreur lors du rafraîchissement |

### Scoring fondamental

Le module scoring calcule des scores fondamentaux par devise et des biais directionnels par paire, basés sur les événements économiques avec décroissance temporelle.

#### `GET /api/v1/scoring/currency/{currency}`

Calcule le score fondamental d'une devise.

**Paramètres :**

| Paramètre | Type | Description | Requis |
|-----------|------|-------------|--------|
| `currency` | path | Code devise (ex: `USD`, `EUR`) | Oui |
| `half_life_hours` | query | Demi-vie pour la décroissance (heures) | Non (défaut: `48`) |
| `lookback_days` | query | Jours à analyser | Non (défaut: `7`) |

**Exemple :**

```bash
curl "http://localhost:8000/api/v1/scoring/currency/EUR"

# Avec paramètres personnalisés
curl "http://localhost:8000/api/v1/scoring/currency/USD?half_life_hours=24&lookback_days=14"
```

**Réponse :**

```json
{
  "currency": "EUR",
  "score": 2.7539,
  "reference_time": "2026-01-18T21:22:09.684849",
  "config": {
    "half_life_hours": 48.0,
    "lookback_days": 7
  }
}
```

**Interprétation du score :**

- Score positif → Sentiment haussier sur la devise
- Score négatif → Sentiment baissier sur la devise
- Score proche de 0 → Sentiment neutre

---

#### `GET /api/v1/scoring/pair/{base}/{quote}`

Calcule le biais directionnel d'une paire de devises.

**Paramètres :**

| Paramètre | Type | Description | Requis |
|-----------|------|-------------|--------|
| `base` | path | Devise de base (ex: `EUR` dans EURUSD) | Oui |
| `quote` | path | Devise de cotation (ex: `USD` dans EURUSD) | Oui |
| `half_life_hours` | query | Demi-vie pour la décroissance (heures) | Non (défaut: `48`) |
| `lookback_days` | query | Jours à analyser | Non (défaut: `7`) |

**Exemple :**

```bash
curl "http://localhost:8000/api/v1/scoring/pair/EUR/USD"
```

**Réponse :**

```json
{
  "base": "EUR",
  "quote": "USD",
  "pair": "EURUSD",
  "base_score": 2.7539,
  "quote_score": 32.6464,
  "bias": -29.8925,
  "reference_time": "2026-01-18T21:22:09.684849"
}
```

**Interprétation du biais :**

Le biais est calculé comme : `base_score - quote_score`

- Biais positif → Sentiment haussier sur la paire (base plus forte que quote)
- Biais négatif → Sentiment baissier sur la paire (quote plus forte que base)

---

#### `GET /api/v1/scoring/signal/{base}/{quote}`

Génère un signal de trading pour une paire de devises.

**Paramètres :**

| Paramètre | Type | Description | Requis |
|-----------|------|-------------|--------|
| `base` | path | Devise de base | Oui |
| `quote` | path | Devise de cotation | Oui |
| `half_life_hours` | query | Demi-vie pour la décroissance (heures) | Non (défaut: `48`) |
| `lookback_days` | query | Jours à analyser | Non (défaut: `7`) |
| `min_bias_threshold` | query | Seuil minimum pour générer un signal directionnel | Non (défaut: `1.0`) |

**Exemple :**

```bash
curl "http://localhost:8000/api/v1/scoring/signal/EUR/USD"

# Avec seuil personnalisé
curl "http://localhost:8000/api/v1/scoring/signal/EUR/USD?min_bias_threshold=5.0"
```

**Réponse :**

```json
{
  "base": "EUR",
  "quote": "USD",
  "pair": "EURUSD",
  "bias": -29.8925,
  "signal": "BEARISH",
  "threshold": 1.0,
  "reference_time": "2026-01-18T21:22:09.684849"
}
```

**Signaux possibles :**

| Signal | Condition |
|--------|-----------|
| `BULLISH` | biais > seuil |
| `BEARISH` | biais < -seuil |
| `NEUTRAL` | \|biais\| ≤ seuil |

## Codes HTTP

| Code | Signification |
|------|---------------|
| 200 | Succès |
| 400 | Requête invalide |
| 404 | Ressource non trouvée |
| 500 | Erreur serveur |
| 503 | Service indisponible (erreur scraper) |

## Authentification

!!! warning "À venir"
    L'authentification n'est pas encore implémentée.
    Les endpoints sont actuellement ouverts.

## CORS

L'API accepte les requêtes de toutes origines par défaut. Cette configuration doit être restreinte en production.
