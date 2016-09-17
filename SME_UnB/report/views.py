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

def create_graphic(path,array_data,array_date):

    fig=Figure()
    ax=fig.add_subplot(111)
    x=[]
    y=[]

    for i in range(len(array_data)) :
        x.append(array_date[i])
        y.append(array_data[i])


    ax.plot_date(x, y, '-')
    ax.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))
    fig.autofmt_xdate()
    canvas=FigureCanvas(fig)

    fig.savefig(path)

    return path

def report(request):


    now=datetime.datetime.now()
    delta=datetime.timedelta(days=1)

    date = []
    for i in range(6):
        date.append(now)
        now+=delta


    data = [4, 6, 23, 7, 4, 2]

    create_graphic('report/static/currentGraphic.png', data, date)
    create_graphic('report/static/voltageGraphic.png', data, date)


    return render(request,'graphics/report.html')
