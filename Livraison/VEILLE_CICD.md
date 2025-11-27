# Veille Technologique - CI/CD et uv

## 📋 Table des matières

### Partie 1 : CI/CD (Continuous Integration / Continuous Deployment)
1. [Qu'est-ce que la CI (Continuous Integration) ?](#quest-ce-que-la-ci-continuous-integration-)
2. [Qu'est-ce que le CD (Continuous Deployment/Delivery) ?](#quest-ce-que-le-cd-continuous-deploymentdelivery-)
3. [Pourquoi CI/CD est important ?](#pourquoi-cicd-est-important-)

### Partie 2 : uv - Gestionnaire de packages Python moderne
4. [Qu'est-ce que uv ?](#quest-ce-que-uv-)
5. [Différences avec pip/poetry/pipenv](#différences-avec-pippoerypipenv)
6. [Avantages de uv](#avantages-de-uv)
7. [uv et pyproject.toml](#uv-et-pyprojecttoml)
8. [uv dans GitHub Actions](#uv-dans-github-actions)

---

# PARTIE 1 : CI/CD

## Qu'est-ce que la CI (Continuous Integration) ?

**La Continuous Integration (Intégration Continue)** est une pratique de développement logiciel où les développeurs intègrent régulièrement leur code dans un dépôt partagé, idéalement plusieurs fois par jour. Chaque intégration est automatiquement vérifiée par un système automatisé qui exécute des tests et des validations.

### Définition technique

> "L'Intégration Continue est une pratique de développement logiciel qui consiste à intégrer fréquemment le travail des développeurs dans une branche principale, chaque intégration étant vérifiée par une construction automatisée (incluant les tests) pour détecter les erreurs d'intégration le plus rapidement possible."
> — Martin Fowler

### Le cycle CI typique

```
┌─────────────────┐
│ Développeur     │
│ fait un commit  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Déclenchement   │
│ du workflow CI  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Checkout code   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Install deps    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Linting         │ ← Vérifie le style de code
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Type checking   │ ← Vérifie les types (mypy)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Security scan   │ ← Détecte les vulnérabilités
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Run tests       │ ← Exécute les tests unitaires
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Build artifact  │ ← Construit l'application
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ ✅ Success      │
│ ou ❌ Failure   │
└─────────────────┘
```

### Quels problèmes résout-elle ?

#### 1. **Détection précoce des bugs**

**Problème :**
- Sans CI, les développeurs travaillent en isolation pendant des jours/semaines
- Les bugs d'intégration ne sont découverts qu'au moment du merge
- "Ça marche sur ma machine !" mais pas ailleurs

**Solution CI :**
```yaml
# Exemple : GitHub Actions qui détecte un bug immédiatement
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - run: pytest  # Les tests échouent → bug détecté en 2 minutes
```

**Avantage :** Bug détecté en **2 minutes** vs **2 semaines** avant le déploiement

#### 2. **"Integration Hell" (Enfer de l'intégration)**

**Problème :**
- 5 développeurs travaillent chacun pendant 2 semaines sur des branches
- Le jour du merge : 3 jours de conflits et de débogage
- Le projet est bloqué pendant la résolution

**Solution CI :**
- Intégrations fréquentes (plusieurs fois par jour)
- Conflits détectés et résolus immédiatement
- Le code est toujours dans un état "releasable"

**Exemple concret :**

| Sans CI | Avec CI |
|---------|---------|
| Merge tous les 15 jours | Merge 5 fois par jour |
| 50+ conflits | 0-2 conflits |
| 3 jours de résolution | 15 minutes de résolution |
| Projet bloqué | Projet fluide |

#### 3. **Manque de reproductibilité**

**Problème :**
- "Ça marche sur mon Mac mais pas sur ton Windows"
- Versions de dépendances différentes entre développeurs
- Configuration locale cachée dans des variables d'environnement

**Solution CI :**
```yaml
# Environnement contrôlé et reproductible
jobs:
  test:
    runs-on: ubuntu-latest  # Même OS pour tous
    steps:
      - run: uv sync --frozen  # Mêmes dépendances pour tous
      - run: pytest  # Mêmes tests pour tous
```

#### 4. **Baisse de qualité du code**

**Problème :**
- Code non testé mergé dans main
- Styles de code incohérents
- Vulnérabilités de sécurité non détectées

**Solution CI :**
```yaml
# Validation automatique de la qualité
jobs:
  quality:
    steps:
      - run: ruff check .        # Style de code
      - run: mypy .              # Vérification de types
      - run: bandit -r app       # Scan de sécurité
      - run: pytest --cov=80     # Couverture de tests minimum
```

#### 5. **Perte de temps en revue de code**

**Problème :**
- Les reviewers doivent vérifier manuellement le style, les types, etc.
- Temps perdu sur des problèmes automatisables
- Les vraies issues de logique passent inaperçues

**Solution CI :**
```yaml
# PR bloquée si les checks ne passent pas
required_status_checks:
  - Lint with Ruff
  - Type Check with Mypy
  - Tests with Pytest
```

**Résultat :** Les reviewers se concentrent sur la **logique métier**, pas sur les détails syntaxiques.

### Quels sont les principes clés ?

#### 1. **Single Source of Truth (Dépôt unique)**

- Tout le code est dans un seul dépôt Git (ou quelques dépôts bien organisés)
- Une seule branche principale (`main` ou `master`)
- Pas de code "caché" sur les machines des développeurs

```bash
# Principe : Le dépôt Git est la vérité absolue
git clone https://github.com/user/projet
# Tout est là, rien n'est caché
```

#### 2. **Commit fréquent sur la branche principale**

- Les développeurs poussent leur code **au minimum une fois par jour**
- Idéalement plusieurs fois par jour
- Pas de branches feature qui durent des semaines

```bash
# Mauvaise pratique
git checkout -b feature-massive
# ... 3 semaines plus tard ...
git merge feature-massive  # 🔥 Conflit géant

# Bonne pratique
git checkout -b feature-petite
# ... quelques heures plus tard ...
git merge feature-petite  # ✅ Merge fluide
```

#### 3. **Chaque commit déclenche un build automatique**

- Chaque `git push` déclenche automatiquement la CI
- Le build compile le code (si nécessaire) et exécute les tests
- Feedback en quelques minutes maximum

```yaml
# GitHub Actions s'exécute automatiquement
on:
  push:
    branches: [main, develop]
  pull_request:
```

#### 4. **Les builds doivent être rapides**

- **Cible : < 10 minutes**
- Si trop long, les développeurs n'attendent pas le résultat
- Utiliser le cache, paralléliser, optimiser

```yaml
# Optimisation : cache des dépendances
- uses: astral-sh/setup-uv@v4
  with:
    enable-cache: true  # Gain de 2-3 minutes

# Optimisation : jobs parallèles
jobs:
  lint:      # 30 secondes
  typecheck: # 45 secondes    } En parallèle = 1 minute total
  test:      # 1 minute
```

#### 5. **Tests automatisés exhaustifs**

- Tests unitaires (logique métier)
- Tests d'intégration (API, base de données)
- Tests de sécurité (vulnérabilités)
- Couverture de code minimum (ex: 80%)

```python
# Exemple : tests automatisés
def test_create_user():
    response = client.post("/users", json={"name": "Alice"})
    assert response.status_code == 201
    assert response.json()["name"] == "Alice"
```

#### 6. **Fix immédiat des builds cassés**

- Si la CI échoue, c'est la **priorité numéro 1**
- Personne ne push tant que le build n'est pas réparé
- Culture d'équipe : "main doit toujours être vert"

```bash
# La CI échoue sur main
❌ Tests failed on main

# Action immédiate
git revert abc123  # Annuler le commit problématique
# OU
git commit --fixup  # Fix rapide et push
```

#### 7. **Environnement de build identique à la production**

- La CI utilise la même version de Python que la prod
- Les mêmes dépendances (via lockfile)
- Les mêmes variables d'environnement

```dockerfile
# CI et production utilisent la même image
FROM python:3.13-slim
```

#### 8. **Tout le monde peut voir les résultats**

- Les résultats de CI sont visibles par toute l'équipe
- Badges de statut sur le README
- Notifications sur Slack/Discord

```markdown
# Badge CI sur le README
![CI](https://github.com/user/projet/workflows/CI/badge.svg)
```

### 3 exemples d'outils de CI

#### 1. **GitHub Actions** (le plus populaire pour GitHub)

**Avantages :**
- ✅ Intégré directement dans GitHub
- ✅ Gratuit pour les projets publics (2000 minutes/mois pour privés)
- ✅ Marketplace énorme d'actions réutilisables
- ✅ Matrice de tests (multi-OS, multi-versions)

**Exemple de workflow :**

```yaml
name: CI
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v4
      - run: uv sync
      - run: uv run pytest
```

**Utilisation :** GitHub, intégration native

#### 2. **GitLab CI/CD** (intégré à GitLab)

**Avantages :**
- ✅ CI/CD complet intégré à GitLab
- ✅ Runners auto-hébergés possibles
- ✅ Pipelines visuels
- ✅ Excellente intégration Kubernetes

**Exemple de pipeline :**

```yaml
# .gitlab-ci.yml
stages:
  - test
  - build
  - deploy

test:
  stage: test
  script:
    - uv sync
    - uv run pytest

build:
  stage: build
  script:
    - docker build -t myapp .

deploy:
  stage: deploy
  script:
    - kubectl apply -f k8s/
```

**Utilisation :** GitLab, équipes DevOps

#### 3. **CircleCI** (plateforme cloud)

**Avantages :**
- ✅ Très rapide (conteneurs optimisés)
- ✅ Cache intelligent
- ✅ Workflows complexes (fan-out, fan-in)
- ✅ Support multi-plateformes (Linux, macOS, Windows)

**Exemple de config :**

```yaml
# .circleci/config.yml
version: 2.1

jobs:
  test:
    docker:
      - image: cimg/python:3.13
    steps:
      - checkout
      - run: curl -LsSf https://astral.sh/uv/install.sh | sh
      - run: uv sync
      - run: uv run pytest

workflows:
  test-and-deploy:
    jobs:
      - test
```

**Utilisation :** Équipes nécessitant des workflows complexes

#### Tableau comparatif

| Outil | Hébergement | Prix (open source) | Intégration | Complexité |
|-------|-------------|-------------------|-------------|-----------|
| **GitHub Actions** | Cloud GitHub | Gratuit illimité | GitHub ⭐⭐⭐ | Facile |
| **GitLab CI/CD** | Cloud/Self-hosted | Gratuit 400 min/mois | GitLab ⭐⭐⭐ | Moyenne |
| **CircleCI** | Cloud | Gratuit 6000 min/mois | Multi-VCS ⭐⭐ | Moyenne |
| **Jenkins** | Self-hosted | Gratuit | Plugins ⭐ | Complexe |
| **Travis CI** | Cloud | Gratuit (limité) | GitHub ⭐⭐ | Facile |

**Autres outils populaires :**
- **Jenkins** : Très flexible, mais complexe à maintenir
- **Azure Pipelines** : Excellent pour l'écosystème Microsoft
- **Drone CI** : Léger, conteneurs Docker
- **Buildkite** : Hybride cloud + self-hosted

---

## Qu'est-ce que le CD (Continuous Deployment/Delivery) ?

Le **Continuous Deployment (CD)** et la **Continuous Delivery (CD)** sont deux pratiques complémentaires à la CI qui automatisent le déploiement du code.

### Différence entre Continuous Delivery et Continuous Deployment

#### Continuous Delivery (Livraison Continue)

**Définition :**
> "La Continuous Delivery est une pratique où le code est **toujours prêt à être déployé en production**, mais le déploiement final nécessite une **validation manuelle**."

**Processus :**

```
Code → CI → Build → Tests → Staging → [👤 Validation manuelle] → Production
```

**Caractéristiques :**
- ✅ Le code passe automatiquement par tous les tests
- ✅ Un artefact déployable est créé automatiquement
- ✅ Le code est déployé automatiquement sur un environnement de staging
- ⏸️ Un humain décide quand déployer en production (bouton "Deploy")

**Exemple de workflow :**

```yaml
name: Continuous Delivery

on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: docker build -t myapp:${{ github.sha }} .
      - run: docker push myapp:${{ github.sha }}

  deploy-staging:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - run: kubectl set image deployment/myapp myapp=myapp:${{ github.sha }}
    environment: staging  # Déployé automatiquement sur staging

  deploy-production:
    needs: deploy-staging
    runs-on: ubuntu-latest
    steps:
      - run: kubectl set image deployment/myapp myapp=myapp:${{ github.sha }}
    environment: production  # ⏸️ Nécessite validation manuelle
    if: github.event_name == 'workflow_dispatch'  # Déclenchement manuel
```

**Cas d'usage :**
- Applications critiques (banque, santé)
- Conformité réglementaire (validation obligatoire)
- Déploiements planifiés (maintenance window)

#### Continuous Deployment (Déploiement Continu)

**Définition :**
> "Le Continuous Deployment est une pratique où chaque changement de code qui passe les tests automatisés est **automatiquement déployé en production** sans intervention humaine."

**Processus :**

```
Code → CI → Build → Tests → Staging → Production (automatique)
```

**Caractéristiques :**
- ✅ Entièrement automatisé
- ✅ Pas d'intervention humaine
- ✅ Déploiements multiples par jour
- ⚡ Feedback ultra-rapide

**Exemple de workflow :**

```yaml
name: Continuous Deployment

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: uv sync
      - run: uv run pytest
      - run: uv run ruff check .

  deploy:
    needs: test
    if: success()  # Déployé automatiquement si les tests passent
    runs-on: ubuntu-latest
    steps:
      - run: docker build -t myapp .
      - run: docker push myapp
      - run: kubectl rollout restart deployment/myapp
      # 🚀 Déploiement automatique en production
```

**Cas d'usage :**
- SaaS web (Facebook, Netflix, Spotify)
- Applications à fort trafic nécessitant des itérations rapides
- Équipes matures avec tests exhaustifs

#### Tableau comparatif

| Critère | Continuous Delivery | Continuous Deployment |
|---------|--------------------|-----------------------|
| **Automatisation** | Partielle (jusqu'au staging) | Totale (jusqu'à la prod) |
| **Validation production** | ⏸️ Manuelle (humain) | ✅ Automatique (tests) |
| **Fréquence de déploiement** | À la demande (ex: hebdomadaire) | Plusieurs fois par jour |
| **Confiance requise** | Moyenne | Très élevée |
| **Complexité tests** | Moyenne | Très élevée |
| **Cas d'usage** | Applications critiques | SaaS, applications web |

**Exemple visuel :**

```
CONTINUOUS DELIVERY
┌────────┐   ┌────┐   ┌──────┐   ┌─────────┐   ┌────────────┐
│ Commit │──>│ CI │──>│ Build│──>│ Staging │──>│ [🚦 Manual]│──> Production
└────────┘   └────┘   └──────┘   └─────────┘   └────────────┘
                                     Auto           Click

CONTINUOUS DEPLOYMENT
┌────────┐   ┌────┐   ┌──────┐   ┌─────────┐   ┌────────────┐
│ Commit │──>│ CI │──>│ Build│──>│ Staging │──>│ Production │
└────────┘   └────┘   └──────┘   └─────────┘   └────────────┘
                                     Auto            Auto
```

### Quels sont les risques et bénéfices ?

#### ✅ Bénéfices du CD

##### 1. **Time to Market réduit**

**Sans CD :**
- Cycle de release de 2 semaines
- Planification, packaging, déploiement manuel
- Les features attendent dans une queue

**Avec CD :**
- Déploiement en quelques minutes après le merge
- Les utilisateurs ont accès aux features immédiatement
- Feedback rapide des utilisateurs

**Exemple concret :**
```
Feature "Nouveau bouton de partage"
Sans CD: 14 jours entre le code et les utilisateurs
Avec CD: 10 minutes entre le code et les utilisateurs
```

##### 2. **Réduction des risques de déploiement**

**Sans CD :**
- Gros déploiements avec 50+ changements
- Si ça casse, difficile de savoir quel changement est responsable
- Rollback complexe

**Avec CD :**
- Petits déploiements avec 1-5 changements
- Si ça casse, le coupable est évident
- Rollback simple (revert 1 commit)

**Statistiques :**
| Métrique | Sans CD | Avec CD |
|----------|---------|---------|
| Taille moyenne d'un déploiement | 200 lignes | 20 lignes |
| Temps de rollback | 2 heures | 5 minutes |
| Taux de succès | 70% | 95% |

##### 3. **Détection rapide des bugs en production**

**Sans CD :**
- Bug déployé avec 50 autres changements
- Découvert 3 jours plus tard
- Difficile à tracer

**Avec CD :**
- Bug déployé seul
- Découvert en 10 minutes (monitoring)
- Rollback immédiat

**Exemple :**
```
Déploiement automatique → Monitoring Sentry détecte une erreur → Alerte Slack
→ Rollback automatique en 2 minutes
```

##### 4. **Moins de stress pour les équipes**

**Sans CD :**
- "Deployment day" = jour de stress
- Toute l'équipe doit être présente
- Déploiements le week-end à 2h du matin

**Avec CD :**
- Déploiements routiniers et sans stress
- Pas de "deployment day" spécial
- Déploiements en pleine journée

##### 5. **Feedback rapide des utilisateurs**

**Sans CD :**
```
Idée → Dev (2 jours) → Review (1 jour) → Attente du prochain release (10 jours)
→ Déploiement → Feedback utilisateurs (après 13 jours)
```

**Avec CD :**
```
Idée → Dev (2 jours) → Review (1 jour) → Déploiement automatique
→ Feedback utilisateurs (après 3 jours)
```

#### ⚠️ Risques du CD

##### 1. **Déploiement automatique d'un bug critique**

**Risque :**
- Un bug critique passe les tests et arrive en production
- Impact immédiat sur les utilisateurs

**Mitigation :**
```yaml
# Feature flags pour désactiver rapidement une feature
if feature_flags.is_enabled("new_payment_flow"):
    new_payment_flow()
else:
    old_payment_flow()

# Canary deployment (déploiement progressif)
deploy:
  strategy:
    canary:
      steps:
        - 5%   # 5% des utilisateurs reçoivent la nouvelle version
        - 25%  # Si OK, 25%
        - 100% # Si OK, 100%
```

##### 2. **Surcharge de la surveillance (monitoring)**

**Risque :**
- Sans monitoring robuste, les bugs passent inaperçus
- Les équipes ne savent pas que la prod est cassée

**Mitigation :**
```yaml
# Monitoring obligatoire
- Sentry (erreurs)
- Prometheus + Grafana (métriques)
- CloudWatch / DataDog (logs)
- Alertes automatiques (Slack, PagerDuty)
```

##### 3. **Complexité technique élevée**

**Risque :**
- Pipeline CD complexe à maintenir
- Coût en infrastructure (CI/CD runners)
- Compétences DevOps nécessaires

**Mitigation :**
- Commencer simple (CI d'abord, CD ensuite)
- Utiliser des services managés (GitHub Actions, GitLab CI)
- Formation de l'équipe

##### 4. **Dépendance aux tests automatisés**

**Risque :**
- Si les tests sont mauvais, des bugs arrivent en production
- Fausse confiance dans les tests

**Mitigation :**
```python
# Tests de qualité avec bonne couverture
def test_payment_flow():
    # Test unitaire
    assert calculate_total([10, 20]) == 30

    # Test d'intégration
    response = client.post("/payment", json={"amount": 30})
    assert response.status_code == 201

    # Test E2E (end-to-end)
    playwright.goto("/checkout")
    playwright.click("button:has-text('Pay')")
    assert playwright.is_visible("text=Payment successful")
```

##### 5. **Conformité et audit**

**Risque :**
- Certaines industries (finance, santé) exigent des validations manuelles
- Le CD pur peut ne pas être conforme

**Mitigation :**
- Utiliser Continuous Delivery (validation manuelle) au lieu de Deployment
- Logs d'audit détaillés
- Approbations multi-niveaux dans GitHub Actions

```yaml
deploy-production:
  environment:
    name: production
    reviewers: [admin, security-team]  # Validation manuelle requise
```

#### Tableau récapitulatif

| Aspect | Bénéfices | Risques | Mitigation |
|--------|-----------|---------|------------|
| **Vitesse** | ✅ Déploiements rapides | ⚠️ Bugs déployés rapidement | Feature flags, canary |
| **Qualité** | ✅ Feedback rapide | ⚠️ Dépendance aux tests | Tests exhaustifs, monitoring |
| **Coût** | ✅ Moins de stress équipe | ⚠️ Infrastructure CI/CD | Services managés, start simple |
| **Conformité** | ✅ Traçabilité | ⚠️ Validation manuelle requise | Continuous Delivery, logs |

---

## Pourquoi CI/CD est important ?

### 1. Impact sur la qualité du code

#### 1.1. **Détection précoce des bugs**

**Sans CI/CD :**
```
Bug introduit (jour 1) → Découvert en QA (jour 15) → Fix (jour 16) → Re-test (jour 17)
Coût: 17 jours, 3 cycles de test
```

**Avec CI/CD :**
```
Bug introduit (minute 0) → CI échoue (minute 5) → Fix (minute 10) → CI passe (minute 15)
Coût: 15 minutes, 1 cycle de test
```

**Règle :** Plus un bug est détecté tôt, moins il coûte cher à corriger.

| Phase de détection | Coût relatif |
|-------------------|-------------|
| CI (avant merge) | 1x |
| QA (après merge) | 10x |
| Production | 100x |
| Client VIP touché | 1000x |

#### 1.2. **Automatisation des validations**

**Validations automatiques en CI :**

```yaml
quality-checks:
  steps:
    # 1. Style de code cohérent
    - run: ruff check .
    - run: ruff format --check .

    # 2. Vérification de types (moins de bugs runtime)
    - run: mypy app/

    # 3. Scan de sécurité
    - run: bandit -r app/
    - run: safety check

    # 4. Tests unitaires + couverture
    - run: pytest --cov=80

    # 5. Tests de régression
    - run: pytest tests/e2e/
```

**Résultat :**
- ✅ 0 erreurs de linting en production
- ✅ 0 vulnérabilités critiques non détectées
- ✅ 80% de couverture de code minimum
- ✅ Code cohérent (même style partout)

#### 1.3. **Code review facilité**

**Sans CI :**
```
Reviewer: "Il y a 15 imports non utilisés, reformate le fichier, et mypy trouve 8 erreurs"
Dev: "OK je corrige..." (2 heures perdues)
Reviewer: "OK maintenant on peut discuter de la logique métier"
```

**Avec CI :**
```
CI: ❌ "15 imports non utilisés, reformate nécessaire, 8 erreurs mypy"
Dev: corrige automatiquement (5 minutes)
CI: ✅ Tous les checks passent
Reviewer: "La logique métier a du sens, approuvé !"
```

**Gain :** Les reviewers se concentrent sur **la logique métier**, pas sur la syntaxe.

#### 1.4. **Documentation vivante**

**Le pipeline CI est une documentation :**

```yaml
# En regardant le pipeline, on comprend :
# - Quelles sont les commandes pour tester (uv run pytest)
# - Quelle version de Python (3.13)
# - Quelles dépendances (uv.lock)
# - Quels outils de qualité (ruff, mypy)
```

**Avantage :** Un nouveau développeur sait **immédiatement** comment tester le projet.

### 2. Impact sur la vitesse de développement

#### 2.1. **Cycles de feedback ultra-rapides**

**Sans CI/CD :**
```
Dev local (5 min) → Push → Attente review (2 jours) → Merge → Attente release (1 semaine)
→ Test QA (2 jours) → Bug trouvé → Retour au dev
CYCLE TOTAL: 10 jours
```

**Avec CI/CD :**
```
Dev local (5 min) → Push → CI automatique (3 min) → Review (2 heures)
→ Merge → Déploiement auto (2 min) → Monitoring détecte un problème (5 min)
→ Rollback auto (2 min)
CYCLE TOTAL: 3 heures
```

**Gain de vitesse : 80x plus rapide**

#### 2.2. **Déploiements fréquents**

**Statistiques de déploiement :**

| Organisation | Déploiements/jour | Approche |
|-------------|-------------------|----------|
| **Amazon** | 1 toutes les secondes | CD pur |
| **Netflix** | 1000+ par jour | CD pur |
| **Facebook** | 2x par jour | CD pur |
| **Enterprise traditionnelle** | 1 tous les 3 mois | Manuel |

**Exemple :**
```
Sans CI/CD: 4 déploiements par an = 4 opportunités de valeur ajoutée
Avec CI/CD: 500 déploiements par an = 500 opportunités de valeur ajoutée
```

#### 2.3. **Réduction du "Work In Progress" (WIP)**

**Sans CI/CD :**
- Les features s'accumulent dans des branches
- 10 features attendent le prochain "release day"
- Conflits géants au moment du merge

**Avec CI/CD :**
- Les features sont mergées dès qu'elles sont prêtes
- Max 2-3 features en cours
- Pas de conflits

**Illustration :**

```
SANS CI/CD (WIP élevé)
Main: ━━━━━━━━━━━━━━━━━━━━━━━━ (stagnante pendant 3 semaines)
       ┗━ Feature A (10 jours)
       ┗━ Feature B (12 jours)
       ┗━ Feature C (8 jours)
       ┗━ Feature D (15 jours)
           ↓
       Mega merge day 🔥

AVEC CI/CD (WIP faible)
Main: ━┯━┯━┯━┯━┯━┯━┯━┯━┯━┯━┯━┯━
      ├─┴─ Feature A (1 jour) ✅
      ├─┴─ Feature B (1 jour) ✅
      ├─┴─ Feature C (1 jour) ✅
      └─┴─ Feature D (1 jour) ✅
```

#### 2.4. **Élimination des tâches manuelles répétitives**

**Tâches automatisées par CI/CD :**

| Tâche | Temps manuel | Temps automatisé |
|-------|-------------|------------------|
| Linting du code | 10 min | 30 sec |
| Exécution des tests | 15 min | 2 min |
| Build de l'application | 20 min | 3 min |
| Déploiement sur staging | 30 min | 2 min |
| Vérification de sécurité | 1 heure | 1 min |
| Génération du CHANGELOG | 30 min | 10 sec |
| **TOTAL par déploiement** | **2h45** | **8 min** |

**Avec 50 déploiements par an :**
- Sans CI/CD : 137 heures perdues
- Avec CI/CD : 6.5 heures
- **Gain : 130 heures par an par développeur**

#### 2.5. **Confiance pour refactorer**

**Sans CI/CD :**
```
Dev: "Je veux refactorer ce vieux code..."
Dev: "Mais j'ai peur de casser quelque chose..."
Dev: "Je ne touche à rien" 😰
Résultat: Dette technique qui s'accumule
```

**Avec CI/CD :**
```
Dev: "Je refactore ce vieux code"
Dev: *refactore*
CI: ✅ Tous les tests passent
Dev: "Parfait, c'est déployé !" 😎
Résultat: Code qui s'améliore continuellement
```

### 3. Impact sur la collaboration en équipe

#### 3.1. **Transparence et visibilité**

**Statut visible par tous :**

```markdown
# README.md avec badges
![CI](https://github.com/user/projet/workflows/CI/badge.svg)
![Coverage](https://codecov.io/gh/user/projet/branch/main/graph/badge.svg)
![Release](https://img.shields.io/github/v/release/user/projet)
```

**Avantages :**
- ✅ Tout le monde sait si le build est cassé
- ✅ Les nouveaux contributeurs voient l'état de santé du projet
- ✅ Les managers ont une vue d'ensemble

#### 3.2. **Responsabilité partagée**

**Culture "Vous l'avez cassé, vous le réparez" :**

```
Alice push un commit → CI échoue → Notification Slack:
"❌ Build failed on main (commit abc123 by @Alice)"
Alice: "Oups, je fixe immédiatement !"
```

**Principe :**
- Celui qui casse le build a la **priorité absolue** pour le réparer
- Pas de "c'est le problème du QA"
- Ownership du code de bout en bout

#### 3.3. **Onboarding facilité des nouveaux développeurs**

**Nouveau développeur :**

```bash
# Jour 1
git clone https://github.com/team/projet
cd projet

# Le README explique :
# "Toutes les commandes sont dans .github/workflows/ci.yml"

# Il copie les commandes de la CI
uv sync
uv run pytest
uv run ruff check .

# ✅ En 5 minutes, il peut contribuer
```

**Sans CI/CD :**
```
Nouveau dev: "Comment je lance les tests ?"
Senior: "Euh... il faut installer PostgreSQL 14, puis..."
Nouveau dev: "Et l'environnement ?"
Senior: "Demande à Bob, lui seul sait..."
Nouveau dev: *frustré après 2 jours de setup*
```

#### 3.4. **Réduction des blocages inter-équipes**

**Sans CI/CD :**
```
Dev team: "On a fini la feature, elle passe en QA"
QA team: *teste pendant 3 jours*
QA team: "Bug trouvé, retour aux devs"
Dev team: "On ne peut pas travailler, on attend le feedback QA"
```

**Avec CI/CD :**
```
Dev: push → CI teste automatiquement → ✅ Passe → Déployé en staging
QA: Teste en staging en parallèle du dev de la prochaine feature
Pas de blocage !
```

#### 3.5. **Communication asynchrone**

**Les PR deviennent self-service :**

```
PR #42: "feat: add user authentication"
├─ ✅ CI passed (all checks green)
├─ ✅ Coverage 85% (+5%)
├─ 📊 Lighthouse score: 95/100
├─ 🔒 Security scan: no issues
└─ 📝 Preview deployment: https://pr-42.staging.app

Reviewer: "Les checks sont verts, le code a du sens, approved!"
```

**Avantage :** Le reviewer a **toutes les informations** sans avoir à exécuter le code localement.

#### 3.6. **Culture d'excellence technique**

**CI/CD encourage les bonnes pratiques :**

| Pratique | Sans CI/CD | Avec CI/CD |
|----------|-----------|------------|
| Tests unitaires | "On n'a pas le temps" | "Obligatoire pour merger" |
| Couverture de code | "Personne ne vérifie" | "Bloqué si < 80%" |
| Style de code | "Chacun son style" | "Formatage automatique" |
| Documentation | "Dépassée" | "Générée automatiquement" |
| Sécurité | "On verra plus tard" | "Scan à chaque commit" |

**Effet culturel :**
- Les développeurs juniors apprennent les bonnes pratiques **par osmose**
- Le code legacy est progressivement amélioré
- La qualité devient une **norme d'équipe**, pas une exception

---

# PARTIE 2 : uv - Gestionnaire de packages Python moderne

## Qu'est-ce que uv ?

**uv** est un gestionnaire de packages et d'environnements Python **extrêmement rapide**, développé par **Astral** (les créateurs de Ruff). Il est écrit en **Rust** pour des performances optimales.

### Caractéristiques principales

- 🚀 **10-100x plus rapide** que pip
- 📦 Gestionnaire de packages complet
- 🔒 Lockfile automatique (`uv.lock`)
- 🐍 Gestion des versions Python
- 🌐 Compatible avec l'écosystème Python existant
- ⚡ Téléchargements parallèles
- 💾 Cache global intelligent

### Installation

```bash
# Linux/macOS
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Via pip
pip install uv

# Homebrew (macOS)
brew install uv
```

---

## Différences avec pip/poetry/pipenv

| Fonctionnalité | **uv** | **pip** | **poetry** | **pipenv** |
|----------------|--------|---------|-----------|------------|
| **Langage** | Rust | Python | Python | Python |
| **Vitesse d'installation** | ⚡⚡⚡ | ⚡ | ⚡⚡ | ⚡⚡ |
| **Résolution de dépendances** | Très rapide | Lente | Rapide | Moyenne |
| **Lockfile** | ✅ `uv.lock` | ❌ | ✅ `poetry.lock` | ✅ `Pipfile.lock` |
| **Gestion de Python** | ✅ Built-in | ❌ | ❌ | ❌ |
| **Cache global** | ✅ Intelligent | ⚠️ Basique | ✅ | ✅ |
| **Compatibilité pip** | ✅ 100% | ✅ | ⚠️ Partielle | ⚠️ Partielle |
| **Build backend** | ✅ `hatchling` | ❌ | ✅ `poetry-core` | ❌ |
| **Téléchargement parallèle** | ✅ | ❌ | ⚠️ Limité | ⚠️ Limité |

### Différences clés

#### 1. **pip** - Gestionnaire de base

```bash
# Installation simple
pip install requests

# Fichier requirements.txt manuel
pip freeze > requirements.txt
pip install -r requirements.txt
```

**Limites :**
- ❌ Pas de lockfile automatique
- ❌ Résolution de dépendances lente
- ❌ Pas de gestion d'environnements virtuels intégrée
- ❌ Pas de séparation dev/prod

#### 2. **poetry** - Gestionnaire tout-en-un

```bash
# Création de projet
poetry new my-project
poetry add requests
poetry add --group dev pytest

# Installation
poetry install
```

**Limites :**
- ⚠️ Plus lent que uv
- ⚠️ Écosystème fermé (moins compatible pip)
- ⚠️ Nécessite Python déjà installé

#### 3. **pipenv** - Mix pip + virtualenv

```bash
# Création d'environnement
pipenv install requests
pipenv install --dev pytest

# Activation
pipenv shell
```

**Limites :**
- ⚠️ Résolution de dépendances très lente
- ⚠️ Moins maintenu récemment
- ⚠️ Fichiers séparés (Pipfile + Pipfile.lock)

#### 4. **uv** - Le plus rapide

```bash
# Création de projet
uv init my-project
uv add requests
uv add --dev pytest

# Installation ultra-rapide
uv sync --frozen
```

**Avantages :**
- ✅ 10-100x plus rapide
- ✅ Compatible avec pip et l'écosystème existant
- ✅ Gestion de Python intégrée
- ✅ Cache global intelligent

---

## Avantages de uv

### 1. 🚀 **Performance exceptionnelle**

#### Comparaison de vitesse (installation de 100 packages)

| Outil | Temps |
|-------|-------|
| **uv** | ~3 secondes |
| **poetry** | ~45 secondes |
| **pip** | ~60 secondes |
| **pipenv** | ~90 secondes |

#### Pourquoi si rapide ?

- **Écrit en Rust** : Compilé, pas d'interpréteur Python
- **Téléchargements parallèles** : Plusieurs packages en même temps
- **Résolution optimisée** : Algorithme de résolution ultra-rapide
- **Cache global** : Réutilisation intelligente des packages

### 2. 🔒 **Reproductibilité garantie**

```bash
# uv.lock contient les versions exactes
uv sync --frozen  # Installe exactement les mêmes versions
```

- Hashes cryptographiques pour chaque package
- Versions verrouillées pour toutes les dépendances transitives
- Garantie que dev/CI/prod sont identiques

### 3. 🐍 **Gestion de Python intégrée**

```bash
# Installer une version spécifique de Python
uv python install 3.13

# Utiliser une version pour le projet
uv python pin 3.12

# Lister les versions disponibles
uv python list
```

**Avantage :** Plus besoin de pyenv, asdf, ou installations manuelles !

### 4. 💾 **Cache intelligent**

```bash
# Cache global partagé entre projets
~/.cache/uv/
```

- **Économie d'espace** : Un package téléchargé = réutilisé partout
- **Économie de bande passante** : Pas de re-téléchargement
- **Économie de temps** : Installation quasi instantanée si en cache

### 5. 🌐 **Compatibilité totale**

```bash
# Compatible avec requirements.txt
uv pip install -r requirements.txt

# Compatible avec pyproject.toml
uv sync

# Compatible avec pip
uv pip install requests
```

**Migration facile depuis pip/poetry/pipenv !**

### 6. ⚡ **Workflow optimisé**

```bash
# Initialisation
uv init

# Ajouter une dépendance
uv add fastapi

# Ajouter une dépendance de dev
uv add --dev pytest

# Installer toutes les dépendances
uv sync

# Exécuter un script
uv run python main.py
uv run pytest

# Supprimer une dépendance
uv remove requests
```

---

## uv et pyproject.toml

### Structure du fichier pyproject.toml

Le fichier `pyproject.toml` est le standard moderne Python (PEP 518, 621). uv l'utilise comme source de vérité.

#### Structure complète

```toml
[project]
name = "mon-projet"
version = "1.0.0"
description = "Description du projet"
authors = [
    {name = "Nom Auteur", email = "email@example.com"}
]
readme = "README.md"
requires-python = ">=3.12"
license = {text = "MIT"}
keywords = ["api", "fastapi", "ci-cd"]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "Programming Language :: Python :: 3.12",
]

# Dépendances de production
dependencies = [
    "fastapi>=0.115.6",
    "uvicorn>=0.34.0",
    "pydantic>=2.10.6",
    "sqlalchemy>=2.0.0",
]

# Dépendances optionnelles
[project.optional-dependencies]
dev = [
    "pytest>=9.0.0",
    "pytest-cov>=7.0.0",
    "mypy>=1.16.0",
    "ruff>=0.9.0",
]
docs = [
    "mkdocs>=1.6.0",
    "mkdocs-material>=9.5.0",
]

# Scripts CLI
[project.scripts]
mon-cli = "mon_projet.cli:main"

# URLs du projet
[project.urls]
Homepage = "https://github.com/user/projet"
Documentation = "https://docs.example.com"
Repository = "https://github.com/user/projet"
Issues = "https://github.com/user/projet/issues"

# Build backend (pour créer des packages .whl/.tar.gz)
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

# Configuration uv
[tool.uv]
dev-dependencies = [
    "pytest>=9.0.0",
    "ruff>=0.9.0",
]

# Configuration d'autres outils
[tool.ruff]
line-length = 100
target-version = "py312"

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-v --cov=app --cov-report=term-missing"

[tool.mypy]
python_version = "3.12"
strict = true
```

### Gestion des dépendances par section

#### 1. **Dépendances de production** (`dependencies`)

Ce sont les packages **nécessaires pour faire tourner l'application**.

```toml
[project]
dependencies = [
    "fastapi>=0.115.6",          # Framework API
    "uvicorn[standard]>=0.34.0", # Serveur ASGI
    "pydantic>=2.10.6",          # Validation de données
    "sqlalchemy>=2.0.0",         # ORM base de données
    "python-dotenv>=1.2.1",      # Variables d'environnement
]
```

**Commandes :**
```bash
# Ajouter une dépendance de prod
uv add fastapi

# Installer uniquement les dépendances de prod (pour Docker)
uv sync --frozen --no-dev
```

#### 2. **Dépendances de développement** (`dev-dependencies`)

Ce sont les outils pour **développer, tester et valider** le code.

```toml
[tool.uv]
dev-dependencies = [
    "pytest>=9.0.0",           # Tests unitaires
    "pytest-cov>=7.0.0",       # Couverture de code
    "mypy>=1.16.0",            # Vérification de types
    "ruff>=0.9.0",             # Linter + formatter
    "pre-commit>=4.0.0",       # Hooks Git
    "ipython>=8.30.0",         # Shell interactif
]
```

**Commandes :**
```bash
# Ajouter une dépendance de dev
uv add --dev pytest

# Installer toutes les dépendances (prod + dev)
uv sync
```

#### 3. **Dépendances optionnelles** (`optional-dependencies`)

Ce sont des **groupes de dépendances optionnelles** pour des cas d'usage spécifiques.

```toml
[project.optional-dependencies]
# Pour générer la documentation
docs = [
    "mkdocs>=1.6.0",
    "mkdocs-material>=9.5.0",
]

# Pour le support PostgreSQL
postgres = [
    "psycopg2-binary>=2.9.0",
]

# Pour le support Redis
redis = [
    "redis>=5.0.0",
]

# Groupe "all" pour tout installer
all = [
    "mkdocs>=1.6.0",
    "psycopg2-binary>=2.9.0",
    "redis>=5.0.0",
]
```

**Commandes :**
```bash
# Installer un groupe optionnel
uv sync --extra docs
uv sync --extra postgres

# Installer plusieurs groupes
uv sync --extra docs --extra postgres

# Installer tous les groupes
uv sync --all-extras
```

### Build backend

Le build backend permet de **créer des packages distribables** (.whl, .tar.gz).

#### Configuration avec hatchling (recommandé par uv)

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/mon_projet"]
```

#### Autres build backends possibles

```toml
# Poetry
[build-system]
requires = ["poetry-core>=1.0.0"]
build-backend = "poetry.core.masonry.api"

# Setuptools
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

# Flit
[build-system]
requires = ["flit-core>=3.2"]
build-backend = "flit_core.buildapi"
```

#### Quand a-t-on besoin d'un build backend ?

| Cas d'usage | Build backend nécessaire ? |
|-------------|---------------------------|
| Application web (FastAPI, Django) | ❌ Non |
| Application CLI | ❌ Non (sauf si distribution sur PyPI) |
| Bibliothèque Python | ✅ Oui (pour publier sur PyPI) |
| Package interne d'entreprise | ✅ Oui (si distribution) |

**Pour notre projet FastAPI :**
```toml
# Pas de build-system nécessaire
# On déploie via Docker, pas via PyPI
```

---

## uv dans GitHub Actions

### 1. Installation de uv

#### Méthode recommandée : Action officielle

```yaml
- name: Set up uv
  uses: astral-sh/setup-uv@v4
  with:
    version: "latest"  # ou version spécifique : "0.9.11"
    enable-cache: true
    cache-dependency-glob: "uv.lock"
```

#### Méthode alternative : Installation manuelle

```yaml
- name: Install uv
  run: curl -LsSf https://astral.sh/uv/install.sh | sh

- name: Add uv to PATH
  run: echo "$HOME/.cargo/bin" >> $GITHUB_PATH
```

### 2. Cache des dépendances

#### Cache automatique avec setup-uv

```yaml
- name: Set up uv
  uses: astral-sh/setup-uv@v4
  with:
    enable-cache: true
    cache-dependency-glob: "uv.lock"  # Invalide le cache si uv.lock change
```

Le cache est automatiquement :
- ✅ Créé à la première exécution
- ✅ Restauré aux exécutions suivantes
- ✅ Invalidé si `uv.lock` change

#### Cache manuel (si nécessaire)

```yaml
- name: Cache uv
  uses: actions/cache@v4
  with:
    path: |
      ~/.cache/uv
      .venv
    key: uv-${{ runner.os }}-${{ hashFiles('uv.lock') }}
    restore-keys: |
      uv-${{ runner.os }}-
```

### 3. Exécution de commandes

#### Workflow complet CI/CD

```yaml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      # 1. Checkout du code
      - uses: actions/checkout@v4

      # 2. Installation de uv avec cache
      - uses: astral-sh/setup-uv@v4
        with:
          enable-cache: true
          cache-dependency-glob: "uv.lock"

      # 3. Installation des dépendances
      - name: Install dependencies
        run: uv sync --frozen  # --frozen = utilise uv.lock sans le modifier

      # 4. Linting
      - name: Lint with Ruff
        run: uv run ruff check .

      # 5. Type checking
      - name: Type check with Mypy
        run: uv run mypy .

      # 6. Tests
      - name: Run tests
        run: uv run pytest --cov --cov-report=xml

      # 7. Upload coverage
      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          file: ./coverage.xml
```

#### Exemples de commandes uv

```yaml
# Installer uniquement les dépendances de production (pour Docker)
- run: uv sync --frozen --no-dev

# Installer toutes les dépendances (prod + dev)
- run: uv sync --frozen

# Exécuter un script Python
- run: uv run python main.py

# Exécuter un outil (pytest, mypy, ruff, etc.)
- run: uv run pytest
- run: uv run mypy .
- run: uv run ruff check .

# Exécuter FastAPI
- run: uv run fastapi run app/main.py

# Ajouter une dépendance (pour mise à jour automatique)
- run: uv add requests
- run: git add pyproject.toml uv.lock
- run: git commit -m "chore: update dependencies"
```

#### Workflow de build Docker avec uv

```yaml
name: Build Docker Image

on:
  push:
    branches: [main, develop]
    tags: ['v*']

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: docker/setup-buildx-action@v3

      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: ghcr.io/${{ github.repository }}:latest
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

**Dockerfile optimisé avec uv :**

```dockerfile
FROM python:3.13-slim

WORKDIR /app

# Installer uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Définir uv en mode système (pas de venv)
ENV UV_SYSTEM_PYTHON=1

# Copier les fichiers de dépendances
COPY pyproject.toml uv.lock ./

# Installer uniquement les dépendances de production
RUN uv sync --frozen --no-dev

# Copier le code source
COPY . .

# Exposer le port
EXPOSE 8000

# Lancer l'application
CMD ["uv", "run", "fastapi", "run", "app/main.py", "--port", "8000", "--host", "0.0.0.0"]
```

#### Matrice de tests multi-versions

```yaml
name: Test Matrix

on: [push, pull_request]

jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
        python-version: ["3.11", "3.12", "3.13"]

    steps:
      - uses: actions/checkout@v4

      - uses: astral-sh/setup-uv@v4
        with:
          enable-cache: true

      # uv peut installer Python automatiquement !
      - name: Set up Python ${{ matrix.python-version }}
        run: uv python install ${{ matrix.python-version }}

      - run: uv sync --frozen

      - run: uv run pytest
```

---

## Conclusion

### Récapitulatif des avantages de uv

| Critère | uv |
|---------|-----|
| 🚀 **Vitesse** | 10-100x plus rapide que pip/poetry |
| 🔒 **Reproductibilité** | Lockfile automatique avec hashes |
| 🐍 **Gestion Python** | Installation de versions Python intégrée |
| 💾 **Cache** | Cache global intelligent, économise espace et temps |
| 🌐 **Compatibilité** | 100% compatible avec l'écosystème pip |
| ⚡ **Simplicité** | Commandes intuitives (`uv add`, `uv run`, `uv sync`) |
| 🔧 **CI/CD** | Intégration GitHub Actions optimale |
| 📦 **Standard** | Utilise `pyproject.toml` (PEP 621) |

### Quand utiliser uv ?

✅ **Utiliser uv si :**
- Vous voulez un workflow **rapide et moderne**
- Vous travaillez en équipe et voulez **garantir la reproductibilité**
- Vous utilisez **GitHub Actions** (intégration native)
- Vous voulez **simplifier la gestion de Python**
- Vous avez des **gros projets** avec beaucoup de dépendances

⚠️ **Peut-être pas uv si :**
- Vous avez besoin de fonctionnalités avancées spécifiques à Poetry
- Votre équipe est fortement investie dans un autre outil
- Vous avez des contraintes legacy très fortes

### Commandes essentielles uv

```bash
# Initialisation
uv init                           # Créer un nouveau projet
uv python install 3.13            # Installer Python 3.13

# Gestion des dépendances
uv add fastapi                    # Ajouter une dépendance
uv add --dev pytest               # Ajouter une dépendance de dev
uv remove requests                # Supprimer une dépendance
uv sync                           # Installer toutes les dépendances
uv sync --frozen                  # Installer sans modifier uv.lock
uv sync --no-dev                  # Installer uniquement prod

# Exécution
uv run python main.py             # Exécuter un script
uv run pytest                     # Exécuter pytest
uv run fastapi run app/main.py    # Exécuter FastAPI

# Informations
uv pip list                       # Lister les packages installés
uv pip show requests              # Informations sur un package
uv tree                           # Arbre de dépendances
```

### Ressources

- 📚 **Documentation officielle** : https://docs.astral.sh/uv/
- 🐙 **GitHub** : https://github.com/astral-sh/uv
- 💬 **Discord Astral** : https://discord.gg/astral-sh
- 📝 **Blog Astral** : https://astral.sh/blog

# PARTIE 3 : Semantic Release - Versionnage Automatique

## Qu'est-ce que le versionnage sémantique (SemVer) ?

**Semantic Versioning (SemVer)** est un système de versionnage standardisé qui utilise un format à trois chiffres pour indiquer l'ampleur et le type de changements dans une version.

### Format MAJOR.MINOR.PATCH

```
version: 2.4.7
         │ │ │
         │ │ └─── PATCH (correctifs)
         │ └───── MINOR (nouvelles fonctionnalités)
         └─────── MAJOR (changements incompatibles)
```

#### Structure détaillée

| Composant | Valeur | Signification | Incrémentation |
|-----------|--------|---------------|----------------|
| **MAJOR** | 2 | Version majeure | Changements incompatibles avec les versions précédentes |
| **MINOR** | 4 | Version mineure | Nouvelles fonctionnalités rétrocompatibles |
| **PATCH** | 7 | Version de correctif | Corrections de bugs rétrocompatibles |

### Quand bumper chaque niveau ?

#### 1. MAJOR - Changements incompatibles (Breaking Changes)

**Quand incrémenter MAJOR** (ex: 1.5.3 → 2.0.0) :
- ❌ Suppression d'une API publique
- ❌ Modification du comportement existant de manière incompatible
- ❌ Changement de la signature d'une fonction publique
- ❌ Renommage de méthodes ou classes publiques

**Exemples concrets :**

```python
# Version 1.x.x
def get_user(user_id: int) -> dict:
    return {"id": user_id, "name": "Alice"}

# Version 2.0.0 - BREAKING CHANGE
def get_user(user_id: int) -> User:  # Retourne un objet au lieu d'un dict
    return User(id=user_id, name="Alice")
```

```python
# Version 1.x.x
@app.post("/items")  # Endpoint POST

# Version 2.0.0 - BREAKING CHANGE
@app.put("/items")   # Changement de méthode HTTP
```

**Impact utilisateur :**
- ⚠️ Le code des utilisateurs **devra être modifié**
- ⚠️ Migration nécessaire
- ⚠️ Documentation de migration requise

#### 2. MINOR - Nouvelles fonctionnalités (Features)

**Quand incrémenter MINOR** (ex: 1.5.3 → 1.6.0) :
- ✅ Ajout d'une nouvelle fonctionnalité publique
- ✅ Ajout d'un nouveau endpoint API
- ✅ Amélioration d'une fonctionnalité existante (rétrocompatible)
- ✅ Marquage d'une fonctionnalité comme dépréciée (sans la supprimer)

**Exemples concrets :**

```python
# Version 1.5.0
class ItemService:
    def get_all(self) -> list[Item]:
        return items

# Version 1.6.0 - Nouvelle fonctionnalité
class ItemService:
    def get_all(self) -> list[Item]:
        return items

    def get_paginated(self, page: int, size: int) -> list[Item]:  # NOUVEAU
        return items[page*size:(page+1)*size]
```

**Impact utilisateur :**
- ✅ Aucun code à modifier
- ✅ Nouvelles fonctionnalités disponibles
- ✅ Upgrade sans risque

#### 3. PATCH - Corrections de bugs (Fixes)

**Quand incrémenter PATCH** (ex: 1.5.3 → 1.5.4) :
- 🐛 Correction d'un bug
- 🐛 Amélioration de performance (sans changement d'API)
- 🐛 Correction de documentation
- 🐛 Refactoring interne (sans impact externe)

**Exemples concrets :**

```python
# Version 1.5.3 - BUG
def calculate_total(items: list[Item]) -> float:
    return sum(item.price for item in items)  # Bug: ne gère pas items vide

# Version 1.5.4 - FIX
def calculate_total(items: list[Item]) -> float:
    if not items:  # Correction du bug
        return 0.0
    return sum(item.price for item in items)
```

**Impact utilisateur :**
- ✅ Aucun code à modifier
- ✅ Bugs corrigés
- ✅ Upgrade recommandé

#### Tableau récapitulatif

| Version | Type | Exemple de changement | Compatibilité | Exemple de bump |
|---------|------|----------------------|---------------|-----------------|
| **MAJOR** | Breaking | Suppression d'un endpoint | ❌ Incompatible | 1.5.3 → **2.0.0** |
| **MINOR** | Feature | Ajout d'un endpoint | ✅ Compatible | 1.5.3 → 1.**6.0** |
| **PATCH** | Fix | Correction de bug | ✅ Compatible | 1.5.3 → 1.5.**4** |

#### Règles spéciales

##### Version 0.x.x (pré-release)

```
0.1.0 → 0.2.0 → 0.3.0 → 1.0.0
│                       │
└─ Développement       └─ Première version stable
```

- **0.x.x** = API instable, tout peut changer
- **1.0.0** = Première version stable (API publique définie)

##### Métadonnées additionnelles

```
1.5.3-alpha.1      # Version alpha
1.5.3-beta.2       # Version beta
1.5.3-rc.1         # Release candidate
1.5.3+20230915     # Build metadata
```

---

## Qu'est-ce que Conventional Commits ?

**Conventional Commits** est une convention de nommage pour les messages de commit Git qui permet d'automatiser le versionnage et la génération de changelog.

### Format des messages

#### Structure de base

```
<type>(<scope>): <description>

[corps optionnel]

[footer optionnel]
```

**Exemple simple :**
```bash
feat(items): add pagination support
```

**Exemple complet :**
```bash
feat(api): add user authentication endpoint

Implement JWT-based authentication with refresh tokens.
This allows users to securely login and maintain sessions.

Closes #123
```

#### Anatomie d'un commit conventionnel

```
feat(items): add pagination to item list endpoint
│    │       │
│    │       └─── Description (impératif, minuscule)
│    └─────────── Scope (optionnel, contexte du changement)
└──────────────── Type (requis, nature du changement)
```

### Types de commits

| Type | Description | Impact SemVer | Exemple |
|------|-------------|---------------|---------|
| `feat` | Nouvelle fonctionnalité | **MINOR** ↑ | `feat: add dark mode` |
| `fix` | Correction de bug | **PATCH** ↑ | `fix: handle null values` |
| `docs` | Documentation uniquement | Aucun | `docs: update README` |
| `style` | Formatage, espaces | Aucun | `style: format with ruff` |
| `refactor` | Refactoring (sans bug ni feature) | Aucun | `refactor: extract service layer` |
| `perf` | Amélioration de performance | **PATCH** ↑ | `perf: optimize db queries` |
| `test` | Ajout ou correction de tests | Aucun | `test: add user tests` |
| `chore` | Tâches de maintenance | Aucun | `chore: update dependencies` |
| `ci` | Changements CI/CD | Aucun | `ci: add GitHub Actions` |
| `build` | Système de build | Aucun | `build: update Dockerfile` |
| `revert` | Annulation d'un commit | Dépend du commit annulé | `revert: feat(api): add endpoint` |

#### Types personnalisés (optionnels)

Certains projets ajoutent des types supplémentaires :

```
hotfix: urgent production fix
security: security vulnerability fix
deps: dependency updates
ui: user interface changes
```

### Scopes (portées)

Le scope précise **quelle partie du code** est affectée.

**Exemples de scopes :**

```bash
feat(auth): add login endpoint       # Module authentification
fix(database): connection pool issue  # Module base de données
docs(api): update API documentation   # Documentation API
test(items): add integration tests    # Tests du module items
```

**Structure de projet typique :**

```
app/
├── auth/      → scope: auth
├── items/     → scope: items
├── users/     → scope: users
└── database/  → scope: database
```

### Impact sur le versionnage

#### Commits qui déclenchent un bump de version

```bash
# MINOR bump (0.1.0 → 0.2.0)
feat(items): add pagination

# PATCH bump (0.1.0 → 0.1.1)
fix(api): handle empty responses

# Aucun bump
docs: update README
style: format code
chore: update dependencies
```

#### Breaking Changes - MAJOR bump

**Option 1 : Utiliser `!` après le type**

```bash
feat!(api): redesign authentication flow

BREAKING CHANGE: The /auth endpoint now requires OAuth2
```

**Option 2 : Utiliser le footer `BREAKING CHANGE:`**

```bash
feat(api): redesign authentication flow

BREAKING CHANGE: The /auth endpoint now requires OAuth2 instead of basic auth.
Migration guide: https://docs.example.com/migration
```

**Impact :**
```
feat!: redesign API  →  1.5.3 → 2.0.0 (MAJOR bump)
```

### Exemples réels de Conventional Commits

#### 1. Nouvelle fonctionnalité simple

```bash
feat(items): add search functionality
```

#### 2. Correction de bug avec détails

```bash
fix(database): prevent connection pool exhaustion

The connection pool was not properly releasing connections
after failed queries, leading to pool exhaustion after
prolonged use.

This fix ensures connections are released in finally blocks.

Fixes #156
```

#### 3. Breaking change avec migration

```bash
feat!(api): migrate to pydantic v2

BREAKING CHANGE: Pydantic v2 has different validation rules.
All models now use ConfigDict instead of class Config.

Migration steps:
- Update `class Config` to `model_config = ConfigDict(...)`
- Replace `schema_extra` with `json_schema_extra`
- Review custom validators

See migration guide: docs/migration-v2.md
```

#### 4. Plusieurs changements

```bash
feat(items): add filtering and sorting

- Add query parameters: ?filter=name&sort=price
- Support multiple sort fields
- Add validation for filter values

Closes #89, #92
```

#### 5. Commit de maintenance

```bash
chore(deps): update dependencies

- fastapi: 0.115.0 → 0.115.6
- pydantic: 2.10.0 → 2.10.6
- uvicorn: 0.33.0 → 0.34.0
```

### Règles et bonnes pratiques

#### ✅ À faire

1. **Utiliser l'impératif présent** : "add feature" pas "added feature"
2. **Première lettre en minuscule** : "add feature" pas "Add feature"
3. **Pas de point final** : "add feature" pas "add feature."
4. **Être descriptif mais concis** : Max 50-72 caractères pour la description
5. **Un commit = un changement logique** : Pas de "fix bug and add feature"

```bash
✅ feat(auth): add JWT authentication
✅ fix(api): handle null user IDs
✅ docs: update installation guide

❌ Added new feature for authentication
❌ Fix bug.
❌ Updated stuff
```

#### ❌ À éviter

```bash
❌ fix: various fixes         # Trop vague
❌ feat: WIP                   # Work in progress n'est pas un commit final
❌ update code                 # Pas de type
❌ FEAT: Add Feature           # Majuscules incorrectes
❌ feat: add feature.          # Point final inutile
```

### Outils de validation

#### 1. Commitlint (validation des commits)

```bash
# Installation
npm install --save-dev @commitlint/cli @commitlint/config-conventional

# Configuration (.commitlintrc.json)
{
  "extends": ["@commitlint/config-conventional"],
  "rules": {
    "type-enum": [2, "always", ["feat", "fix", "docs", "style", "refactor", "test", "chore"]]
  }
}

# Utilisation avec pre-commit
- repo: https://github.com/alessandrojcm/commitlint-pre-commit-hook
  hooks:
    - id: commitlint
```

#### 2. Template de commit Git

```bash
# .gitmessage template
<type>(<scope>): <description>

# <body>

# <footer>

# Types: feat, fix, docs, style, refactor, perf, test, chore, ci
# Scope: auth, items, api, database, etc.
# Breaking changes: Add ! after type or BREAKING CHANGE: in footer
```

```bash
# Configurer le template
git config commit.template .gitmessage
```

---

## Comment python-semantic-release fonctionne ?

**Python Semantic Release** est un outil qui automatise le versionnage, la génération de changelog et la création de releases GitHub en analysant les commits conventionnels.

### Workflow automatique

```
┌─────────────────────────────────────────────────────────┐
│  1. Analyse des commits depuis la dernière version      │
│     (cherche feat, fix, BREAKING CHANGE)                │
└───────────────────┬─────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────┐
│  2. Détermine le type de bump                           │
│     - feat → MINOR (0.1.0 → 0.2.0)                      │
│     - fix → PATCH (0.1.0 → 0.1.1)                       │
│     - BREAKING CHANGE → MAJOR (0.1.0 → 1.0.0)           │
└───────────────────┬─────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────┐
│  3. Met à jour la version dans pyproject.toml           │
└───────────────────┬─────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────┐
│  4. Génère/met à jour CHANGELOG.md                      │
│     (groupe les commits par type)                       │
└───────────────────┬─────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────┐
│  5. Crée un commit de release                           │
│     (message: "chore(release): 0.2.0")                  │
└───────────────────┬─────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────┐
│  6. Crée un tag Git (v0.2.0)                            │
└───────────────────┬─────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────┐
│  7. Push le commit et le tag vers GitHub               │
└───────────────────┬─────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────┐
│  8. Crée une GitHub Release avec le changelog          │
└─────────────────────────────────────────────────────────┘
```

### Configuration dans pyproject.toml

#### Configuration complète

```toml
[tool.semantic_release]
# Version actuelle (mise à jour automatiquement)
version_toml = ["pyproject.toml:project.version"]

# Branche principale (où les releases sont créées)
branch = "main"

# Format du tag Git
tag_format = "v{version}"

# Construire le projet avant la release
build_command = "uv build"

# Créer une release GitHub
upload_to_repository = false
upload_to_release = true

# Variables d'environnement pour GitHub
[tool.semantic_release.remote]
name = "origin"
type = "github"

# Configuration du changelog
[tool.semantic_release.changelog]
exclude_commit_patterns = [
    "chore\\(release\\):.*",  # Exclure les commits de release
    "Merge.*",                 # Exclure les commits de merge
]

# Template du changelog
template_dir = "templates"
changelog_file = "CHANGELOG.md"

# Configuration des commits conventionnels
[tool.semantic_release.commit_parser_options]
allowed_tags = [
    "feat",
    "fix",
    "perf",
    "docs",
    "style",
    "refactor",
    "test",
    "chore",
    "ci",
    "build",
]
minor_tags = ["feat"]
patch_tags = ["fix", "perf"]

# Configuration des branches
[tool.semantic_release.branches.main]
match = "main"
prerelease = false

[tool.semantic_release.branches.develop]
match = "develop"
prerelease = true
prerelease_token = "rc"
```

#### Configuration minimale

```toml
[tool.semantic_release]
version_toml = ["pyproject.toml:project.version"]
branch = "main"
upload_to_release = true
build_command = ""

[tool.semantic_release.changelog]
changelog_file = "CHANGELOG.md"
exclude_commit_patterns = []
```

### Génération du CHANGELOG

#### Structure automatique du CHANGELOG.md

```markdown
# CHANGELOG

## v0.2.0 (2025-11-27)

### Features
- **items**: add pagination support (#42)
- **api**: add filtering by name (#45)

### Bug Fixes
- **database**: fix connection pool leak (#43)
- **auth**: handle expired tokens correctly (#46)

### Documentation
- update API documentation (#44)

## v0.1.0 (2025-11-20)

### Features
- **items**: initial item CRUD operations (#1)
- **api**: add health check endpoint (#2)
```

#### Template personnalisé

```jinja2
{# templates/CHANGELOG.md.j2 #}
# CHANGELOG

{% for version in versions %}
## {{ version.tag }} ({{ version.date }})

{% if version.sections.feature %}
### ✨ Features
{% for commit in version.sections.feature %}
- **{{ commit.scope }}**: {{ commit.description }} (#{{ commit.pr_number }})
{% endfor %}
{% endif %}

{% if version.sections.fix %}
### 🐛 Bug Fixes
{% for commit in version.sections.fix %}
- **{{ commit.scope }}**: {{ commit.description }} (#{{ commit.pr_number }})
{% endfor %}
{% endif %}

{% if version.sections.breaking %}
### ⚠️ BREAKING CHANGES
{% for commit in version.sections.breaking %}
- **{{ commit.scope }}**: {{ commit.breaking_description }}
{% endfor %}
{% endif %}

{% endfor %}
```

### Création des releases GitHub

#### Processus automatique

```yaml
# .github/workflows/release.yml
name: Semantic Release

on:
  push:
    branches:
      - main

permissions:
  contents: write
  issues: write
  pull-requests: write

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Nécessaire pour l'historique complet

      - uses: astral-sh/setup-uv@v4

      - name: Install dependencies
        run: uv sync

      - name: Python Semantic Release
        id: release
        uses: python-semantic-release/python-semantic-release@v9.14.0
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}

      - name: Publish to GitHub Releases
        if: steps.release.outputs.released == 'true'
        run: |
          echo "Released version: ${{ steps.release.outputs.version }}"
          echo "Tag: ${{ steps.release.outputs.tag }}"
```

#### Résultat sur GitHub

**Release créée automatiquement :**

```
Release v0.2.0
───────────────

## What's Changed

### ✨ Features
- Add pagination support by @user in #42
- Add filtering by name by @user in #45

### 🐛 Bug Fixes
- Fix connection pool leak by @user in #43
- Handle expired tokens correctly by @user in #46

### 📝 Documentation
- Update API documentation by @user in #44

**Full Changelog**: v0.1.0...v0.2.0
```

### Commandes utiles

#### 1. Dry-run (simulation)

```bash
# Voir quelle version serait créée (sans rien modifier)
uv run semantic-release version --dry-run

# Output:
# Current version: 0.1.0
# Next version: 0.2.0 (MINOR bump due to feat commits)
```

#### 2. Générer le changelog manuellement

```bash
# Générer le changelog sans créer de release
uv run semantic-release changelog --dry-run
```

#### 3. Forcer un type de bump

```bash
# Forcer un MAJOR bump
uv run semantic-release version --major

# Forcer un MINOR bump
uv run semantic-release version --minor

# Forcer un PATCH bump
uv run semantic-release version --patch
```

#### 4. Publier une release

```bash
# Créer la release complète (version + changelog + tag + GitHub release)
uv run semantic-release publish
```

### Exemples de scénarios

#### Scénario 1 : Développement normal

```bash
# Commits depuis v0.1.0
git log --oneline
abc123 feat(items): add pagination
def456 fix(api): handle null values
ghi789 docs: update README

# Semantic release analyse:
# - feat → MINOR bump
# - fix → inclus dans le changelog
# - docs → inclus dans le changelog mais pas de bump

# Résultat: v0.1.0 → v0.2.0
```

#### Scénario 2 : Breaking change

```bash
# Commits depuis v0.2.0
git log --oneline
abc123 feat!(api): redesign authentication

BREAKING CHANGE: OAuth2 required instead of basic auth

# Semantic release analyse:
# - feat! → MAJOR bump

# Résultat: v0.2.0 → v1.0.0
```

#### Scénario 3 : Uniquement des fixes

```bash
# Commits depuis v1.0.0
git log --oneline
abc123 fix(database): connection pool
def456 fix(auth): token expiration
ghi789 chore: update dependencies

# Semantic release analyse:
# - 2x fix → PATCH bump
# - chore → pas de bump

# Résultat: v1.0.0 → v1.0.1
```

### Intégration avec uv

```toml
# pyproject.toml
[project]
name = "mon-projet"
version = "0.1.0"  # Mis à jour automatiquement par semantic-release
dependencies = [
    "fastapi>=0.115.6",
]

[tool.uv]
dev-dependencies = [
    "python-semantic-release>=9.14.0",
]

[tool.semantic_release]
version_toml = ["pyproject.toml:project.version"]
branch = "main"
upload_to_release = true
build_command = "uv build"
```

**Installation :**

```bash
# Ajouter semantic-release
uv add --dev python-semantic-release

# Vérifier la configuration
uv run semantic-release --help
```

### Avantages de python-semantic-release

| Avantage | Description |
|----------|-------------|
| ⚡ **Automatisation complète** | Plus besoin de bumper manuellement les versions |
| 📝 **Changelog automatique** | Génération du changelog à partir des commits |
| 🏷️ **Tags Git automatiques** | Création et push automatique des tags |
| 🚀 **GitHub Releases** | Création automatique des releases GitHub |
| 🔒 **Reproductibilité** | Versionnage basé sur des règles strictes |
| 👥 **Collaboration** | Tout le monde suit les mêmes règles |
| 📊 **Traçabilité** | Historique clair des changements |

---

**Document rédigé dans le cadre du brief CI/CD - Phase de veille technologique**
**Date :** 2025-11-25
**Auteur :** Leozmee
**Projet :** brief-ci-cd-semantic-release-mkdocs
