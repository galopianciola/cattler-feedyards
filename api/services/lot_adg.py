from datetime import date

from django.db.models import Sum

from api.models import Lot, WeightRecord


def calculate_lot_adg(lot: Lot, from_date: date, to_date: date) -> float:
    totals = {
        row["date"]: row["total_weight"]
        for row in (
            WeightRecord.objects.filter(
                animal__lot=lot,  # todos los animales del lote
                date__in=[from_date, to_date],
            )
            .values("date")
            .annotate(total_weight=Sum("weight"))
        )
    }

    initial_weight = totals.get(from_date, 0.0)
    final_weight = totals.get(to_date, 0.0)
    days_difference = (to_date - from_date).days

    return (final_weight - initial_weight) / days_difference


def calculate_lot_adg_from_entry_date(lot: Lot, to_date: date) -> float:
    entry_date = lot.animals.values_list("entry_date", flat=True).first()
    return calculate_lot_adg(lot, entry_date, to_date)
