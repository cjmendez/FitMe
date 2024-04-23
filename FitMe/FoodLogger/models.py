from django.db import models

# Create your models here.
class WeightEntry(models.Model):
    date = models.DateField()
    weight = models.DecimalField(max_digits=5, decimal_places=2)

class FoodEntry(models.Model):
    food_name = models.CharField(max_length=100)
    meal_type = models.CharField(max_length=20)
    calories = models.FloatField()
    protein = models.FloatField()
    carbs = models.FloatField()
    fat = models.FloatField()
    water = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.food_name
