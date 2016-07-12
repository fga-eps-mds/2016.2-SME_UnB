from __future__ import absolute_import

from django import forms

from .models import Report


class ContentForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = '__all__'
