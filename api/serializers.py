from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from api.constants import MIN_ANIMALS_PER_LOT, MIN_LOT_AVERAGE_WEIGHT
from api.exceptions import ConflictValidationError
from api.services.lot_creation import create_lot_with_animals


class LotSerializer(serializers.Serializer):
    quantity = serializers.IntegerField()
    entry_date = serializers.DateField()
    average_weight = serializers.FloatField()

    def validate_quantity(self, value):
        if value < MIN_ANIMALS_PER_LOT:
            raise ConflictValidationError(
                detail=_(
                    f"Animal quantity must be greater than or equal to {MIN_ANIMALS_PER_LOT}."
                ),
            )
        return value

    def validate_average_weight(self, value):
        if value <= MIN_LOT_AVERAGE_WEIGHT:
            raise ConflictValidationError(
                detail=_(
                    f"Lot average weight must be greater than {MIN_LOT_AVERAGE_WEIGHT}."
                ),
            )
        return value

    def validate_entry_date(self, value):
        if value > timezone.localdate():
            raise ConflictValidationError(
                detail=_("Entry date cannot be in the future."),
            )
        return value

    def create(self, validated_data):
        feedyard = validated_data.pop("feedyard")
        return create_lot_with_animals(feedyard, **validated_data)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["lot"] = LotSerializer(instance).data
        return data
