from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from api.constants import MIN_ANIMALS_PER_LOT, MIN_LOT_AVERAGE_WEIGHT
from api.exceptions import ConflictValidationError
from api.mixins import ConflictOnValidationErrorMixin
from api.models import Lot
from api.services.lot_creation import create_lot_with_animals
from api.services.lot_weight_update import update_lot_weight


class LotReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lot
        fields = ["id", "name"]
        read_only_fields = ["id", "name"]


class LotSerializer(
    ConflictOnValidationErrorMixin, serializers.Serializer
):  # primero el mixin, luego Serializer para que se encuentre primero su is_valid
    quantity = serializers.IntegerField()
    entry_date = serializers.DateField()
    average_weight = serializers.FloatField()

    def validate_quantity(self, value):
        if value < MIN_ANIMALS_PER_LOT:
            raise ConflictValidationError(
                detail=_(
                    "Animal quantity must be greater than or equal to %(min_quantity)s."
                )
                % {
                    "min_quantity": MIN_ANIMALS_PER_LOT,
                },
            )
        return value

    def validate_average_weight(self, value):
        if value <= MIN_LOT_AVERAGE_WEIGHT:
            raise ConflictValidationError(
                detail=_("Lot average weight must be greater than %(min_weight)s.")
                % {
                    "min_weight": MIN_LOT_AVERAGE_WEIGHT,
                },
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
        return LotReadSerializer(instance).data


class LotWeightUpdateSerializer(ConflictOnValidationErrorMixin, serializers.Serializer):
    from_date = serializers.DateField()
    average_weight = serializers.FloatField()

    def validate_from_date(self, value):
        if value > timezone.localdate():
            raise ConflictValidationError(
                detail=_("From date cannot be in the future."),
            )
        return value

    def validate(self, attrs):
        lot = self.context["lot"]
        entry_date = lot.animals.values_list("entry_date", flat=True).first()
        if attrs["from_date"] < entry_date:
            raise ConflictValidationError(
                detail=_("From date must be greater than or equal to the entry date."),
            )
        return attrs

    def validate_average_weight(self, value):
        if value <= MIN_LOT_AVERAGE_WEIGHT:
            raise ConflictValidationError(
                detail=_("Lot average weight must be greater than %(min_weight)s.")
                % {
                    "min_weight": MIN_LOT_AVERAGE_WEIGHT,
                },
            )
        return value

    def update(self, instance, validated_data):
        update_lot_weight(
            lot=instance,
            from_date=validated_data["from_date"],
            average_weight=validated_data["average_weight"],
        )
        return instance

    def to_representation(self, instance):
        return LotReadSerializer(instance).data


class LotADGQuerySerializer(ConflictOnValidationErrorMixin, serializers.Serializer):
    start_date = serializers.DateField()
    end_date = serializers.DateField()

    def validate_start_date(self, value):
        if value > timezone.localdate():
            raise ConflictValidationError(
                detail=_("Start date cannot be in the future."),
            )
        return value

    def validate_end_date(self, value):
        if value > timezone.localdate():
            raise ConflictValidationError(
                detail=_("End date cannot be in the future."),
            )
        return value

    def validate(self, attrs):
        lot = self.context["lot"]
        start_date = attrs["start_date"]
        end_date = attrs["end_date"]
        entry_date = lot.animals.values_list("entry_date", flat=True).first()

        if start_date > end_date:
            raise ConflictValidationError(
                detail=_("Start date must be less than or equal to end date."),
            )

        if start_date == end_date:
            raise ConflictValidationError(
                detail=_("Start date and end date must be different."),
            )

        if start_date < entry_date:
            raise ConflictValidationError(
                detail=_("Start date must be greater than or equal to the entry date."),
            )

        return attrs
