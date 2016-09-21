""" Represents the User's views, and it contains all the elements
as the interface. For example buttons, text, boxes, etc."""
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.views import login
from django.contrib.auth.views import logout
from django.core.urlresolvers import reverse_lazy, reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import CreateView


def home(request):
    return render(request, 'users/home.html')


@login_required
def dashboard(request):
    return render(request, 'users/dashboard.html')


def show_login(request):
    if request.method == "GET":
        return render(request, "users/login.html")
    else:
        context = make_login(request)

        if context.get('is_logged'):
            return HttpResponseRedirect(reverse("users:dashboard"))
        else:
            return render(request, "users/login.html", context)


def make_login(request):
    form = request.POST
    username = form.get('username')
    password = form.get('password')

    user = authenticate(username=username, password=password)
    is_logged = False

    if user is not None:
        login(request, user)
        message = "Logged"
        is_logged = True
    else:
        message = "Incorrect user"

    context = {
        "is_logged": is_logged,
        "message": message,
    }

    return context

def logout_view(request, *args, **kwargs):
    kwargs['next_page'] = reverse('index')
    return logout(request, *args, **kwargs)

@login_required
def register(request):

    if request.method == "GET":
        return render(request,'userRegister/register.html')
    else:
        form = request.POST
        first_name = form.get('first_name')
        last_name =  form.get('last_name')
        password = form.get('password')
        confirPassword = form.get('confirmPassword')
        email = form.get('email')


        if not first_name.isalpha() or not last_name.isalpha():
            return render(request,'userRegister/register.html', {'falha':'Nome deve conter apenas letras'})
        if '@' not in email or '.' not in email or ' ' in email:
            return render(request,'userRegister/register.html', {'falha':'Email invalido! Esse e-mail nao esta em um formato valido'})
        if User.objects.filter(email=email).exists():
            return render(request,'userRegister/register.html', {'falha':'Email invalido! Esse e-mail ja esta cadastrado no nosso banco de dados'})
        if len(password) <6:
            return render(request,'userRegister/register.html', {'falha':'Senha Invalida, digite uma senha com no minimo 6 letras'})
        if password !=confirPassword:
            return render(request,'userRegister/register.html', {'falha':'Senha invalida! Senhas de cadastros diferentes'})


        user = User.objects.create_user(username=first_name,password=password,email=email)
        user.last_name = last_name
        user.first_name = first_name
        user.save()

        return render(request,'users/dashboard.html')

@login_required
def list_user_edit(request):

    users = User.objects.all()
    return render(request,'users/list_user_edit.html',{'users':users})

@login_required
def list_user_delete(request):

    users = User.objects.all()
    return render(request,'users/list_user_delete.html',{'users':users})

@login_required
def edit_user(request,user_id):

    user = User.objects.get(id=user_id)
    if request.method == "GET":
        return render(request,'users/edit_user.html',{'user':user})
    else:
        form = request.POST
        first_name = form.get('first_name')
        last_name =  form.get('last_name')
        password = form.get('password')
        confirPassword = form.get('confirmPassword')
        email = form.get('email')


        if first_name != "":
            if not first_name.isalpha():
                return render(request,'users/edit_user.html', {'falha':'Nome deve conter apenas letras','user':user})

            user.first_name = first_name

        if last_name != "":
            if not last_name.isalpha():
                return render(request,'users/edit_user.html', {'falha':'Nome deve conter apenas letras','user':user})

            user.last_name  =last_name


        if email != '':
            if '@' not in email or '.' not in email or ' ' in email:
                return render(request,'users/edit_user.html', {'falha':'Email invalido! Esse e-mail nao esta em um formato valido','user':user})
            if User.objects.filter(email=email).exists():
                return render(request,'users/edit_user.html', {'falha':'Email invalido! Esse e-mail ja esta cadastrado no nosso banco de dados','user':user})

            user.username = email

        if password != '':
            if len(password) < 6:
                return render(request,'users/edit_user.html', {'falha':'Senha Invalida, digite uma senha com no minimo 6 letras','user':user})
            if password !=confirPassword:
                return render(request,'users/edit_user.html', {'falha':'Senha invalida! Senhas de cadastros diferentes', 'user':user})

            user.set_password(password)




        user.save()

        return render(request,'users/edit_user.html',{'info':'usuario modificado com sucesso', 'user':user})

@login_required
def delete_user(request,user_id):

    user = User.objects.get(id=user_id)
    if request.method == "GET":
        return render(request,'users/delete_user.html',{'user':user})
    else:
            user.delete()

    return render (request, 'users/dashboard.html',{'info':'usuario deletado com sucesso'})
