import pytest
from rest_framework import status

from api.models import Animal, Lot, WeightRecord

pytestmark = pytest.mark.django_db


MSG_QUANTITY_ES = "La cantidad de animales debe ser mayor o igual a 1."
MSG_QUANTITY_EN = "Animal quantity must be greater than or equal to 1."
MSG_WEIGHT_ES = "El peso promedio del lote debe ser mayor a 0.0."
MSG_WEIGHT_EN = "Lot average weight must be greater than 0.0."
MSG_DATE_ES = "La fecha de ingreso no puede ser futura."
MSG_DATE_EN = "Entry date cannot be in the future."


class TestCreateLotSuccess:
    def test_create_lot_returns_201(
        self, api_client, user_es, lot_url, valid_payload, frozen_today
    ):
        api_client.credentials(HTTP_AUTHORIZATION="Token token-es")
        response = api_client.post(lot_url, valid_payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data == {"id": 1, "name": "Lote 02-06-2026"}

        lot = Lot.objects.get()
        assert lot.feedyard == user_es.feedyard
        assert Animal.objects.filter(lot=lot).count() == 5

        # 5 animales × 10 dias
        assert WeightRecord.objects.filter(animal__lot=lot).count() == 5 * 10

    def test_unauthenticated_returns_401(
        self, api_client, lot_url, valid_payload, frozen_today
    ):
        response = api_client.post(lot_url, valid_payload, format="json")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestCreateLotValidation:
    @pytest.mark.parametrize(
        "payload, field, message_es, message_en",
        [
            (
                {
                    "quantity": 0,
                    "entry_date": "2026-06-01",
                    "average_weight": 300.0,
                },
                "quantity",
                MSG_QUANTITY_ES,
                MSG_QUANTITY_EN,
            ),
            (
                {
                    "quantity": 5,
                    "entry_date": "2026-06-01",
                    "average_weight": 0,
                },
                "average_weight",
                MSG_WEIGHT_ES,
                MSG_WEIGHT_EN,
            ),
            (
                {
                    "quantity": 5,
                    "entry_date": "2099-01-01",
                    "average_weight": 300.0,
                },
                "entry_date",
                MSG_DATE_ES,
                MSG_DATE_EN,
            ),
        ],
    )
    def test_validation_returns_409_with_translated_message(
        self,
        api_client,
        user_es,
        user_en,
        lot_url,
        frozen_today,
        payload,
        field,
        message_es,
        message_en,
    ):
        # es
        api_client.credentials(HTTP_AUTHORIZATION="Token token-es")
        response = api_client.post(lot_url, payload, format="json")
        assert response.status_code == status.HTTP_409_CONFLICT
        assert response.data[field][0] == message_es

        # en
        api_client.credentials(HTTP_AUTHORIZATION="Token token-en")
        response = api_client.post(lot_url, payload, format="json")
        assert response.status_code == status.HTTP_409_CONFLICT
        assert response.data[field][0] == message_en
