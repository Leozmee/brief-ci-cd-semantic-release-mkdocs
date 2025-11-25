# 🚀 Items CRUD API - CI/CD Professionnel

![CI](https://github.com/Leozmee/brief-ci-cd-semantic-release-mkdocs/workflows/CI/badge.svg)
![Build](https://github.com/Leozmee/brief-ci-cd-semantic-release-mkdocs/workflows/Build%20%26%20Push%20Docker%20Image/badge.svg)
![Release](https://github.com/Leozmee/brief-ci-cd-semantic-release-mkdocs/workflows/Semantic%20Release/badge.svg)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)
[![GitHub release](https://img.shields.io/github/v/release/Leozmee/brief-ci-cd-semantic-release-mkdocs)](https://github.com/Leozmee/brief-ci-cd-semantic-release-mkdocs/releases)
[![Docker](https://img.shields.io/badge/Docker-GHCR-2496ED?logo=docker)](https://ghcr.io/leozmee/brief-ci-cd-semantic-release-mkdocs)

## 📖 Description

API REST CRUD professionnelle construite avec FastAPI et SQLModel pour la gestion d'articles, avec une **pipeline CI/CD complète automatisée**.

Ce projet démontre l'implémentation de bonnes pratiques DevOps modernes :
- ✅ Intégration Continue (CI) avec GitHub Actions
- ✅ Déploiement Continu (CD) avec releases automatiques
- ✅ Contrôle qualité à plusieurs niveaux
- ✅ Versionnage sémantique automatique
- ✅ Containerisation avec Docker

## 🏗️ Architecture CI/CD

```
┌─────────────────────────────────────────────────────┐
│              DÉVELOPPEMENT LOCAL                     │
│  • Pre-commit hooks (5s de feedback)                │
│  • Ruff, Mypy, Tests locaux                         │
└───────────────────┬─────────────────────────────────┘
                    │ git push
                    ▼
┌─────────────────────────────────────────────────────┐
│           PULL REQUEST → develop                     │
│                                                      │
│  ┌──────────┬──────────┬──────────┬──────────┐     │
│  │   LINT   │TYPECHECK │ SECURITY │  TESTS   │     │
│  │  Ruff    │  Mypy    │  Bandit  │ Pytest   │     │
│  └──────────┴──────────┴──────────┴──────────┘     │
│                                                      │
│  ┌─────────────────────────────────────────┐        │
│  │     Build & Push Docker → GHCR          │        │
│  └─────────────────────────────────────────┘        │
└───────────────────┬─────────────────────────────────┘
                    │ Merge
                    ▼
┌─────────────────────────────────────────────────────┐
│             MERGE dans main                          │
│                                                      │
│  1. CI s'exécute sur main                           │
│  2. Semantic Release analyse les commits            │
│  3. Version bump automatique (SemVer)               │
│  4. CHANGELOG.md généré                             │
│  5. Tag Git créé (v1.0.0)                           │
│  6. GitHub Release publiée                          │
│  7. develop synchronisé avec main                   │
└─────────────────────────────────────────────────────┘
```

## 🚀 Démarrage Rapide

### Prérequis

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) (gestionnaire de paquets moderne)
- Docker & Docker Compose
- PostgreSQL

### Installation

```bash
# Cloner le repository
git clone https://github.com/Leozmee/brief-ci-cd-semantic-release-mkdocs.git
cd brief-ci-cd-semantic-release-mkdocs

# Installer uv (si nécessaire)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Synchroniser les dépendances
uv sync

# Installer les pre-commit hooks
uv run pre-commit install

# Démarrer PostgreSQL
docker compose up -d db

# Lancer l'API
uv run fastapi dev app/main.py --port 8001
```

L'API sera disponible sur : http://localhost:8001

Documentation interactive : http://localhost:8001/docs

## 🐳 Utilisation avec Docker

### Depuis GitHub Container Registry

```bash
# Pull l'image depuis GHCR
docker pull ghcr.io/leozmee/brief-ci-cd-semantic-release-mkdocs:main

# Run le container
docker run -p 8000:8000 ghcr.io/leozmee/brief-ci-cd-semantic-release-mkdocs:main
```

### Build local

```bash
# Build l'image
docker build -t items-api:local .

# Run avec docker-compose
docker compose up
```

## 📊 Qualité du Code

### Métriques

- ✅ **Coverage** : 73%
- ✅ **Tests** : 8 tests unitaires
- ✅ **Linting** : Ruff (0 erreurs)
- ✅ **Type checking** : Mypy (0 erreurs)
- ✅ **Security** : Bandit (0 vulnérabilités critiques)

### Outils de Qualité

| Outil | Usage | Configuration |
|-------|-------|---------------|
| **Ruff** | Linting & Formatting | [pyproject.toml](pyproject.toml#L31-L49) |
| **Mypy** | Type checking | [pyproject.toml](pyproject.toml#L51-L57) |
| **Bandit** | Security scanning | Ligne de commande |
| **Pytest** | Tests unitaires | [pyproject.toml](pyproject.toml#L59-L63) |
| **Pre-commit** | Git hooks | [.pre-commit-config.yaml](.pre-commit-config.yaml) |

### Commandes de Qualité

```bash
# Linting
uv run ruff check .

# Formatage
uv run ruff format .

# Type checking
uv run mypy app/

# Tests avec coverage
uv run pytest --cov=app --cov-report=term

# Pre-commit sur tous les fichiers
uv run pre-commit run --all-files
```

## 🔄 Workflow Git

### Conventional Commits

Ce projet utilise [Conventional Commits](https://www.conventionalcommits.org/) pour le versionnage automatique :

```bash
# Nouvelle fonctionnalité (MINOR bump)
git commit -m "feat: add pagination to items list"

# Correction de bug (PATCH bump)
git commit -m "fix: handle null values in database"

# Breaking change (MAJOR bump)
git commit -m "feat!: redesign API structure

BREAKING CHANGE: endpoints /api/v1/* are removed"
```

### Branches

- `main` : Production (protégée, releases seulement)
- `develop` : Intégration continue (protégée)
- `feature/*` : Nouvelles fonctionnalités
- `fix/*` : Corrections de bugs

### Processus de Contribution

1. Créer une branche depuis `develop`
   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b feature/ma-fonctionnalite
   ```

2. Développer avec pre-commit hooks actifs
   ```bash
   # Les hooks s'exécutent automatiquement à chaque commit
   git add .
   git commit -m "feat: add new feature"
   ```

3. Pousser et créer une PR vers `develop`
   ```bash
   git push -u origin feature/ma-fonctionnalite
   gh pr create --base develop
   ```

4. Attendre que la CI passe ✅

5. Merger la PR

6. Pour une release : PR `develop` → `main`

## 📦 Releases

Les releases sont **100% automatiques** grâce à [python-semantic-release](https://python-semantic-release.readthedocs.io/).

### Dernière Release

**[v1.0.0](https://github.com/Leozmee/brief-ci-cd-semantic-release-mkdocs/releases/tag/v1.0.0)** - 2025-11-25
- Initial Release
- Pipeline CI/CD complète
- Docker build & push automatique
- Pre-commit hooks configurés

### Processus de Release

Quand vous mergez `develop` → `main` :
1. ✅ CI s'exécute et passe
2. 🤖 Semantic Release analyse les commits
3. 📈 Version bump automatique basé sur les conventional commits
4. 📝 CHANGELOG.md mis à jour automatiquement
5. 🏷️ Tag Git créé (ex: v1.0.0)
6. 🚀 GitHub Release publiée
7. 🐳 Image Docker taggée avec la version
8. 🔄 develop synchronisé avec main

## 🛠️ Stack Technique

### Backend
- **FastAPI** 0.121+ - Framework web moderne et rapide
- **SQLModel** 0.0.27 - ORM avec Pydantic
- **PostgreSQL** 15 - Base de données relationnelle
- **Psycopg2** 2.9+ - Driver PostgreSQL

### DevOps
- **GitHub Actions** - CI/CD pipeline
- **Docker** - Containerisation
- **GitHub Container Registry** - Registry d'images Docker
- **uv** - Gestionnaire de paquets Python ultra-rapide

### Qualité
- **Ruff** - Linting & formatting (10-100x plus rapide que Black)
- **Mypy** - Type checking statique
- **Bandit** - Security scanning
- **Pytest** - Framework de tests
- **Pre-commit** - Git hooks automatiques

## 📂 Structure du Projet

```
brief-ci-cd-semantic-release-mkdocs/
├── .github/
│   └── workflows/
│       ├── ci.yml                    # Pipeline CI (5 jobs)
│       ├── build.yml                 # Docker build & push
│       ├── release.yml               # Semantic release
│       └── sync-develop.yml          # Sync develop ← main
├── app/
│   ├── main.py                       # Point d'entrée FastAPI
│   ├── database.py                   # Configuration DB
│   ├── models/
│   │   └── item.py                  # Modèles SQLModel
│   ├── routes/
│   │   └── items.py                 # Routes API CRUD
│   ├── schemas/
│   │   └── item.py                  # Schémas Pydantic
│   └── services/
│       └── item_service.py          # Logique métier
├── tests/
│   └── test_api.py                   # Tests unitaires
├── Livraison/
│   ├── PROBLEMES_DETECTES.md        # Analyse Phase 1
│   └── LIVRAISON_FINALE.md          # Document de livraison
├── .pre-commit-config.yaml           # Configuration pre-commit
├── pyproject.toml                    # Dépendances + config outils
├── docker-compose.yml                # PostgreSQL + App
├── Dockerfile                        # Image Docker
└── CHANGELOG.md                      # Généré automatiquement
```

## 📚 Documentation

- **Brief du projet** : [BRIEF_CI_CD_V2.md](BRIEF_CI_CD_V2.md)
- **Problèmes détectés** : [Livraison/PROBLEMES_DETECTES.md](Livraison/PROBLEMES_DETECTES.md)
- **Travail réalisé** : [claude.md](claude.md)
- **Changelog** : [CHANGELOG.md](CHANGELOG.md)
- **Livraison finale** : [Livraison/LIVRAISON_FINALE.md](Livraison/LIVRAISON_FINALE.md)

## 🔗 Liens Utiles

- **Repository** : https://github.com/Leozmee/brief-ci-cd-semantic-release-mkdocs
- **Releases** : https://github.com/Leozmee/brief-ci-cd-semantic-release-mkdocs/releases
- **Actions** : https://github.com/Leozmee/brief-ci-cd-semantic-release-mkdocs/actions
- **Packages** : https://github.com/Leozmee?tab=packages
- **Docker Images** : https://ghcr.io/leozmee/brief-ci-cd-semantic-release-mkdocs

## 👨‍💻 Développé avec

- [FastAPI](https://fastapi.tiangolo.com/)
- [uv](https://docs.astral.sh/uv/)
- [Ruff](https://docs.astral.sh/ruff/)
- [GitHub Actions](https://github.com/features/actions)
- [Python Semantic Release](https://python-semantic-release.readthedocs.io/)
- ❤️ et ☕

## 📄 License

Ce projet est un projet pédagogique dans le cadre d'une formation DevOps.

---

**🤖 Projet réalisé avec [Claude Code](https://claude.com/claude-code)**
