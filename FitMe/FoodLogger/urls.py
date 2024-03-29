from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('food-search/', views.food_search, name='food_search'),
    path('food-nutrients/<int:fdc_id>/', views.food_detail, name='food_detail'),
    
]