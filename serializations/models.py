from django.db import models
from batches.models import Batch


class Serialization(models.Model):
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name='serializations')
    serial_number = models.CharField(max_length=255, unique=True)
    status = models.CharField(max_length=50, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'serializations'
        indexes = [
            models.Index(fields=['serial_number']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return self.serial_number


