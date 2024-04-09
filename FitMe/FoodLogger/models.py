from django.db import models

# Create your models here.
class WeightEntry(models.Model):
    date = models.DateField()
    weight = models.DecimalField(max_digits=5, decimal_places=2)