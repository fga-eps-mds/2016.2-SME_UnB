from django.shortcuts import render

from django.shortcuts import render
from django.views.generic import CreateView
from django.http import HttpResponseRedirect
from django.contrib.auth.views import login
from django.contrib.auth.views import logout
from django.contrib.auth.decorators import login_required

from django.core.urlresolvers import reverse_lazy, reverse

def home(request):
    return render(request, 'users/home.html')

@login_required
def dashboard(request):
    return render(request, 'users/dashboard.html')


def login_view(request, *args, **kwargs):
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('users:dashboard'))
    else:
        kwargs['extra_context'] = {'next': reverse('users:dashboard')}
        kwargs['template_name'] = 'users/login.html'
        return login(request, *args, **kwargs)

def logout_view(request, *args, **kwargs):
    kwargs['next_page'] = reverse('index')
    return logout(request, *args, **kwargs)
