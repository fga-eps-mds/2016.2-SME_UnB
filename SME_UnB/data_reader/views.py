from django.shortcuts import render
from django.views import generic
from .models import Transductor
from django.shortcuts import get_object_or_404, render

class IndexView(generic.ListView):
     template_name = 'data_reader/index.html'
     context_object_name = 'transductors_list'
 
     def get_queryset(self):
         return Transductor.objects.all()


def detail(request, transductor_id):
    template_name = 'data_reader/detail.html'
    transductor = get_object_or_404(Transductor, pk=transductor_id)
    data_list = Transductor.objects.get(id=transductor_id).measurements_set.all()

    return render(request, template_name, {'data_list': data_list})