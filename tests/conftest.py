import pytest
from fastapi.testclient import TestClient

from main import app
from repositories.predict import PredictRepository
from services.predict import PredictService


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def valid_payload() -> dict:
    return {
        "seller_id": 1,
        "is_verified_seller": True,
        "item_id": 100,
        "name": "Велосипед горный",
        "description": "Отличное состояние, почти не использовался, полный комплект",
        "category": 1,
        "images_qty": 3,
    }


@pytest.fixture
def predict_service() -> PredictService:
    return PredictService(repository=PredictRepository())
