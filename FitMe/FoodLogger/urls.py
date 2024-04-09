from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('food-search/', views.food_search, name='food_search'),
    path('food-nutrients/<int:fdc_id>/', views.food_detail, name='food_detail'),
    path('add_weight_entry/', views.add_weight_entry, name='add_weight_entry'),
    path('weight_tracker/', views.weight_tracker, name='weight_tracker'),
]