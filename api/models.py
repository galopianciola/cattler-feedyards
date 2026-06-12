from django.contrib.auth.models import AbstractUser
from django.db import models


class Feedyard(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name = "Feedyard"
        verbose_name_plural = "Feedyards"

    def __str__(self):
        return self.name


class Lot(models.Model):
    name = models.CharField(max_length=255)
    feedyard = models.ForeignKey(Feedyard, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Lot"
        verbose_name_plural = "Lots"

    def __str__(self):
        return self.name


class Animal(models.Model):
    lot = models.ForeignKey(Lot, on_delete=models.CASCADE, related_name="animals")
    entry_date = models.DateField()
    initial_weight = models.FloatField()
    current_weight = models.FloatField()

    class Meta:
        verbose_name = "Animal"
        verbose_name_plural = "Animals"

    def __str__(self):
        return f"{self.lot.name} - {self.entry_date}"


class WeightRecord(models.Model):
    animal = models.ForeignKey(
        Animal, on_delete=models.CASCADE, related_name="weight_records"
    )
    weight = models.FloatField()
    date = models.DateField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["animal", "date"], name="unique_weight_record_per_day"
            )
        ]
        verbose_name = "Weight Record"
        verbose_name_plural = "Weight Records"

    def __str__(self):
        return f"{self.animal.lot.name} - {self.date} ({self.weight} kg)"


class User(AbstractUser):
    feedyard = models.ForeignKey(
        Feedyard, on_delete=models.PROTECT, related_name="users"
    )

    class Language(models.TextChoices):
        EN = "en", "English"
        ES = "es", "Spanish"

    language = models.CharField(
        max_length=2, choices=Language.choices, default=Language.ES
    )

    def __str__(self):
        return self.get_full_name() or self.username

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
