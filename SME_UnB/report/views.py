from django.shortcuts import render

from django.shortcuts import render
from django.views.generic import CreateView
from django.http import HttpResponseRedirect
from django.contrib.auth.views import login
from django.contrib.auth.views import logout
from django.contrib.auth.decorators import login_required

from django.core.urlresolvers import reverse_lazy, reverse

import random
import django
import datetime

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.dates import DateFormatter

def create_voltage_graphic():

    fig=Figure()
    ax=fig.add_subplot(111)
    x=[]
    y=[]


    now=datetime.datetime.now()
    delta=datetime.timedelta(days=1)

    for i in range(10):
        x.append(now)
        now+=delta
        y.append(random.randint(0, 1000))

    ax.plot_date(x, y, '-')
    ax.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))
    fig.autofmt_xdate()
    canvas=FigureCanvas(fig)
    response=django.http.HttpResponse(content_type='image/png')
    canvas.print_png(response)


    path = 'report/static/voltageGraphic.png'
    fig.savefig(path)
    return path


def create_current_graphic():

    fig=Figure()
    ax=fig.add_subplot(111)
    x=[]
    y=[]


    now=datetime.datetime.now()
    delta=datetime.timedelta(days=1)

    for i in range(10):
        x.append(now)
        now+=delta
        y.append(random.randint(0, 1000))

    ax.plot_date(x, y, '-')
    ax.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))
    fig.autofmt_xdate()
    canvas=FigureCanvas(fig)
    response=django.http.HttpResponse(content_type='image/png')
    canvas.print_png(response)


    path = 'report/static/currentGraphic.png'
    fig.savefig(path)

    return path

def report(request):
    create_voltage_graphic()
    create_current_graphic()

    return render(request,'graphics/report.html')
