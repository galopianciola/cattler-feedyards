from datetime import date
from unittest.mock import patch

import pytest
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from api.models import Feedyard, User
from api.services.lot_creation import create_lot_with_animals

FROZEN_TODAY = date(2026, 6, 11)
LOT_ENTRY_DATE = date(2026, 6, 2)


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def lot_url():
    return "/api/lots/"


@pytest.fixture
def feedyard(db):
    return Feedyard.objects.create(name="Feedyard Test")


@pytest.fixture
def user_es(feedyard):
    user = User.objects.create_user(
        username="user_es",
        password="pass",
        feedyard=feedyard,
        language=User.Language.ES,
    )
    Token.objects.create(user=user, key="token-es")
    return user


@pytest.fixture
def user_en(feedyard):
    user = User.objects.create_user(
        username="user_en",
        password="pass",
        feedyard=feedyard,
        language=User.Language.EN,
    )
    Token.objects.create(user=user, key="token-en")
    return user


@pytest.fixture
def valid_payload():
    return {
        "quantity": 5,
        "entry_date": "2026-06-02",
        "average_weight": 300.0,
    }


@pytest.fixture
def frozen_today():
    with (
        patch("api.serializers.timezone.localdate", return_value=FROZEN_TODAY),
        patch(
            "api.services.lot_creation.timezone.localdate", return_value=FROZEN_TODAY
        ),
        patch(
            "api.services.lot_weight_update.timezone.localdate",
            return_value=FROZEN_TODAY,
        ),
    ):
        yield FROZEN_TODAY


@pytest.fixture
def lot_with_animals(feedyard, frozen_today):
    return create_lot_with_animals(
        feedyard=feedyard,
        quantity=5,
        entry_date=LOT_ENTRY_DATE,
        average_weight=300.0,
    )


@pytest.fixture
def lot_detail_url(lot_with_animals):
    return f"/api/lots/{lot_with_animals.pk}/"


@pytest.fixture
def valid_update_payload():
    return {
        "from_date": "2026-06-05",
        "average_weight": 400.0,
    }


@pytest.fixture
def lot_adg_url(lot_with_animals):
    return f"/api/lots/{lot_with_animals.pk}/adg/"


@pytest.fixture
def feedyard_b(db):
    return Feedyard.objects.create(name="Feedyard B")


@pytest.fixture
def user_b(feedyard_b):
    user = User.objects.create_user(
        username="user_b",
        password="pass",
        feedyard=feedyard_b,
        language=User.Language.EN,
    )
    Token.objects.create(user=user, key="token-b")
    return user


@pytest.fixture
def adg_params():
    return {
        "start_date": "2026-06-02",
        "end_date": "2026-06-11",
    }
