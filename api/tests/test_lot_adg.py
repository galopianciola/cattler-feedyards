import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


MSG_START_FUTURE_ES = "La fecha inicial no puede ser futura."
MSG_START_FUTURE_EN = "Start date cannot be in the future."

MSG_END_FUTURE_ES = "La fecha final no puede ser futura."
MSG_END_FUTURE_EN = "End date cannot be in the future."

MSG_START_AFTER_END_ES = "La fecha inicial debe ser menor o igual a la fecha final."
MSG_START_AFTER_END_EN = "Start date must be less than or equal to end date."

MSG_SAME_DATE_ES = "La fecha inicial y la fecha final deben ser distintas."
MSG_SAME_DATE_EN = "Start date and end date must be different."

MSG_START_BEFORE_ENTRY_ES = (
    "La fecha inicial no puede ser anterior a la fecha de ingreso del lote."
)
MSG_START_BEFORE_ENTRY_EN = (
    "Start date must be greater than or equal to the entry date."
)


class TestLotADGSuccess:
    def test_adg_returns_zero_with_constant_weight(
        self, api_client, user_es, lot_adg_url, adg_params, frozen_today
    ):
        api_client.credentials(HTTP_AUTHORIZATION="Token token-es")
        response = api_client.get(lot_adg_url, adg_params)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == {"adg": 0.0}

    def test_adg_returns_positive_after_weight_update(
        self,
        api_client,
        user_es,
        lot_adg_url,
        lot_detail_url,
        adg_params,
        valid_update_payload,
        frozen_today,
    ):
        api_client.credentials(HTTP_AUTHORIZATION="Token token-es")
        api_client.patch(lot_detail_url, valid_update_payload, format="json")

        response = api_client.get(lot_adg_url, adg_params)

        assert response.status_code == status.HTTP_200_OK
        # (5 * 400) - (5 * 300) = 500, / 9 días
        assert response.data["adg"] == pytest.approx(500 / 9)

    def test_unauthenticated_returns_401(
        self, api_client, lot_adg_url, adg_params, frozen_today
    ):
        response = api_client.get(lot_adg_url, adg_params)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestLotADGValidation:
    @pytest.mark.parametrize(
        "params, field, message_es, message_en",
        [
            (
                {"start_date": "2099-01-01", "end_date": "2026-06-11"},
                "start_date",
                MSG_START_FUTURE_ES,
                MSG_START_FUTURE_EN,
            ),
            (
                {"start_date": "2026-06-02", "end_date": "2099-01-01"},
                "end_date",
                MSG_END_FUTURE_ES,
                MSG_END_FUTURE_EN,
            ),
            (
                {"start_date": "2026-06-11", "end_date": "2026-06-02"},
                "non_field_errors",
                MSG_START_AFTER_END_ES,
                MSG_START_AFTER_END_EN,
            ),
            (
                {"start_date": "2026-06-05", "end_date": "2026-06-05"},
                "non_field_errors",
                MSG_SAME_DATE_ES,
                MSG_SAME_DATE_EN,
            ),
            (
                {"start_date": "2020-01-01", "end_date": "2026-06-11"},
                "non_field_errors",
                MSG_START_BEFORE_ENTRY_ES,
                MSG_START_BEFORE_ENTRY_EN,
            ),
        ],
    )
    def test_validation_returns_409_with_translated_message(
        self,
        api_client,
        user_es,
        user_en,
        lot_adg_url,
        frozen_today,
        params,
        field,
        message_es,
        message_en,
    ):
        api_client.credentials(HTTP_AUTHORIZATION="Token token-es")
        response = api_client.get(lot_adg_url, params)
        assert response.status_code == status.HTTP_409_CONFLICT
        assert response.data[field][0] == message_es

        api_client.credentials(HTTP_AUTHORIZATION="Token token-en")
        response = api_client.get(lot_adg_url, params)
        assert response.status_code == status.HTTP_409_CONFLICT
        assert response.data[field][0] == message_en
