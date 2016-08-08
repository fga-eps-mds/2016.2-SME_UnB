from django.views import generic
from .models import Transductor, TransductorManager
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponseRedirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse
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
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            transductor = form.save(commit=False)
            transductor.creation_date = timezone.now()
            transductor.transductor_manager = TransductorManager.objects.all().first()
            transductor.save()

            # Fix communication protocol
            # cp = CommunicationProtocol.all().first()

            return redirect('data_reader:detail', transductor_id=transductor.id)
    else:
        form = PostForm()
    return render(request, 'data_reader/new.html', {'form': form})


def edit(request, pk):
    post = get_object_or_404(Transductor, pk=pk)
    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            transductor = form.save(commit=False)
            transductor.transductor_manager = TransductorManager.objects.all().first()
            transductor.save()
            return redirect('/data_reader')
    else:
        form = PostForm(instance=post)
    return render(request, 'data_reader/new.html', {'form': form})


def delete(request, pk):
    transductor = get_object_or_404(Transductor, pk=pk)
    transductor.delete()

    return HttpResponseRedirect(reverse('data_reader:index'))
