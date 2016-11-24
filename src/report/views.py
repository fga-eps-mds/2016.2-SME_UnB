from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from django.core.urlresolvers import reverse_lazy, reverse
from django.core import serializers
from cStringIO import StringIO
from reportlab.platypus.flowables import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

from django.http import HttpResponse
from django.utils.translation import ugettext as _

import datetime

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.dates import DateFormatter
import matplotlib.patches as mpatches

from transductor.models import EnergyMeasurements, EnergyTransductor
from transductor.models import TransductorModel
import json


def create_graphic(path, array_date, array_dateb,
                   array_datec, array_data, label):
    title = _('Monitoring') + ' ' + label

    fig = Figure()

    ax = fig.add_subplot(111)
    bx = fig.add_subplot(111)
    cx = fig.add_subplot(111)
    x = []
    y = []
    yb = []
    yc = []
    xb = []
    xc = []

    for i in range(len(array_data)):
        x.append(array_data[i])
        y.append(array_date[i])
        xb.append(array_data[i])
        xc.append(array_data[i])
        yb.append(array_dateb[i])
        yc.append(array_datec[i])

    ax.plot_date(x, y, '-')
    bx.plot_date(xb, yb, '-')
    cx.plot_date(xc, yc, '-')

    patch1 = mpatches.Patch(color='blue', label=_('Phase 1'))
    patch2 = mpatches.Patch(color='green', label=_('Phase 2'))
    patch3 = mpatches.Patch(color='red', label=_('Phase 3'))

    z = [patch1, patch2, patch3]

    cx.legend(handles=z, loc=1)

    ax.set_title(title)
    ax.set_xlabel(_('Date'))
    ax.set_ylabel(label)
    ax.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))
    fig.autofmt_xdate()
    canvas = FigureCanvas(fig)

    fig.savefig(path)

    return path


def generatePdf(transductor_id):
    import time
    from reportlab.lib.enums import TA_JUSTIFY
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch

    doc = SimpleDocTemplate("src/report/static/Relatorio"+transductor_id+".pdf",
                            pagesize=letter,
                            rightMargin=72, leftMargin=72,
                            topMargin=72, bottomMargin=18)
    Story = []
    logo = "src/report/static/currentGraphic"+transductor_id+".png"
    logo2 = "src/report/static/voltageGraphic"+transductor_id+".png"
    logo3 = "src/report/static/activePowerGraphic"+transductor_id+".png"
    logo4 = "src/report/static/reactivePowerGraphic"+transductor_id+".png"
    logo5 = "src/report/static/apparentPowerGraphic"+transductor_id+".png"

    magName = "Pythonista"
    issueNum = 12
    subPrice = "99.00"
    limitedDate = "03/05/2010"
    freeGift = "tin foil hat"

    formatted_time = time.ctime()
    full_name = "SME-UnB"
    address_parts = ["Campus Universitario UnB", "Brasilia-DF, 70910-900"]

    im = Image(logo, 8 * inch, 5 * inch)
    im2 = Image(logo2, 8 * inch, 5 * inch)
    im3 = Image(logo3, 8 * inch, 5 * inch)
    im4 = Image(logo4, 8 * inch, 5 * inch)
    im5 = Image(logo5, 8 * inch, 5 * inch)

    Story.append(im)
    Story.append(im2)
    Story.append(im3)
    Story.append(im4)
    Story.append(im5)

    styles = getSampleStyleSheet()
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
    ptext = '<font size=12>{ % trans Report Energy Monitoring % }</font>'
    Story.append(Paragraph(ptext, styles["Normal"]))

    doc.build(Story)
    return 1


def __minValue(arrayData):

    arrayData.sort()
    return arrayData[0]


def __maxValue(arrayData):

    arrayData.sort(reverse=True)

    return arrayData[0]


def __average(arrayData):
    total = 0
    for i in arrayData:
        total += i

    if(len(arrayData) != 0):
        return total / len(arrayData)
    else:
        return 0

@login_required
def report(request, transductor_id):
    now = datetime.datetime.now()
    delta = datetime.timedelta(days=1)

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

    for i in EnergyMeasurements.objects.all().filter(transductor=EnergyTransductor.objects.get(id=transductor_id)):

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

        # now+=delta

    data = [4, 6, 23, 7, 4, 2]

    create_graphic(
        'src/report/static/currentGraphic' + transductor_id + '.png',
        current_a,
        current_b,
        current_c,
        date,
        _('Current'))

    create_graphic(
        'src/report/static/voltageGraphic' + transductor_id + '.png',
        voltage_a,
        voltage_b,
        voltage_c,
        date,
        _('Voltage'))

    create_graphic(
        'src/report/static/activePowerGraphic' + transductor_id + '.png',
        active_power_a,
        active_power_b,
        active_power_c,
        date,
        _('Active Power'))

    create_graphic(
        'src/report/static/reactivePowerGraphic' + transductor_id + '.png',
        reactive_power_a,
        reactive_power_b,
        reactive_power_c,
        date,
        _('Reactive Power'))

    create_graphic(
        'src/report/static/apparentPowerGraphic' + transductor_id + '.png',
        apparent_power_a,
        apparent_power_b,
        apparent_power_c,
        date,
        _('Apparent Power'))

    generatePdf(transductor_id)

    maxVoltage = [__maxValue(voltage_a),
                  __maxValue(voltage_b),
                  __maxValue(voltage_c)]

    minVoltage = [__minValue(voltage_a),
                  __minValue(voltage_b),
                  __minValue(voltage_c)]

    averageVoltage = [__average(voltage_a),
                      __average(voltage_b),
                      __average(voltage_c)]

    maxCurrent = [__maxValue(current_a),
                  __maxValue(current_b),
                  __maxValue(current_c)]

    minCurrent = [__minValue(current_a),
                  __minValue(current_b),
                  __minValue(current_c)]

    averageCurrent = [__average(current_a),
                      __average(current_b),
                      __average(current_c)]

    maxActivePower = [__maxValue(active_power_a),
                      __maxValue(active_power_b),
                      __maxValue(active_power_c)]

    minActivePower = [__minValue(active_power_a),
                      __minValue(active_power_b),
                      __minValue(active_power_c)]

    averageActivePower = [__average(active_power_a),
                          __average(active_power_b),
                          __average(active_power_c)]

    maxReactivePower = [__maxValue(reactive_power_a),
                        __maxValue(reactive_power_b),
                        __maxValue(reactive_power_c)]

    minReactivePower = [__minValue(reactive_power_a),
                        __minValue(reactive_power_b),
                        __minValue(reactive_power_c)]

    averageReactivePower = [__average(reactive_power_a),
                            __average(reactive_power_b),
                            __average(reactive_power_c)]

    maxApparentPower = [__maxValue(apparent_power_a),
                        __maxValue(apparent_power_b),
                        __maxValue(apparent_power_c)]

    minApparentPower = [__minValue(apparent_power_a),
                        __minValue(apparent_power_b),
                        __minValue(apparent_power_c)]

    averageApparentPower = [__average(apparent_power_a),
                            __average(apparent_power_b),
                            __average(apparent_power_c)]

    VoltageInformation = {'max': maxVoltage, 'min': minVoltage,
                          'average': averageVoltage}

    currentInformation = {'max': maxCurrent, 'min': minCurrent,
                          'average': averageCurrent}

    activePowerInformation = {'max': maxActivePower, 'min': minActivePower,
                              'average': averageActivePower}

    reactivePowerInformation = {'max': maxReactivePower,
                                'min': minReactivePower,
                                'average': averageReactivePower}

    apparentPowerInformation = {'max': maxApparentPower,
                                'min': minApparentPower,
                                'average': averageApparentPower}

    information = {'voltage': VoltageInformation,
                   'Current': currentInformation,
                   'activePower': activePowerInformation,
                   'reactivePower': reactivePowerInformation,
                   'apparentPower': apparentPowerInformation,
                   'transductor_id': transductor_id}

    return render(request, 'graphics/report.html', information)


@login_required
def transductors_filter(request):
    return render(request, 'graphics/transductors_filter.html',
                  {'transductors': EnergyTransductor.objects.all()})

@login_required
def transductor_list(request):
    return render(request,'invoice/transductor_list.html',{'transductors': EnergyTransductor.objects.all()});

def open_pdf(request,transductor_id):
    with open('src/report/static/Relatorio'+transductor_id+'.pdf', 'r') as pdf:
        response = HttpResponse(pdf.read(), content_type='application/pdf')
        response['Content-Disposition'] = 'filename=Relatorio' + \
        transductor_id+'.pdf'
        return response
    pdf.closed

@login_required
def invoice(request, transductor_id):
    context = {
    'transductor_id': transductor_id
    }
    return render(request, 'invoice/invoice.html', context)


def get_measurements_filter_transductor(request, transductor_id):
    measurements = EnergyMeasurements.objects.all().filter(transductor = EnergyTransductor.objects.get(id = transductor_id))
    return HttpResponse(serializers.serialize('json',measurements),'application/json')

def list_transductors(request):
    return HttpResponse(serializers.serialize('json',EnergyTransductor.objects.all()))

@login_required
def return_chart(request):
    return render(request,'graphics/chart.html', {'all_transductors' : EnergyTransductor.objects.all()})
