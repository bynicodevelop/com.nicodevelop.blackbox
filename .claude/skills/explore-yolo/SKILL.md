---
description: Lance une exploration YOLO dans un worktree isole
allowed-tools: Bash, Read, Glob, AskUserQuestion
argument-hint: <description de la tache a explorer>
---

# Explore YOLO

Lance un agent Claude en mode autonome dans un worktree Git isolé.

## Processus

### Etape 1: Preparation
- Generer un ID unique (8 caracteres): `ID=$(uuidgen | cut -c1-8 | tr '[:upper:]' '[:lower:]')`
- Creer les dossiers si necessaire: `mkdir -p ../worktrees ../logs`
- Creer le worktree: `git worktree add -b yolo/$ID ../worktrees/yolo-$ID`

### Etape 2: Lancement agent YOLO
- Executer le script helper en background:
  ```bash
  nohup bash scripts/yolo-launcher.sh "../worktrees/yolo-$ID" "$ARGUMENTS" "../logs/yolo-$ID.log" > /dev/null 2>&1 &
  ```
- Noter le PID du process

### Etape 3: Confirmation
- Afficher les informations de session:
  - ID de session: $ID
  - Worktree: ../worktrees/yolo-$ID
  - Branch: yolo/$ID
  - Log: ../logs/yolo-$ID.log
- Afficher les commandes utiles:
  - Suivre les logs: `tail -f ../logs/yolo-$ID.log`
  - Voir le status: `/explore-status`
  - Faire la review: `/explore-review $ID`

## Notes importantes
- L'agent tourne en background et continue meme si tu fermes le terminal
- Review manuelle obligatoire avant merge
- Le cleanup est automatique apres la review
- Budget max par defaut: 20$ USD
- Turns max par defaut: 100
