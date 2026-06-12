import pytest
from rest_framework import status

from api.models import Lot

pytestmark = pytest.mark.django_db


class TestTenantIsolation:
    def test_create_lot_uses_authenticated_user_feedyard(
        self, api_client, user_es, lot_url, valid_payload, frozen_today
    ):
        api_client.credentials(HTTP_AUTHORIZATION="Token token-es")
        response = api_client.post(lot_url, valid_payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        lot = Lot.objects.get(pk=response.data["id"])
        assert lot.feedyard == user_es.feedyard

    def test_user_cannot_patch_lot_from_other_feedyard(
        self,
        api_client,
        user_b,
        lot_with_animals,
        lot_detail_url,
        valid_update_payload,
        frozen_today,
    ):
        api_client.credentials(HTTP_AUTHORIZATION="Token token-b")
        response = api_client.patch(lot_detail_url, valid_update_payload, format="json")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_user_cannot_get_adg_of_lot_from_other_feedyard(
        self,
        api_client,
        user_b,
        lot_adg_url,
        adg_params,
        frozen_today,
    ):
        api_client.credentials(HTTP_AUTHORIZATION="Token token-b")
        response = api_client.get(lot_adg_url, adg_params)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_owner_can_still_access_own_lot(
        self,
        api_client,
        user_es,
        lot_detail_url,
        lot_adg_url,
        valid_update_payload,
        adg_params,
        frozen_today,
    ):
        api_client.credentials(HTTP_AUTHORIZATION="Token token-es")

        patch_response = api_client.patch(
            lot_detail_url, valid_update_payload, format="json"
        )
        assert patch_response.status_code == status.HTTP_200_OK

        adg_response = api_client.get(lot_adg_url, adg_params)
        assert adg_response.status_code == status.HTTP_200_OK
