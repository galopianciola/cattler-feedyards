from datetime import date, timedelta

from django.db import transaction
from django.utils import timezone

from api.models import Animal, Feedyard, Lot, WeightRecord


@transaction.atomic
def create_lot_with_animals(
    feedyard: Feedyard, quantity: int, entry_date: date, average_weight: float
):
    lot = Lot.objects.create(
        feedyard=feedyard, name=f"Lote {entry_date.strftime('%d-%m-%Y')}"
    )
    animals = [
        Animal(
            lot=lot,
            entry_date=entry_date,
            initial_weight=average_weight,
            current_weight=average_weight,
        )
        for _ in range(quantity)
    ]
    Animal.objects.bulk_create(animals, batch_size=5000)

    days_from_entry_date = (timezone.localdate() - entry_date).days
    dates = [entry_date + timedelta(days=d) for d in range(days_from_entry_date + 1)]

    weight_records = [
        WeightRecord(
            animal_id=animal.pk,
            weight=average_weight,
            date=d,
        )
        for animal in animals
        for d in dates
    ]

    WeightRecord.objects.bulk_create(weight_records, batch_size=5000)
    return lot
