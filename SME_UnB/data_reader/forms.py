from django import forms
from .models import EnergyTransductor


class EnergyForm(forms.ModelForm):

    class Meta:
        model = EnergyTransductor
        fields = ('serie_number', 'ip_address', 'description',)
