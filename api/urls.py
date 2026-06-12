from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token

from api.views import CreateLotView, LotADGView, UpdateLotView

urlpatterns = [
    path("auth/token/", obtain_auth_token, name="get-auth-token"),
    path("lots/", CreateLotView.as_view(), name="create-lot"),
    path("lots/<int:pk>/adg/", LotADGView.as_view(), name="get-lot-adg"),
    path("lots/<int:pk>/", UpdateLotView.as_view(), name="update-lot"),
]
