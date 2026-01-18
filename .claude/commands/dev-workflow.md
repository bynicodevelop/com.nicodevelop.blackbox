---
description: Workflow de developpement complet en 5 etapes (analyse, conception, implementation, test, documentation)
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, Task, TodoWrite, AskUserQuestion
argument-hint: <description de la tache>
---

# Dev Workflow

Workflow de developpement complet en 5 etapes pour la tache: $ARGUMENTS

## Processus

### Etape 1: Analyse 🔍
- Utiliser Task (Explore) pour analyser la codebase
- Identifier les fichiers pertinents
- Identifier les patterns existants
- Resumer les findings

### Etape 2: Conception 📐
- Proposer 2-3 approches techniques
- Lister avantages/inconvenients de chaque approche
- Demander validation utilisateur (AskUserQuestion)
- Documenter l'approche choisie

### Etape 3: Implementation ⚡
- Creer todo list (TodoWrite)
- Implementer fichier par fichier
- Respecter conventions: ruff (88 chars), double quotes, type hints
- Marquer chaque todo complete

### Etape 4: Test ✅
- Executer `make lint`
- Executer `make test`
- Corriger erreurs si necessaire
- Confirmer tous tests passent

### Etape 5: Documentation 📝
- Mettre a jour le site MkDocs dans `docs/` :
  - `docs/cli/commands.md` pour nouvelles commandes CLI
  - `docs/api/endpoints.md` pour nouveaux endpoints API
  - `docs/data/calendar.md` pour nouveaux modeles de donnees
  - `docs/architecture.md` si changement architectural
- Ajouter docstrings dans le code si necessaire
- Verifier avec `make docs` (serveur local port 8001)
- Afficher recapitulatif final des changements
