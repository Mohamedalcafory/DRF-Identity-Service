from django.db import models
from sites.models import Site


class Batch(models.Model):
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name='batches')
    code = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    manufacture_date = models.DateField()
    expiry_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'batches'
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['site', 'manufacture_date']),
        ]

    def __str__(self):
        return f"{self.code} @ {self.site.code}"


