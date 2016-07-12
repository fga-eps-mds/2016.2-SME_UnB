from __future__ import absolute_import

from django.db import models

from djangoplugins.fields import PluginField

from plugins.plugins import BasePlugin

from data_reader.models import Transductor


class Report(models.Model):
    title = models.CharField(max_length=255)
    transductor = models.ForeignKey(Transductor, on_delete=models.CASCADE)

    plugin = PluginField(BasePlugin, editable=False)

    def get_absolute_url(self):
        return self.plugin.get_plugin().get_read_url(self)
