from django.shortcuts import render
from django.views import generic


class IndexView(generic.ListView):
    template_name = 'data_reader/index.html'
    context_object_name = 'transductors'