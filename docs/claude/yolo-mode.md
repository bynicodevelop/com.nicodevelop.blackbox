# Mode YOLO (Explore YOLO)

Le mode YOLO permet a Claude Code de travailler de maniere autonome sur des taches complexes sans demander de confirmation a chaque etape. Ce mode est ideal pour les taches bien definies ou vous faites confiance a l'agent pour prendre des decisions.

## Commandes disponibles

| Commande | Description |
|----------|-------------|
| `/explore-yolo` | Demarre une session YOLO sur une nouvelle branche |
| `/explore-status` | Affiche le statut de la session YOLO en cours |
| `/explore-review` | Review et valide les changements effectues |

## Workflow complet

### 1. Demarrer une session YOLO

```bash
/explore-yolo <description de la tache>
```

Cette commande :

- Cree une nouvelle branche Git dediee (format: `yolo/<id-unique>`)
- Configure Claude Code en mode autonome
- Demarre l'execution de la tache sans interruptions

**Exemple :**

```bash
/explore-yolo Ajouter une commande CLI pour exporter les donnees en CSV
```

Claude va alors :

1. Analyser la codebase existante
2. Identifier les fichiers a modifier
3. Implementer la fonctionnalite
4. Ecrire les tests
5. Verifier que tout compile et passe les tests

### 2. Suivre la progression

Pendant que Claude travaille, vous pouvez verifier l'avancement :

```bash
/explore-status
```

Cette commande affiche :

- La branche YOLO active
- Les fichiers modifies
- Les taches completees
- Les taches en cours
- Les erreurs eventuelles

**Exemple de sortie :**

```
Session YOLO: yolo/91269117
Branche: yolo/91269117
Statut: En cours

Fichiers modifies:
  - src/blackbox/cli/main.py
  - src/blackbox/cli/commands/export.py (nouveau)
  - tests/cli/test_export.py (nouveau)

Progression:
  [x] Analyse de la codebase
  [x] Creation du module export
  [x] Implementation de la commande
  [ ] Ecriture des tests
  [ ] Verification lint/tests
```

### 3. Reviewer les changements

Une fois la tache terminee, reviewez les changements :

```bash
/explore-review
```

Cette commande permet de :

- Voir un resume de tous les changements effectues
- Consulter le diff complet
- Valider ou rejeter les modifications
- Merger dans la branche principale si approuve

**Options disponibles lors du review :**

- **Approuver** : Merge les changements dans la branche principale
- **Modifier** : Demander des ajustements specifiques
- **Rejeter** : Annuler tous les changements et supprimer la branche

## Bonnes pratiques

### Quand utiliser le mode YOLO

- Taches bien definies avec un scope clair
- Ajout de nouvelles fonctionnalites isolees
- Refactoring avec des regles precises
- Generation de tests pour du code existant
- Corrections de bugs simples

### Quand eviter le mode YOLO

- Modifications critiques en production
- Changements architecturaux majeurs
- Taches necessitant des decisions business
- Code touchant a la securite ou aux paiements

## Exemples pratiques

### Exemple 1 : Ajouter un endpoint API

```bash
/explore-yolo Creer un endpoint GET /api/v1/portfolio qui retourne le portfolio actuel avec les positions ouvertes
```

Claude va :

1. Analyser les endpoints existants dans `src/blackbox/api/`
2. Creer le nouveau endpoint en suivant les patterns existants
3. Ajouter les modeles Pydantic necessaires
4. Ecrire les tests unitaires
5. Mettre a jour la documentation OpenAPI

### Exemple 2 : Ajouter une commande CLI

```bash
/explore-yolo Ajouter une commande 'blackbox calendar --export json' pour exporter le calendrier economique
```

Claude va :

1. Examiner les commandes CLI existantes
2. Ajouter l'option `--export` a la commande calendar
3. Implementer l'export JSON
4. Tester la commande
5. Mettre a jour l'aide de la commande

### Exemple 3 : Refactoring

```bash
/explore-yolo Extraire la logique de validation des signaux dans un module dedie src/blackbox/core/validation.py
```

Claude va :

1. Identifier toute la logique de validation dispersee
2. Creer le nouveau module
3. Migrer le code en preservant les tests
4. Verifier que tous les tests passent

## Gestion des erreurs

Si Claude rencontre une erreur pendant l'execution :

1. La session est mise en pause
2. L'erreur est logguee dans le statut
3. Vous pouvez corriger manuellement ou relancer

```bash
# Voir l'erreur
/explore-status

# Reprendre apres correction manuelle
/explore-yolo --resume
```

## Configuration

Le mode YOLO respecte les configurations du projet :

- **Linting** : ruff avec les regles du projet
- **Tests** : pytest avec couverture
- **Pre-commit hooks** : executes avant chaque commit

## Securite

- Les changements sont toujours sur une branche separee
- Aucun push automatique vers `main` ou `master`
- Review obligatoire avant merge
- Possibilite de rollback complet

## Comparaison avec le mode standard

| Aspect | Mode Standard | Mode YOLO |
|--------|---------------|-----------|
| Confirmations | A chaque etape | Aucune |
| Branche | Branche courante | Nouvelle branche dediee |
| Vitesse | Plus lent | Plus rapide |
| Controle | Total | Apres coup |
| Ideal pour | Taches sensibles | Taches bien definies |
