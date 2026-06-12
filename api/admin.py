from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.db.models import Avg, Count, Min, OuterRef, Subquery, Sum
from django.db.models.expressions import F, Value
from django.db.models.fields import FloatField
from django.db.models.functions import Coalesce
from django.utils import timezone

from api.models import Feedyard, Lot, User, WeightRecord


@admin.register(Lot)
class LotAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "feedyard",
        "animals_quantity",
        "entry_date",
        "average_weight",
        "adg_since_entry_date",
    ]
    list_filter = ["feedyard"]
    search_fields = ["name"]

    def get_queryset(self, request):
        today = timezone.localdate()
        queryset = super().get_queryset(request).select_related("feedyard")

        queryset = queryset.annotate(
            animals_quantity=Count("animals"),
            entry_date=Min("animals__entry_date"),  # todos iguales
            average_weight=Avg("animals__current_weight"),
        )

        initial_weight = (
            WeightRecord.objects.filter(
                animal__lot=OuterRef("pk"),
                date=F("animal__entry_date"),
            )
            .values("animal__lot")
            .annotate(total_weight=Sum("weight"))
            .values("total_weight")
        )

        final_weight = (
            WeightRecord.objects.filter(
                animal__lot=OuterRef("pk"),
                date=today,
            )
            .values("animal__lot")
            .annotate(total_weight=Sum("weight"))
            .values("total_weight")
        )

        return queryset.annotate(
            initial_weight=Coalesce(
                Subquery(initial_weight, output_field=FloatField()),
                Value(0.0),
                output_field=FloatField(),
            ),
            final_weight=Coalesce(
                Subquery(final_weight, output_field=FloatField()),
                Value(0.0),
                output_field=FloatField(),
            ),
        )

    @admin.display(ordering="animals_quantity", description="Animals")
    def animals_quantity(self, obj):
        return obj.animals_quantity

    @admin.display(ordering="entry_date", description="Entry date")
    def entry_date(self, obj):
        return obj.entry_date

    @admin.display(ordering="average_weight", description="Avg weight")
    def average_weight(self, obj):
        if obj.average_weight is None:
            return "-"
        return round(obj.average_weight, 2)

    @admin.display(description="ADG (entry → today)")
    def adg_since_entry_date(self, obj):
        if obj.entry_date is None:
            return "-"
        days = (timezone.localdate() - obj.entry_date).days
        if days == 0:
            return 0
        return round((obj.final_weight - obj.initial_weight) / days, 2)


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = (*UserAdmin.list_display, "feedyard", "language")
    list_filter = (*UserAdmin.list_filter, "feedyard", "language")

    fieldsets = (
        *UserAdmin.fieldsets,
        ("Cattler", {"fields": ("feedyard", "language")}),
    )

    add_fieldsets = (
        *UserAdmin.add_fieldsets,
        ("Cattler", {"fields": ("feedyard", "language")}),
    )


admin.site.register(Feedyard)
