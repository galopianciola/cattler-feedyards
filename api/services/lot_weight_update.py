from datetime import date, timedelta

from django.db import transaction
from django.utils import timezone

from api.models import Lot, WeightRecord


@transaction.atomic
def update_lot_weight(lot: Lot, from_date: date, average_weight: float) -> Lot:
    days_to_update = (timezone.localdate() - from_date).days
    dates = [from_date + timedelta(days=d) for d in range(days_to_update + 1)]

    weight_records = [
        WeightRecord(animal=animal, weight=average_weight, date=d)
        for animal in lot.animals.all()
        for d in dates
    ]
    WeightRecord.objects.bulk_create(
        weight_records,
        update_conflicts=True,  # activa upsert
        unique_fields=["animal", "date"],  # esto decide si insert o update
        update_fields=["weight"],  # campo a actualizar si es update
        batch_size=5000,
    )
    lot.animals.update(
        current_weight=average_weight,
    )
    return lot
