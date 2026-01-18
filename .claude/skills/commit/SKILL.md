---
description: Creer un commit Git avec un message bien structure
allowed-tools: Bash, AskUserQuestion
argument-hint: <message optionnel ou vide pour generation automatique>
---

# Commit Workflow

Workflow de creation de commit Git.

## Processus

### Etape 1: Analyse des changements 🔍
- Executer `git status` pour voir les fichiers modifies (sans -uall)
- Executer `git diff` pour voir les changements staged et unstaged
- Executer `git log --oneline -10` pour voir le style des commits recents

### Etape 2: Preparation du message 📝
- Si $ARGUMENTS est fourni, utiliser comme base du message
- Sinon, analyser les changements et generer un message:
  - Determiner le type: feat, fix, refactor, docs, test, chore, style
  - Resumer les changements de maniere concise (1-2 phrases)
  - Focus sur le "pourquoi" plutot que le "quoi"

### Etape 3: Validation utilisateur ✅
- Presenter le message de commit propose
- Demander confirmation avec AskUserQuestion
- Permettre modification si necessaire

### Etape 4: Creation du commit 🚀
- Ajouter les fichiers pertinents avec `git add`
- Ne PAS ajouter les fichiers sensibles (.env, credentials, etc.)
- Creer le commit avec le message valide
- Utiliser HEREDOC pour le message multi-ligne
- Ajouter le co-author: `Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>`
- Verifier avec `git status` apres le commit

## Regles importantes
- Ne JAMAIS faire de push automatique
- Ne JAMAIS utiliser --amend sauf demande explicite
- Ne JAMAIS utiliser --no-verify
- Toujours demander confirmation avant de commiter
