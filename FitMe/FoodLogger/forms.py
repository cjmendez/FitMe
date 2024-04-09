# forms.py

from django import forms
from .models import WeightEntry

class WeightEntryForm(forms.ModelForm):
    class Meta:
        model = WeightEntry
        fields = ['date', 'weight']