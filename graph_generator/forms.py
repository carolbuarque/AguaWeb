from django import forms

from .models import Posto

class FormCriaPosto(forms.ModelForm):
    class Meta:
        model = Posto
        fields = ['codigo_ana']
        labels = {'Código ANA': ''}