from django.db import models
from django.db.models import F


class ImageTransformationLog(models.Model):
    class Status(models.TextChoices):
        SUCCESS = "success", "Succès"
        ERROR = "error", "Erreur"

    image_name = models.CharField("nom de l'image", max_length=255)
    transformed_at = models.DateTimeField("date et heure", auto_now_add=True)
    status = models.CharField("statut", max_length=10, choices=Status.choices)
    error_message = models.TextField("message d'erreur", blank=True)

    class Meta:
        ordering = ["-transformed_at"]
        verbose_name = "transformation d'image"
        verbose_name_plural = "transformations d'images"

    def __str__(self):
        return f"{self.image_name} - {self.get_status_display()}"


class ImageTransformationStats(models.Model):
    successful_transformations = models.PositiveBigIntegerField(
        "nombre total d'images transformées",
        default=0,
    )
    updated_at = models.DateTimeField("dernière mise à jour", auto_now=True)

    class Meta:
        verbose_name = "compteur de transformations"
        verbose_name_plural = "compteur de transformations"

    def __str__(self):
        return f"{self.successful_transformations} images transformées"

    @classmethod
    def increment_successful_transformations(cls):
        stats, _ = cls.objects.get_or_create(pk=1)
        cls.objects.filter(pk=stats.pk).update(
            successful_transformations=F("successful_transformations") + 1,
        )

    @classmethod
    def get_total_successful_transformations(cls) -> int:
        stats = cls.objects.filter(pk=1).first()
        if stats is None:
            return 0

        return stats.successful_transformations
