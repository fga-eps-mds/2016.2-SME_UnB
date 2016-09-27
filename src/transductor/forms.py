from django import forms
from .models import EnergyTransductor, TransductorModel


class EnergyForm(forms.ModelForm):
    class Meta:
        model = EnergyTransductor
        fields = ('serie_number', 'ip_address', 'description',)

    model = forms.ModelChoiceField(queryset=TransductorModel.objects.all(), required=True, initial=0)


class DeleteEnergyForm(forms.ModelForm):
    class Meta:
        model = EnergyTransductor
        fields = []
