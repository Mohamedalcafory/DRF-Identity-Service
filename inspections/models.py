from django.db import models
from batches.models import Batch


class Inspection(models.Model):
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name='inspections')
    inspector_name = models.CharField(max_length=255)
    result = models.CharField(max_length=50)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'inspections'
        indexes = [
            models.Index(fields=['result']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"Inspection {self.id} - {self.result}"


