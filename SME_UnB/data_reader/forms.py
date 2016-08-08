from django import forms

from .models import Transductor


class PostForm(forms.ModelForm):

    class Meta:
        model = Transductor
        fields = ('serie_number', 'ip_address', 'description',)
