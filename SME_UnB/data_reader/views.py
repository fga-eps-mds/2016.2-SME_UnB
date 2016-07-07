from django.views import generic
from .models import *
from django.shortcuts import get_object_or_404, render, redirect
from .forms import PostForm
from django.utils import timezone

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

def new(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            transductor = form.save(commit=False)
            transductor.creation_date = timezone.now()
            transductor.transductor_manager = TransductorManager.objects.all().first()
            transductor.save()

            # Fix communication protocol
            # cp = CommunicationProtocol.all().first()

            return redirect('detail', transductor_id=transductor.id)
    else:
        form = PostForm()
    return render(request, 'data_reader/new.html', {'form': form})