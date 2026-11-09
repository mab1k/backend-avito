from unittest.mock import MagicMock

import pytest
from fastapi import status

from exceptions import PredictionError
from repositories.predict import PredictRepository
from schemas.predict import PredictRequest
from services.predict import PredictService


POSITIVE_CASES = [
    pytest.param(
        {
            "seller_id": 1,
            "is_verified_seller": True,
            "item_id": 101,
            "name": "Стол письменный",
            "description": "Деревянный стол в хорошем состоянии, самовывоз",
            "category": 2,
            "images_qty": 2,
        },
        False,
        id="clean-verified",
    ),
    pytest.param(
        {
            "seller_id": 2,
            "is_verified_seller": False,
            "item_id": 102,
            "name": "Кресло офисное",
            "description": "Удобное кресло с регулировкой высоты и подлокотниками",
            "category": 2,
            "images_qty": 1,
        },
        False,
        id="clean-unverified-long-description",
    ),
]

NEGATIVE_CASES = [
    pytest.param(
        {
            "seller_id": 3,
            "is_verified_seller": True,
            "item_id": 201,
            "name": "Телефон",
            "description": "Пишите в telegram для связи",
            "category": 1,
            "images_qty": 2,
        },
        True,
        id="forbidden-word",
    ),
    pytest.param(
        {
            "seller_id": 4,
            "is_verified_seller": True,
            "item_id": 202,
            "name": "Ноутбук",
            "description": "Рабочий ноутбук в отличном состоянии без царапин",
            "category": 1,
            "images_qty": 0,
        },
        True,
        id="no-images",
    ),
    pytest.param(
        {
            "seller_id": 5,
            "is_verified_seller": False,
            "item_id": 203,
            "name": "Книга",
            "description": "Коротко",
            "category": 3,
            "images_qty": 1,
        },
        True,
        id="unverified-short-description",
    ),
]


@pytest.mark.parametrize("payload, expected", POSITIVE_CASES + NEGATIVE_CASES)
def test_predict_results(client, payload, expected):
    response = client.post("/predict", json=payload)

    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert body["item_id"] == payload["item_id"]
    assert body["has_violation"] is expected


@pytest.mark.parametrize(
    "override, missing_field",
    [
        ({"seller_id": "not-int"}, "seller_id"),
            ({"is_verified_seller": "not-a-bool"}, "is_verified_seller"),
        ({"item_id": "abc"}, "item_id"),
        ({"category": "home"}, "category"),
        ({"images_qty": "many"}, "images_qty"),
        ({"seller_id": 0}, "seller_id"),
        ({"item_id": -1}, "item_id"),
        ({"images_qty": -5}, "images_qty"),
        ({"name": ""}, "name"),
        ({"description": ""}, "description"),
    ],
)
def test_predict_validation_types_and_constraints(client, valid_payload, override, missing_field):
    payload = {**valid_payload, **override}

    response = client.post("/predict", json=payload)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert any(err["loc"][-1] == missing_field for err in response.json()["detail"])


@pytest.mark.parametrize(
    "field",
    [
        "seller_id",
        "is_verified_seller",
        "item_id",
        "name",
        "description",
        "category",
        "images_qty",
    ],
)
def test_predict_missing_required_fields(client, valid_payload, field):
    payload = {**valid_payload}
    del payload[field]

    response = client.post("/predict", json=payload)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert any(err["loc"][-1] == field for err in response.json()["detail"])


def test_predict_business_logic_error_returns_500(client, valid_payload, monkeypatch):
    def failing_predict(_payload):
        raise PredictionError("сбой бизнес-логики")

    monkeypatch.setattr(
        "routers.predict._service.predict",
        failing_predict,
    )

    response = client.post("/predict", json=valid_payload)

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "сбой бизнес-логики" in response.json()["detail"]


def test_predict_repository_failure_propagates_as_500(client, valid_payload):
    payload = {**valid_payload, "item_id": PredictRepository.FAILING_ITEM_ID}

    response = client.post("/predict", json=payload)

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "недоступна" in response.json()["detail"]


def test_service_wraps_repository_exceptions(predict_service):
    broken_repo = MagicMock()
    broken_repo.predict.side_effect = RuntimeError("db down")
    service = PredictService(repository=broken_repo)
    payload = PredictRequest(
        seller_id=1,
        is_verified_seller=True,
        item_id=10,
        name="Тест",
        description="Нормальное длинное описание без нарушений",
        category=1,
        images_qty=1,
    )

    with pytest.raises(PredictionError, match="db down"):
        service.predict(payload)


def test_root(client):
    response = client.get("/")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Hello World"}
