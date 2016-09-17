from django.shortcuts import render
from django.shortcuts import render
from django.views.generic import CreateView
from django.http import HttpResponseRedirect
from django.contrib.auth.views import login
from django.contrib.auth.views import logout
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse_lazy, reverse
from cStringIO import StringIO
from reportlab.platypus.flowables import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import sys
import PIL

import random
import django
import datetime

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.dates import DateFormatter

from transductor.models import EnergyMeasurements

def create_graphic(path,array_data,array_date, label):
    title = 'Monitoramento de ' + label

    fig=Figure()

    ax=fig.add_subplot(111)
    x=[]
    y=[]


    for i in range(len(array_data)) :
        x.append(array_date[i])
        y.append(array_data[i])


    ax.plot_date(x, y, '-')
    ax.set_title(title)
    ax.set_xlabel('Data')
    ax.set_ylabel(label)
    ax.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))
    fig.autofmt_xdate()
    canvas=FigureCanvas(fig)

    fig.savefig(path)

    return path

def generatePdf():
    import time
    from reportlab.lib.enums import TA_JUSTIFY
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch

    doc = SimpleDocTemplate("report/static/Relatorio.pdf",pagesize=letter,
                            rightMargin=72,leftMargin=72,
                            topMargin=72,bottomMargin=18)
    Story=[]
    logo = "report/static/currentGraphic.png"
    logo2 = "report/static/voltageGraphic.png"
    magName = "Pythonista"
    issueNum = 12
    subPrice = "99.00"
    limitedDate = "03/05/2010"
    freeGift = "tin foil hat"

    formatted_time = time.ctime()
    full_name = "SME-UnB"
    address_parts = ["Campus Universitario UnB", "Brasilia-DF, 70910-900"]

    im = Image(logo, 8*inch, 5*inch)
    im2 = Image(logo2, 8*inch, 5*inch)
    Story.append(im)
    Story.append(im2)

    styles=getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Justify', alignment=TA_JUSTIFY))
    ptext = '<font size=12>%s</font>' % formatted_time

    Story.append(Paragraph(ptext, styles["Normal"]))
    Story.append(Spacer(1, 12))


    ptext = '<font size=12>%s</font>' % full_name
    Story.append(Paragraph(ptext, styles["Normal"]))
    for part in address_parts:
        ptext = '<font size=12>%s</font>' % part.strip()
        Story.append(Paragraph(ptext, styles["Normal"]))

    Story.append(Spacer(1, 12))
    Story.append(Spacer(1, 12))
    ptext = '<font size=12>Relatorio do monitoramento de energia</font>'
    Story.append(Paragraph(ptext, styles["Normal"]))

    doc.build(Story)




def report(request):


    now=datetime.datetime.now()
    delta=datetime.timedelta(days=1)

    date = []
    data = []

    voltage_a = []
    voltage_b = []
    voltage_c = []
    current_a = []
    current_b = []
    current_c = []
    active_power_a = []
    active_power_b = []
    active_power_c = []
    reactive_power_a = []
    reactive_power_b = []
    reactive_power_c = []
    apparent_power_a = []
    apparent_power_b = []
    apparent_power_c = []

    for i in EnergyMeasurements.objects.all():

        date.append(i.collection_date)
        voltage_a.append(i.voltage_a)
        voltage_b.append(i.voltage_b)
        voltage_c.append(i.voltage_c)
        current_a.append(i.current_a)
        current_b.append(i.current_b)
        current_c.append(i.current_c)
        active_power_a.append(i.active_power_a)
        active_power_b.append(i.active_power_b)
        active_power_c.append(i.active_power_c)
        reactive_power_a.append(i.reactive_power_a)
        reactive_power_b.append(i.reactive_power_b)
        reactive_power_c.append(i.reactive_power_c)
        apparent_power_a.append(i.apparent_power_a)
        apparent_power_b.append(i.apparent_power_b)
        apparent_power_c.append(i.apparent_power_c)

        #now+=delta

    data = [4, 6, 23, 7, 4, 2]

    create_graphic('report/static/currentGraphic.png', current_a, date, 'Corrente')
    create_graphic('report/static/voltageGraphic.png', voltage_a, date,'Voltagem' )
    create_graphic('report/static/activePowerGraphic.png', active_power_a, date,'Potencia Ativa' )
    create_graphic('report/static/reactivePowerGraphic.png', reactive_power_a, date,'Potencia Reativa' )
    create_graphic('report/static/apparentPowerGraphic.png', apparent_power_a, date ,'Potencia Aparente' )



    generatePdf()

    return render(request,'graphics/report.html')
