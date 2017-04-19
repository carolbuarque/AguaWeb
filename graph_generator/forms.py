from django import forms

from .models import Series

class SerieForm(forms.ModelForm):
    class Meta:
        model = Series
        fields = ['station']
        labels = {'station': ''}

#class StatsForm(forms.ModelForm):
#    class Meta:
#        model = Series
#        fields = ['stats']
#        labels = {'stats': ''}

#class GraphForm(forms.ModelForm):
#    class Meta:
#        model = Series
#        fields = ['graph']
#        labels = {'graph': ''}