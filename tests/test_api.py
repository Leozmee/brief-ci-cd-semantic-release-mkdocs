"""Tests basiques pour l'API Items."""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.main import app
from app.database import get_db


# Configuration de la base de données de test en mémoire
@pytest.fixture(name="session")
def session_fixture():
    """Crée une session de base de données de test en mémoire."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    """Crée un client de test avec une base de données de test."""

    def get_session_override():
        return session

    app.dependency_overrides[get_db] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


def test_read_root(client: TestClient):
    """Test du endpoint racine."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Items CRUD API"}


def test_read_health(client: TestClient):
    """Test du endpoint health."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_create_item(client: TestClient):
    """Test de création d'un item."""
    response = client.post(
        "/items/", json={"nom": "Test Item", "prix": 99.99}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["nom"] == "Test Item"
    assert data["prix"] == 99.99
    assert "id" in data


def test_read_items(client: TestClient):
    """Test de lecture de tous les items."""
    # Créer d'abord un item
    client.post("/items/", json={"nom": "Item 1", "prix": 10.0})
    client.post("/items/", json={"nom": "Item 2", "prix": 20.0})

    # Lire tous les items
    response = client.get("/items/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2


def test_read_item(client: TestClient):
    """Test de lecture d'un item spécifique."""
    # Créer un item
    create_response = client.post(
        "/items/", json={"nom": "Specific Item", "prix": 50.0}
    )
    item_id = create_response.json()["id"]

    # Lire cet item
    response = client.get(f"/items/{item_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["nom"] == "Specific Item"
    assert data["prix"] == 50.0


def test_read_item_not_found(client: TestClient):
    """Test de lecture d'un item inexistant."""
    response = client.get("/items/9999")
    assert response.status_code == 404


def test_update_item(client: TestClient):
    """Test de mise à jour d'un item."""
    # Créer un item
    create_response = client.post(
        "/items/", json={"nom": "Original", "prix": 100.0}
    )
    item_id = create_response.json()["id"]

    # Mettre à jour l'item
    response = client.put(
        f"/items/{item_id}", json={"nom": "Updated", "prix": 150.0}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["nom"] == "Updated"
    assert data["prix"] == 150.0


def test_delete_item(client: TestClient):
    """Test de suppression d'un item."""
    # Créer un item
    create_response = client.post(
        "/items/", json={"nom": "To Delete", "prix": 25.0}
    )
    item_id = create_response.json()["id"]

    # Supprimer l'item
    response = client.delete(f"/items/{item_id}")
    assert response.status_code == 204

    # Vérifier qu'il n'existe plus
    get_response = client.get(f"/items/{item_id}")
    assert get_response.status_code == 404
