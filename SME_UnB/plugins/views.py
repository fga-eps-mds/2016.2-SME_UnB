from __future__ import absolute_import
from django.http import HttpResponseRedirect

from django.shortcuts import render
from django.shortcuts import get_object_or_404

import plugins


def index(request):
    return render(request, 'index.html')


def content_list(request, plugin):
    return render(request, 'content/list.html', {
        'plugin': plugins.plugins.BasePlugin.get_plugin(plugin),
        'reports': plugins.models.Report.objects.all(),
    })


def content_create(request, plugin):
    import plugins.forms

    plugin = plugins.plugins.BasePlugin.get_plugin(plugin)
    if request.method == 'POST':
        form = plugins.forms.ContentForm(request.POST)
        if form.is_valid():
            content = form.save(commit=False)
            content.plugin = plugin.get_model()
            content.save()
            return HttpResponseRedirect(content.get_absolute_url())
        else:
            return "[ERROR] from views: {0}".format(form.errors)
    else:
        form = plugins.forms.ContentForm()
    return render(request, 'content/form.html', {
        'form': form,
    })


def content_read(request, pk, plugin):
    plugin = plugins.plugins.BasePlugin.get_plugin(plugin)
    content = get_object_or_404(plugins.models.Report,
                                pk=pk, plugin=plugin.get_model())
    return render(request, 'content/detail.html', {
        'plugin': plugin,
        'content': content,
        'data_list': content.transductor.measurements_set.all(),
    })
