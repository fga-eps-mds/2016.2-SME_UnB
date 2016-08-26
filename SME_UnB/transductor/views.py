from .models import EnergyTransductor, TransductorInfo
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponseRedirect
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse
from .forms import EnergyForm
from django.utils import timezone


def index(request):
    template_name = 'transductor/index.html'
    transductors_list = EnergyTransductor.objects.all()

    return render(request, template_name, {'transductors_list': transductors_list})


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


def new(request):
    if request.POST:
        form = EnergyForm(request.POST)

        if form.is_valid():
            transductor = EnergyTransductor()
            transductor.serie_number = form.cleaned_data['serie_number']
            transductor.ip_address = form.cleaned_data['ip_address']
            transductor.description = form.cleaned_data['description']
            transductor.creation_date = timezone.now()

            try:
                transductor.save()
            except ValidationError, err:
                errors = '; '.join(err.messages)
                return render(request, 'transductor/new.html', {'form': form, 'errors': errors})

            return redirect('transductor:detail', transductor_id=transductor.id)
    else:
        form = EnergyForm()
    return render(request, 'transductor/new.html', {'form': form})


def edit(request, transductor_id):
    transductor = get_object_or_404(EnergyTransductor, pk=transductor_id)

    if request.POST:
        form = EnergyForm(request.POST, instance=transductor)

        if form.is_valid():
            edited_transductor = form.save(commit=False)

            try:
                edited_transductor.save()
            except ValidationError, err:
                errors = '; '.join(err.messages)
                return render(request, 'transductor/new.html', {'form': form, 'errors': errors})

            return redirect('transductor:index')
    else:
        form = EnergyForm(instance=transductor)

    return render(request, 'transductor/new.html', {'form': form})


def delete(request, transductor_id):
    transductor = get_object_or_404(EnergyTransductor, pk=transductor_id)
    transductor.delete()

    return HttpResponseRedirect(reverse('transductor:index'))


def model_index(request):
    template_name = 'transductor/model_index.html'
    transductors_models = TransductorInfo.objects.all()

    return render(request, template_name, {'transductors_models': transductors_models})


def model_new(request):
    if request.POST:
        form = EnergyForm(request.POST)

        if form.is_valid():
            transductor = EnergyTransductor()
            transductor.serie_number = form.cleaned_data['serie_number']
            transductor.ip_address = form.cleaned_data['ip_address']
            transductor.description = form.cleaned_data['description']
            transductor.creation_date = timezone.now()

            try:
                transductor.save()
            except ValidationError, err:
                errors = '; '.join(err.messages)
                return render(request, 'transductor/new.html', {'form': form, 'errors': errors})

            return redirect('transductor:detail', transductor_id=transductor.id)
    else:
        form = EnergyForm()
    return render(request, 'transductor/new.html', {'form': form})    