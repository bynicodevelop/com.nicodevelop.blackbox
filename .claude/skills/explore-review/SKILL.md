---
description: Review et valide une exploration YOLO
allowed-tools: Bash, Read, Glob, AskUserQuestion
argument-hint: <id de l'exploration (ex: abc123)>
---

# Explore Review

Review une exploration YOLO et decide de merger ou rejeter.

## Processus

### Etape 1: Verification
- Verifier que l'ID est fourni dans $ARGUMENTS
- Verifier que le worktree existe: `test -d ../worktrees/yolo-$ID`
- Verifier que la branch existe: `git branch --list yolo/$ID`
- Verifier si l'agent est encore en cours (process actif ou log termine)

### Etape 2: Analyse des changements
- Afficher le resume des changements: `git diff main..yolo/$ID --stat`
- Compter les fichiers modifies
- Lister les fichiers touches

### Etape 3: Decision utilisateur
- Utiliser AskUserQuestion avec les options:
  - "Approve" - Merger les changements dans main
  - "Reject" - Supprimer l'exploration
  - "Voir diff complet" - Afficher le diff detaille avant de decider

### Etape 4: Si Approve
- Checkout main: `git checkout main`
- Merge avec message: `git merge yolo/$ID --no-ff -m "Merge exploration yolo/$ID"`
- Supprimer le worktree: `git worktree remove ../worktrees/yolo-$ID`
- Supprimer la branch: `git branch -d yolo/$ID`
- Supprimer le log: `rm -f ../logs/yolo-$ID.log`
- Confirmer le merge reussi

### Etape 5: Si Reject
- Supprimer le worktree (force): `git worktree remove --force ../worktrees/yolo-$ID`
- Supprimer la branch (force): `git branch -D yolo/$ID`
- Supprimer le log: `rm -f ../logs/yolo-$ID.log`
- Confirmer la suppression

## Notes
- Si "Voir diff complet" est choisi, afficher le diff puis reposer la question Approve/Reject
- Ne jamais merger automatiquement - toujours demander confirmation
- En cas de conflit de merge, informer l'utilisateur et proposer des options
