from .models import EnergyTransductor, TransductorModel
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponseRedirect
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse
from .forms import EnergyForm, DeleteEnergyForm
from django.utils import timezone
from django.contrib.auth.decorators import login_required


def index(request):
    template_name = 'transductor/index.html'
    transductors_list = EnergyTransductor.objects.all()

    return render(request, template_name, {'transductors_list': transductors_list})

@login_required
def detail(request, transductor_id):
    template_name = 'transductor/detail.html'
    transductor = get_object_or_404(EnergyTransductor, pk=transductor_id)
    measurements = EnergyTransductor.objects.get(id=transductor_id).energymeasurements_set.all()
    paginator = Paginator(measurements, 4)
    page = request.GET.get('page')

    try:
        data = paginator.page(page)
    except PageNotAnInteger:
        data = paginator.page(1)
    except EmptyPage:
        data = paginator.page(paginator.num_pages)

    return render(request, template_name, {'measurements': data, 'transductor': transductor})

@login_required
def new(request):
    if request.POST:
        form = EnergyForm(request.POST)

        if form.is_valid():
            transductor = EnergyTransductor()
            transductor.serie_number = form.cleaned_data['serie_number']
            transductor.ip_address = form.cleaned_data['ip_address']
            transductor.description = form.cleaned_data['description']
            transductor.model = form.cleaned_data['transductor_model']
            transductor.creation_date = timezone.now()

            transductor.save()

            return redirect('transductor:detail', transductor_id=transductor.id)
    else:
        form = EnergyForm()

    return render(request, 'transductor/new.html', {'form': form})

@login_required
def edit(request, transductor_id):
    transductor = get_object_or_404(EnergyTransductor, pk=transductor_id)

    if request.POST:
        form = EnergyForm(request.POST, instance=transductor)

        if form.is_valid():
            form.save()

            return redirect('transductor:index')
    else:
        form = EnergyForm(instance=transductor)

    return render(request, 'transductor/new.html', {'form': form})

@login_required
def delete(request, transductor_id):
    transductor = get_object_or_404(EnergyTransductor, pk=transductor_id)

    if request.POST:
        form = DeleteEnergyForm(request.POST, instance=transductor)

        if form.is_valid():
            transductor.delete()

    return HttpResponseRedirect(reverse('transductor:index'))


def model_index(request):
    template_name = 'transductor/model_index.html'
    transductors_models = TransductorModel.objects.all()

    return render(request, template_name, {'transductors_models': transductors_models})
