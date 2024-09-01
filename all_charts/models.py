"""Model classes."""

from django.db import models

from datetime import datetime


class DataForChart(models.Model):
    """Data for chart."""

    id = models.AutoField(primary_key=True)
    date = models.DateField(unique=True, blank=False, null=False)
    data = models.JSONField()

    def __str__(self):
        """String representation."""

        return datetime.strftime(self.date, "%Y/%m/%d")
