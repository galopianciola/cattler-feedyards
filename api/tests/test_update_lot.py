from datetime import date

import pytest
from rest_framework import status

from api.models import Animal, WeightRecord
from api.tests.conftest import FROZEN_TODAY

pytestmark = pytest.mark.django_db


MSG_FROM_DATE_FUTURE_ES = "La fecha no puede ser futura."
MSG_FROM_DATE_FUTURE_EN = "From date cannot be in the future."

MSG_FROM_DATE_BEFORE_ENTRY_ES = (
    "La fecha no puede ser anterior a la fecha de ingreso del lote."
)
MSG_FROM_DATE_BEFORE_ENTRY_EN = (
    "From date must be greater than or equal to the entry date."
)

MSG_WEIGHT_ES = "El peso promedio del lote debe ser mayor a 0.0."
MSG_WEIGHT_EN = "Lot average weight must be greater than 0.0."


class TestUpdateLotSuccess:
    def test_update_lot_returns_200(
        self,
        api_client,
        user_es,
        lot_with_animals,
        lot_detail_url,
        valid_update_payload,
        frozen_today,
    ):
        api_client.credentials(HTTP_AUTHORIZATION="Token token-es")
        response = api_client.patch(lot_detail_url, valid_update_payload, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data == {
            "id": lot_with_animals.pk,
            "name": lot_with_animals.name,
        }

        lot = lot_with_animals
        assert not Animal.objects.filter(lot=lot).exclude(current_weight=400).exists()

        # 5-jun .. 11-jun = 7 días × 5 animales
        updated_count = WeightRecord.objects.filter(
            animal__lot=lot,
            date__gte=date(2026, 6, 5),
            date__lte=FROZEN_TODAY,
            weight=400,
        ).count()
        assert updated_count == 5 * 7

        # antes del from_date siguen en 300
        old_count = WeightRecord.objects.filter(
            animal__lot=lot,
            date__lt=date(2026, 6, 5),
            weight=300,
        ).count()
        assert old_count > 0

        # peso de hoy actualizado
        assert (
            WeightRecord.objects.filter(
                animal__lot=lot,
                date=FROZEN_TODAY,
                weight=400,
            ).count()
            == 5
        )

    def test_unauthenticated_returns_401(
        self,
        api_client,
        lot_detail_url,
        valid_update_payload,
        frozen_today,
    ):
        response = api_client.patch(lot_detail_url, valid_update_payload, format="json")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestUpdateLotValidation:
    @pytest.mark.parametrize(
        "payload, field, message_es, message_en",
        [
            (
                {"from_date": "2099-01-01", "average_weight": 400.0},
                "from_date",
                MSG_FROM_DATE_FUTURE_ES,
                MSG_FROM_DATE_FUTURE_EN,
            ),
            (
                {"from_date": "2020-01-01", "average_weight": 400.0},
                "non_field_errors",
                MSG_FROM_DATE_BEFORE_ENTRY_ES,
                MSG_FROM_DATE_BEFORE_ENTRY_EN,
            ),
            (
                {"from_date": "2026-06-05", "average_weight": 0},
                "average_weight",
                MSG_WEIGHT_ES,
                MSG_WEIGHT_EN,
            ),
        ],
    )
    def test_validation_returns_409_with_translated_message(
        self,
        api_client,
        user_es,
        user_en,
        lot_with_animals,
        lot_detail_url,
        frozen_today,
        payload,
        field,
        message_es,
        message_en,
    ):
        api_client.credentials(HTTP_AUTHORIZATION="Token token-es")
        response = api_client.patch(lot_detail_url, payload, format="json")
        assert response.status_code == status.HTTP_409_CONFLICT
        assert response.data[field][0] == message_es

        api_client.credentials(HTTP_AUTHORIZATION="Token token-en")
        response = api_client.patch(lot_detail_url, payload, format="json")
        assert response.status_code == status.HTTP_409_CONFLICT
        assert response.data[field][0] == message_en
