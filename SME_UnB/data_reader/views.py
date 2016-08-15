from django.views import generic
from .models import EnergyTransductor
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponseRedirect
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse
from .forms import EnergyForm
from django.utils import timezone


class IndexView(generic.ListView):
    template_name = 'data_reader/index.html'
    context_object_name = 'transductors_list'

    def get_queryset(self):
        return EnergyTransductor.objects.all()


def detail(request, transductor_id):
    template_name = 'data_reader/detail.html'
    transductor = get_object_or_404(EnergyTransductor, pk=transductor_id)

    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # trocar por measurements
    data_list = EnergyTransductor.objects.get(id=transductor_id).energymeasurements_set.all()

    paginator = Paginator(data_list, 4)
    page = request.GET.get('page')

    try:
        data = paginator.page(page)
    except PageNotAnInteger:
        data = paginator.page(1)
    except EmptyPage:
        data = paginator.page(paginator.num_pages)

    return render(request, template_name, {'data_list': data, 'transductor': transductor})


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
                return render(request, 'data_reader/new.html', {'form': form, 'errors': errors})

            return redirect('data_reader:detail', transductor_id=transductor.id)
    else:
        form = EnergyForm()
    return render(request, 'data_reader/new.html', {'form': form})


def edit(request, pk):
    transductor = get_object_or_404(EnergyTransductor, pk=pk)

    if request.POST:
        form = EnergyForm(request.POST, instance=transductor)

        if form.is_valid():
            edited_transductor = form.save(commit=False)

            try:
                edited_transductor.save()
            except ValidationError, err:
                errors = '; '.join(err.messages)
                return render(request, 'data_reader/new.html', {'form': form, 'errors': errors})

            return redirect('data_reader:index')
    else:
        form = EnergyForm(instance=transductor)

    return render(request, 'data_reader/new.html', {'form': form})


def delete(request, pk):
    transductor = get_object_or_404(EnergyTransductor, pk=pk)
    transductor.delete()

    return HttpResponseRedirect(reverse('data_reader:index'))
