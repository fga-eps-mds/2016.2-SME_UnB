from __future__ import absolute_import

from django.conf.urls import url
from django.core.urlresolvers import reverse

from djangoplugins.point import PluginPoint

import plugins.views


class BasePlugin(PluginPoint):
    urls = [
        url(r'^$', plugins.views.content_list, name='content-list'),
        url(r'^create/$', plugins.views.content_create,
            name='content-create')
    ]

    instance_urls = [
        url(r'^$', plugins.views.content_read, name='content-read')
    ]

    def get_list_url(self):
        return reverse('content-list')

    def get_create_url(self):
        return reverse('content-create')

    def get_read_url(self, content):
        return reverse('content-read', args=[content.pk])
