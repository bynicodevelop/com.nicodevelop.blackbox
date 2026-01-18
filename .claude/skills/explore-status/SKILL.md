---
description: Liste les explorations YOLO actives
allowed-tools: Bash, Read, Glob
argument-hint:
---

# Explore Status

Affiche l'etat de toutes les explorations YOLO actives.

## Processus

### Etape 1: Lister les worktrees YOLO
- Executer: `git worktree list`
- Filtrer ceux qui contiennent "yolo-"
- Extraire les IDs

### Etape 2: Pour chaque exploration trouvee
- Extraire l'ID depuis le chemin du worktree
- Verifier si le process claude est encore actif (chercher dans les logs)
- Compter les fichiers modifies: `git diff main..yolo/$ID --stat | tail -1`
- Recuperer la date du dernier commit: `git log yolo/$ID -1 --format="%cr"`

### Etape 3: Afficher le tableau resume
Format:
```
EXPLORATIONS YOLO ACTIVES
=========================

ID        | Status    | Fichiers | Derniere activite
----------|-----------|----------|------------------
abc123    | En cours  | 5        | il y a 2 minutes
def456    | Termine   | 12       | il y a 1 heure

Total: 2 explorations actives

Commandes:
- Review: /explore-review <id>
- Logs:   tail -f ../logs/yolo-<id>.log
```

### Etape 4: Si aucune exploration
Afficher: "Aucune exploration YOLO active. Lancez-en une avec /explore-yolo <tache>"

## Notes
- Le status "En cours" est determine si le fichier log est encore en ecriture
- Le status "Termine" est determine si le log contient "YOLO exploration complete"
