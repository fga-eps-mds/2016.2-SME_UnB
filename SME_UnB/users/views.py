#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Permission
from django.contrib.auth.views import login
from django.contrib.auth.views import logout
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.contrib import messages
from django.db import IntegrityError
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import update_session_auth_hash

import os

import logging


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
        logger = logging.getLogger(__name__)
        logger.info(user.__str__() + ' User is logged')
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
    logger = logging.getLogger(__name__)
    logger.info(request.user.__str__() + ' Logout ')

    return logout(request, *args, **kwargs)


@login_required
@user_passes_test(lambda user: user.is_staff, login_url='/accounts/dashboard/')
def register(request):

    if request.method == "GET":
        return render(request, 'userRegister/register.html')
    else:
        form = request.POST
        first_name = form.get('first_name')
        last_name = form.get('last_name')
        password = form.get('password')
        confirmPassword = form.get('confirmPassword')
        email = form.get('email')

        resultCheck = fullValidationRegister(form)

        if len(resultCheck) != 0:
            return render(
                request,
                'userRegister/register.html',
                {'falha': resultCheck})

        # Fim do bloco que saira da view
        first_name = form.get('first_name')
        last_name = form.get('last_name')
        password = form.get('password')
        email = form.get('email')
        user_type = form.get('user_type')

        try:
            if user_type == 'common':
                user = User.objects.create_user(first_name=first_name,
                                                last_name=last_name,
                                                password=password,
                                                username=email)
            else:
                user = User.objects.create_superuser(first_name=first_name,
                                                     last_name=last_name,
                                                     password=password,
                                                     username=first_name,
                                                     email=email)

        except IntegrityError as e:
            return render(request, 'userRegister/register.html',
                          {'falha': 'Invalid email, email already exist'})
        except:
            return render(request, 'userRegister/register.html',
                          {'falha': 'unexpected error'})

        give_permission(request, user)
        user.save()
        messages.success(request, 'Usuario registrado com sucesso')

        return HttpResponseRedirect(reverse("users:dashboard"))

        logger = logging.getLogger(__name__)
        logger.info(request.user.__str__() + ' Registered ' + user.__str__())

        print(email)
        from django.core import mail
        connection = mail.get_connection()

        # Manually open the connection
        connection.open()

        # Construct an email message that uses the connection
        email1 = mail.EmailMessage('Hello',
                                   'Body goes here',
                                   'mds@sof2u.com',
                                   [email],
                                   connection=connection,)

        email1.send()  # Send the email
	"""
    send_mail(
            'Account registered with success',
            'Your account on SME-UNB was successfully created',
            'mds@sof2u.com',
            [email],
            fail_silently=False,
            )
    """

    return render(request, 'users/dashboard.html')


def check_name(first_name, last_name):
    if not first_name.isalpha() or not last_name.isalpha():
        return 'Nome deve conter apenas letras'
    else:
        return ''


def check_email(email):
    if '@' not in email or '.' not in email or ' ' in email:
        return ' -- Email inválido! Esse e-mail não esta em um formato válido'
    else:
        return ''


def check_email_exist(email, original_email):
    if User.objects.filter(email=email).exists() and email != original_email:
        return ' -- E-mail já esta cadastrado no nosso banco de dados'
    else:
        return ''


def check_password_lenght(password, confirmPassword):
    if len(password) < 6 and password != confirmPassword:
        return ' -- Senha Inválida, digite uma senha com no mínimo 6 letras'
    else:
        return ''


def check_password(password, confirmPassword):
    if password != confirmPassword:
        return ' -- Senha inválida! Senhas de cadastros diferentes'
    else:
        return ''


def check_current_password(user, currentPassword):

    if not user.check_password(currentPassword):
        return ' -- Campo de Senha atual diferente da Senha Atual!'
    else:
        return ''


def fullValidation(form):
    first_name = form.get('first_name')
    last_name = form.get('last_name')
    email = form.get('email')
    original_email = form.get('original_email')

    resultCheck = ''
    resultCheck += check_name(first_name, last_name)
    resultCheck += check_email(email)
    resultCheck += check_email_exist(email, original_email)

    return resultCheck


def fullValidationRegister(form, user=None):
    currentPassword = form.get('currentPassword')
    password = form.get('password')
    confirmPassword = form.get('confirmPassword')

    resultCheck = ''
    resultCheck += fullValidation(form)
    if user is not None:
        resultCheck += check_current_password(user, currentPassword)
        resultCheck += check_password_lenght(password, confirmPassword)
        resultCheck += check_password(password, confirmPassword)

    return resultCheck


@login_required
def list_user_edit(request):

    return __list__(request, 'users/list_user_edit.html')


@login_required
def list_user_delete(request):

    return __list__(request, 'users/list_user_delete.html')


def check_permissions(user):

    has_report_permission = 'checked' if user. \
        has_perm('report.can_generate') else ''
    has_transductor_permission = 'checked' if user. \
        has_perm('transductor.can_view_transductors') else ''
    has_edit_user_permission = 'checked' if user. \
        has_perm('users.can_edit_user') else ''
    has_delete_user_permission = 'checked' if user. \
        has_perm('users.can_delete_user') else ''
    has_see_logging_permission = 'checked' if user. \
        has_perm('users.can_see_logging') else ''

    context = {
        'user': user,
        "can_generate": has_report_permission,
        "view_transductors": has_transductor_permission,
        "edit_users": has_edit_user_permission,
        "delete_users": has_delete_user_permission,
        "see_logging": has_see_logging_permission,
    }

    return context


@login_required
def self_edit_user(request):

    user = User.objects.get(pk=request.user.id)
    print(user)

    if request.method == "GET":
        return render(request, 'users/self_edit.html',)

    else:
        form = request.POST
        first_name = form.get('first_name')
        last_name = form.get('last_name')
        # email = form.get('email')
        email = request.user.username
        password = form.get('password')
        currentPassword = form.get('currentPassword')
        print(currentPassword)

        resultCheck = fullValidationRegister(form, user)

        if len(resultCheck) != 0:
            return __prepare_error_render_self__(request, resultCheck, user)

        user.first_name = first_name
        user.last_name = last_name
        user.username = email
        user.email = email
        user.set_password(password)

        user.save()

        # login(request,user)
        update_session_auth_hash(request, user)

        logger = logging.getLogger(__name__)
        logger.info(request.user.__str__() + ' edited ' + user.__str__())

        return render(request, 'users/dashboard.html')


@login_required
def edit_user(request, user_id):

    user = User.objects.get(id=user_id)

    if request.method == "GET":
        context = check_permissions(user)
        return render(request, 'users/edit_user.html', context)

    else:
        form = request.POST
        first_name = form.get('first_name')
        last_name = form.get('last_name')
        email = form.get('email')

        resultCheck = fullValidation(form)

        if len(resultCheck) != 0:
            return __prepare_error_render__(request, resultCheck, user)

        user.first_name = first_name
        user.last_name = last_name
        user.username = email
        user.email = email

        give_permission(request, user)

        context = check_permissions(user)
        logger = logging.getLogger(__name__)
        logger.info(request.user.__str__() + ' edited ' + user.__str__())
        context['info'] = 'usuario modificado com sucesso'

        return render(request, 'users/edit_user.html', context)


def give_permission(request, user):

    report_checkbox = request.POST.get('can_generate')
    transductor_checkbox = request.POST.get('view_transductors')
    useredit_checkbox = request.POST.get('edit_users')
    userdelete_checkbox = request.POST.get('delete_users')
    seelogging_checkbox = request.POST.get('seelogging_checkbox')

    user.user_permissions.clear()

    __permision__(report_checkbox, 'can_generate', user)
    __permision__(transductor_checkbox, 'can_view_transductors', user)
    __permision__(useredit_checkbox, 'can_edit_user', user)
    __permision__(userdelete_checkbox, 'can_delete_user', user)
    __permision__(seelogging_checkbox, 'can_see_logging', user)

    user.save()


@login_required
def delete_user(request, user_id):

    user = User.objects.get(id=user_id)
    if request.method == "GET":
        return render(request, 'users/delete_user.html', {'user': user})
    else:

        logger = logging.getLogger(__name__)
        logger.info(request.user.__str__() + ' deleted  ' + user.__str__())
        user.delete()
    return render(request, 'users/dashboard.html',
                  {'info': 'usuario deletado com sucesso'})


@login_required
def logging_list(request):
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file = open(BASE_DIR + '/SME_UnB/logging.logging', 'r')
    file_contentes = file.read()

    return render(request, 'users/logging_list.html',
                  {'logging': file_contentes})


def __list__(request, template):

    users = User.objects.all()

    return render(request, template, {'users': users})


def __prepare_error_render__(request, fail_message, user):

    return render(request, 'users/edit_user.html',
                  {'falha': fail_message, 'user': user})


def __prepare_error_render_self__(request, fail_message, user):

    return render(request, 'users/self_edit.html',
                  {'falha': fail_message, 'user': user})


def __permision__(permision_type, codename, user):

    if permision_type == 'on':
        permision = Permission.objects.get(codename=codename)
        user.user_permissions.add(permision)
