from django import forms
from .models import EnergyTransductor, TransductorModel


class EnergyForm(forms.ModelForm):
    transductor_model = forms.ModelChoiceField(queryset=TransductorModel.objects.all(), required=True, initial=0)

    class Meta:
        model = EnergyTransductor
        fields = ('serie_number', 'ip_address', 'description',)


class DeleteEnergyForm(forms.ModelForm):
    class Meta:
        model = EnergyTransductor
        fields = []
