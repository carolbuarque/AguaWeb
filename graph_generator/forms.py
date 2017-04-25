from django import forms

from .models import Series

class SerieForm(forms.ModelForm):
    class Meta:
        model = Series
        fields = ['station']
        labels = {'station': ''}