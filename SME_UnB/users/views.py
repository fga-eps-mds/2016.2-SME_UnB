""" Represents the User's views, and it contains all the elements
as the interface. For example buttons, text, boxes, etc."""
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Permission
from django.contrib.auth.views import login
from django.contrib.auth.views import logout
from django.core.urlresolvers import reverse_lazy, reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
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
        return render(request, 'userRegister/register.html')
    else:
        form = request.POST
        first_name = form.get('first_name')
        last_name = form.get('last_name')
        password = form.get('password')
        confirPassword = form.get('confirmPassword')
        email = form.get('email')

        check_name(request, first_name, last_name)
        check_email(request, email)
        check_email_exist(request, email)
        check_password_lenght(request, password, confirPassword)
        check_password(request, password, confirPassword)
        # Fim do bloco que saira da view

        try:
            user = User.objects.create_user(
                first_name=first_name, last_name=last_name, password=password, username=email)
        except:
            return render(request, 'userRegister/register.html', {'falha': 'Email invalido!'})

        user.last_name = last_name
        user.first_name = first_name
        user.email = email
        give_permission(request, user)
        user.save()

        return render(request, 'users/dashboard.html')

def check_name(request, first_name, last_name):
    if not first_name.isalpha() or not last_name.isalpha():
        return render(
            request,
            'userRegister/register.html',
            {'falha': 'Nome deve conter apenas letras'})

def check_email(request, email):
    if '@' not in email or '.' not in email or ' ' in email:
        return render(
            request,
            'userRegister/register.html',
            {'falha': 'Email invalido! Esse e-mail nao esta em um formato valido'})

def check_email_exist(request, email):
    if User.objects.filter(email=email).exists():
        return render(
            request,
            'userRegister/register.html',
            {'falha': 'Email invalido! Esse e-mail ja esta cadastrado no nosso banco de dados'})

def check_password_lenght(request, password, confirPassword):
    if len(password) < 6 and password != confirPassword:
        return render(
            request,
            'userRegister/register.html',
            {'falha': 'Senha Invalida, digite uma senha com no minimo 6 letras'})

def check_password(request, password, confirPassword):
    if password != confirPassword:
        return render(
            request,
            'userRegister/register.html',
            {'falha': 'Senha invalida! Senhas de cadastros diferentes'})

@login_required
def list_user_edit(request):

    return __list__(request, 'users/list_user_edit.html')

@login_required
def list_user_delete(request):

    return __list__(request, 'users/list_user_delete.html')

def check_permissions(user):

    has_report_permission = 'checked' if user.has_perm('report.can_generate') else ''
    has_transductor_permission = 'checked' if user.has_perm('transductor.can_view_transductors') else ''
    has_edit_user_permission = 'checked' if user.has_perm('users.can_edit_user') else ''
    has_delete_user_permission = 'checked' if user.has_perm('users.can_delete_user') else ''

    context = {
        'user': user,
        "can_generate": has_report_permission,
        "view_transductors": has_transductor_permission,
        "edit_users": has_edit_user_permission,
        "delete_users": has_delete_user_permission,
    }

    return context


@login_required
def edit_user(request, user_id):

    user = User.objects.get(id=user_id)

    if request.method == "GET":
        context = check_permissions(user)
        return render(request, 'users/edit_user.html', context)

    else:
        form = request.POST
        first_name = form.get('first_name')
        last_name =  form.get('last_name')
        password = form.get('password')
        confirPassword = form.get('confirmPassword')
        email = form.get('email')

        if first_name != "":

            if not first_name.isalpha():

                return __prepare_error_render__(request, 'Nome deve conter apenas letras', user)

            user.first_name = first_name

        if last_name != "":
            if not last_name.isalpha():

                return __prepare_error_render__(request, 'Nome deve conter apenas letras', user)

            user.last_name = last_name

        if email != '':
            if '@' not in email or '.' not in email or ' ' in email:

                return __prepare_error_render__(request, 'Email invalido! Esse e-mail nao esta em um formato valido', user)

            if User.objects.filter(email=email).exists():

                return __prepare_error_render__(request, 'Email invalido! Esse e-mail ja esta cadastrado no nosso banco de dados', user)

            user.username = email
            user.email = email

        if password != '':
            if len(password) < 6:

                return __prepare_error_render__(request, 'Senha Invalida, digite uma senha com no minimo 6 letras', user)
            if password != confirPassword:

                return __prepare_error_render__(request, 'Senha invalida! Senhas de cadastros diferentes', user)

            user.set_password(password)

        give_permission(request, user)

        context = check_permissions(user)
        context['info'] = 'usuario modificado com sucesso'

        return render(request, 'users/edit_user.html', context)


def give_permission(request, user):

    report_checkbox = request.POST.get('can_generate')
    transductor_checkbox = request.POST.get('view_transductors')
    useredit_checkbox = request.POST.get('edit_users')
    userdelete_checkbox = request.POST.get('delete_users')

    user.user_permissions.clear()

    __permision__(report_checkbox, 'can_generate', user)
    __permision__(transductor_checkbox, 'can_view_transductors', user)
    __permision__(useredit_checkbox, 'can_edit_user', user)
    __permision__(userdelete_checkbox, 'can_delete_user', user)

    user.save()

@login_required
def delete_user(request, user_id):

    user = User.objects.get(id=user_id)
    if request.method == "GET":
        return render(request, 'users/delete_user.html', {'user': user})
    else:
        user.delete()

    return render (request, 'users/dashboard.html', {'info': 'usuario deletado com sucesso'})

def __list__(request, template):

    users = User.objects.all()
    return render(request, template, {'users':users})

def __prepare_error_render__(request, fail_message, user):

    return render(request, 'user/edit_user.html', {'falha': fail_message, 'user': user})

def __permision__(permision_type, codename, user):

    if permision_type == 'on':
        permision = Permission.objects.get(codename=codename)
        user.user_permissions.add(permision)
