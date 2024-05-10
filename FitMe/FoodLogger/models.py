from django.db import models
from django.utils import timezone
# Create your models here.
class WeightEntry(models.Model):
    date = models.DateField()
    weight = models.DecimalField(max_digits=5, decimal_places=2)

class FoodEntry(models.Model):
    food_name = models.CharField(max_length=100)
    meal_type = models.CharField(max_length=20)
    log_date = models.DateField(default=timezone.now)  # Added this field to store the date of the log
    calories = models.FloatField()
    protein = models.FloatField()
    carbs = models.FloatField()
    fat = models.FloatField()
    
    def __str__(self):
        return f"{self.food_name} ({self.meal_type})"
