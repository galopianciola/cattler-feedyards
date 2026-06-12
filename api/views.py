from rest_framework import status
from rest_framework.generics import CreateAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.response import Response

from api.models import Lot
from api.serializers import (
    LotADGQuerySerializer,
    LotSerializer,
    LotWeightUpdateSerializer,
)
from api.services.lot_adg import calculate_lot_adg


class CreateLotView(CreateAPIView):
    serializer_class = LotSerializer

    def perform_create(self, serializer):
        serializer.save(feedyard=self.request.user.feedyard)  # tenant


class UpdateLotView(UpdateAPIView):
    serializer_class = LotWeightUpdateSerializer

    def get_queryset(self):
        return Lot.objects.filter(feedyard=self.request.user.feedyard)  # tenant

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["lot"] = self.get_object()
        return context


class LotADGView(RetrieveAPIView):
    def get(self, request, pk):
        lot = Lot.objects.filter(
            feedyard=request.user.feedyard, pk=pk
        ).first()  # tenant

        if not lot:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = LotADGQuerySerializer(
            data=request.query_params, context={"lot": lot}
        )
        serializer.is_valid(raise_exception=True)

        adg = calculate_lot_adg(
            lot,
            serializer.validated_data["start_date"],
            serializer.validated_data["end_date"],
        )
        return Response({"adg": adg})
