# Items API - CI/CD Pipeline

![CI](https://github.com/Leozmee/brief-ci-cd-semantic-release-mkdocs/workflows/CI/badge.svg)
![Build](https://github.com/Leozmee/brief-ci-cd-semantic-release-mkdocs/workflows/Build%20%26%20Push%20Docker%20Image/badge.svg)
![Release](https://github.com/Leozmee/brief-ci-cd-semantic-release-mkdocs/workflows/Semantic%20Release/badge.svg)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)

API REST simple pour gérer des items (CRUD), développée dans le cadre d'un brief sur les pipelines CI/CD professionnelles.

## Le projet

Une API FastAPI avec PostgreSQL qui permet de créer, lire, mettre à jour et supprimer des items. Rien de compliqué côté fonctionnel, mais avec une pipeline CI/CD complète qui automatise tout.

## Ce qui a été mis en place

### Pipeline CI
Chaque push ou pull request déclenche 5 jobs en parallèle :
- Pre-commit checks (hooks Git)
- Linting avec Ruff
- Type checking avec Mypy
- Scan de sécurité avec Bandit
- Tests avec pytest + couverture de code

### Pre-commit hooks
Les hooks Git vérifient le code avant chaque commit. Ça bloque si y'a des problèmes et ça corrige automatiquement quand c'est possible. Gain de temps énorme par rapport à attendre que la CI plante.

### Semantic Release
Le versionnage est complètement automatique. Quand on merge dans main, semantic-release analyse les commits (feat, fix, etc.) et crée automatiquement :
- La nouvelle version
- Le tag Git
- La release GitHub
- Le CHANGELOG

### Docker
L'image Docker se build automatiquement et se publie sur GitHub Container Registry à chaque push sur main ou develop.

Image disponible : `ghcr.io/leozmee/brief-ci-cd-semantic-release-mkdocs:main`

## Installation

Le projet utilise [uv](https://docs.astral.sh/uv/), un gestionnaire de packages Python moderne et ultra rapide.

```bash
# Cloner le repo
git clone https://github.com/Leozmee/brief-ci-cd-semantic-release-mkdocs.git
cd brief-ci-cd-semantic-release-mkdocs

# Installer uv (si pas déjà fait)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Installer les dépendances
uv sync

# Installer les pre-commit hooks
uv run pre-commit install
```

## Lancer l'API

### Avec Docker Compose (recommandé)

```bash
# Démarrer PostgreSQL
docker compose up -d db

# Lancer l'API
uv run fastapi dev app/main.py --port 8001
```

L'API est dispo sur http://localhost:8001

La doc interactive : http://localhost:8001/docs

### Avec Docker uniquement

```bash
docker pull ghcr.io/leozmee/brief-ci-cd-semantic-release-mkdocs:main
docker run -p 8000:8000 ghcr.io/leozmee/brief-ci-cd-semantic-release-mkdocs:main
```

## Tests

```bash
# Lancer les tests
uv run pytest

# Avec la couverture
uv run pytest --cov=app --cov-report=term
```

Actuellement 8 tests, 73% de couverture.

## Outils utilisés

- **uv** : Gestion des dépendances (10-100x plus rapide que pip)
- **Ruff** : Linting + formatage (remplace flake8, isort, black)
- **Mypy** : Type checking
- **Bandit** : Scan de sécurité
- **pytest** : Tests unitaires
- **pre-commit** : Hooks Git automatiques
- **python-semantic-release** : Versionnage automatique
- **GitHub Actions** : CI/CD

Pourquoi ces choix ? Voir [Livraison/COMPARATIF_OUTILS.md](Livraison/COMPARATIF_OUTILS.md)

## Stratégie de branches

On suit un GitFlow simplifié :
- `main` : Production, releases uniquement
- `develop` : Intégration continue
- `feature/*` : Branches de fonctionnalités

Les branches `main` et `develop` sont protégées, impossible de push directement dessus.

## Workflow de développement

```bash
# Créer une branche depuis develop
git checkout develop
git pull origin develop
git checkout -b feature/ma-feature

# Développer + commits conventionnels
git commit -m "feat: ajouter pagination"

# Push et créer une PR vers develop
git push -u origin feature/ma-feature
```

La CI se lance automatiquement. Si tout passe, on peut merger.

Quand on est prêt pour une release, on fait une PR de `develop` vers `main`. Une fois mergée, semantic-release crée automatiquement la nouvelle version.

## Conventional Commits

Les messages de commit suivent la spec Conventional Commits :

- `feat:` → nouvelle fonctionnalité (bump MINOR)
- `fix:` → correction de bug (bump PATCH)
- `feat!:` → breaking change (bump MAJOR)
- `docs:`, `style:`, `refactor:`, `test:`, `chore:` → pas de bump

## Structure du projet

```
.
├── app/
│   ├── main.py              # Point d'entrée FastAPI
│   ├── database.py          # Config DB
│   ├── models/              # Modèles SQLModel
│   ├── routes/              # Endpoints API
│   ├── schemas/             # Schémas Pydantic
│   └── services/            # Logique métier
├── tests/
│   └── test_api.py          # Tests unitaires
├── .github/workflows/       # Workflows CI/CD
├── Livraison/               # Documents du brief
└── pyproject.toml           # Config projet + outils
```

## Releases

Les releases sont créées automatiquement : [Releases](https://github.com/Leozmee/brief-ci-cd-semantic-release-mkdocs/releases)

Dernière version : [v1.0.0](https://github.com/Leozmee/brief-ci-cd-semantic-release-mkdocs/releases/tag/v1.0.0)

## Documentation du brief

- [VEILLE_CICD.md](Livraison/VEILLE_CICD.md) : Recherches sur CI/CD, uv, semantic release
- [PROBLEMES_DETECTES.md](Livraison/PROBLEMES_DETECTES.md) : Analyse des problèmes du code initial
- [COMPARATIF_OUTILS.md](Livraison/COMPARATIF_OUTILS.md) : Justification des choix techniques

## Commandes utiles

```bash
# Vérifier le code localement
uv run ruff check .
uv run ruff format .
uv run mypy app/
uv run bandit -r app/

# Pre-commit sur tous les fichiers
uv run pre-commit run --all-files

# Tester l'API
curl http://localhost:8001/health
curl http://localhost:8001/items

# Créer un item
curl -X POST http://localhost:8001/items \
  -H "Content-Type: application/json" \
  -d '{"nom": "Laptop", "prix": 999.99}'
```

## Problèmes rencontrés

Quelques trucs qui ont coincé :
- Tag Docker invalide avec semantic-release → résolu en retirant le prefix de branch
- Build command qui faisait planter → désactivé car c'est une app, pas une lib Python
- Safety v3 devenu payant → remplacé par Bandit uniquement

## Améliorations possibles

- Documentation avec MkDocs (Phase 7 du brief)
- Déploiement sur Azure Container Apps (Phase 8)
- Augmenter la couverture de tests à 90%+
- Ajouter Trivy pour scanner l'image Docker

## Licence

Projet éducatif dans le cadre d'un brief CI/CD.
