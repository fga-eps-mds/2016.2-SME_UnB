from django import forms
from .models import EnergyTransductor, TransductorModel


class EnergyForm(forms.ModelForm):
    tranductorModel = TransductorModel.objects.all()
    transductor_model = forms.ModelChoiceField(queryset=TransductorModel,
                                               required=True,
                                               initial=0)

    class Meta:
        model = EnergyTransductor
        fields = ('serie_number', 'ip_address', 'description',)
