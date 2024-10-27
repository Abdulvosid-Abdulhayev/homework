from django import forms
from .models import FoodType, Food

class FoodTypeForm(forms.ModelForm):
    class Meta:
        model = FoodType
        fields = ['name']

class FoodForm(forms.ModelForm):
    class Meta:
        model = Food
        fields = ['food_type', 'name', 'ingredients', 'price']
