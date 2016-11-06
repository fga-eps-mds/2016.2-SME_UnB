#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
from django.contrib import messages
from django.db import IntegrityError
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponse
from django.core.mail import send_mail
from django.core import mail
from SME_UnB.settings import EMAIL_HOST_USER
import os

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import json
import logging
import hashlib
import datetime


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
    logger.info(request.user.__str__() + ' Logout ' )
    return logout(request, *args, **kwargs)


@login_required
@user_passes_test(lambda user:user.is_staff, login_url='/accounts/dashboard/')
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

        try:

            user = User.objects.create_user(
                        first_name=first_name, last_name=last_name, password=password, username=email)
        except  IntegrityError as e:
            return render(request, 'userRegister/register.html', {'falha': 'Invalid email, email already exist'})
        except:
            return render(request, 'userRegister/register.html', {'falha': 'Falha de Registro!'})

        give_permission(request, user)
        user.save()
        messages.success(request, 'Usuario registrado com sucesso')

        return HttpResponseRedirect(reverse("users:dashboard"))

        logger = logging.getLogger(__name__)
        logger.info(request.user.__str__() + ' Registered ' + user.__str__() )

	from django.core import mail
	connection = mail.get_connection()

	# Manually open the connection
	connection.open()

	# Construct an email message that uses the connection
	email1 = mail.EmailMessage(
	    'Hello',
	    'Body goes here',
	    'mds@sof2u.com',
	    [email],
	    connection=connection,
	)
	email1.send() # Send the email
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

def check_email_exist(email,original_email):
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

def fullValidation(form):
    first_name = form.get('first_name')
    last_name = form.get('last_name')
    email = form.get('email')
    original_email = form.get('original_email')


    resultCheck = ''
    resultCheck += check_name(first_name, last_name)
    resultCheck += check_email(email)
    resultCheck += check_email_exist(email,original_email)

    return resultCheck

def fullValidationRegister(form):
    password = form.get('password')
    confirmPassword = form.get('confirmPassword')

    resultCheck = ''
    resultCheck += fullValidation(form)
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

    has_report_permission = 'checked' if user.has_perm('report.can_generate') else ''
    has_transductor_permission = 'checked' if user.has_perm('transductor.can_view_transductors') else ''
    has_edit_user_permission = 'checked' if user.has_perm('users.can_edit_user') else ''
    has_delete_user_permission = 'checked' if user.has_perm('users.can_delete_user') else ''
    has_see_logging_permission = 'checked' if user.has_perm('users.can_see_logging') else ''

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

    if request.method == "GET":
        return render(request, 'users/self_edit.html',)

    else:
        form = request.POST
        first_name = form.get('first_name')
        last_name =  form.get('last_name')
        email = form.get('email')
        password = form.get('password')

        resultCheck = fullValidationRegister(form)

        if len(resultCheck) != 0:
            return __prepare_error_render_self__(request, resultCheck, user)

        user.first_name = first_name
        user.last_name = last_name
        user.username = email
        user.email = email
        if password != "":
            user.set_password(password)
        user.save()

        logger = logging.getLogger(__name__)
        logger.info(request.user.__str__() + ' edited '  + user.__str__() )


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
        last_name =  form.get('last_name')
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
        logger.info(request.user.__str__() + ' edited '  + user.__str__() )
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
        logger.info(request.user.__str__() + ' deleted  ' + user.__str__() )
        user.delete()
    return render (request, 'users/dashboard.html', {'info': 'usuario deletado com sucesso'})
@login_required
def logging_list (request):
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file = open (BASE_DIR+'/SME_UnB/logging.logging', 'r')
    file_contentes = file.read()

    return render(request, 'users/logging_list.html',{'logging' : file_contentes})

def __list__(request, template):

    users = User.objects.all()
    return render(request, template, {'users':users})

def __prepare_error_render__(request, fail_message, user):

    return render(request, 'users/edit_user.html', {'falha': fail_message, 'user': user})

def __prepare_error_render_self__(request, fail_message, user):

    return render(request, 'users/self_edit.html', {'falha': fail_message, 'user': user})

def __permision__(permision_type, codename, user):

    if permision_type == 'on':
        permision = Permission.objects.get(codename=codename)
        user.user_permissions.add(permision)

def _generate_token_(user):
    """TODO: Docstring for _genarate_token_.
    :user: is a user witch like changes the password
    :returns: unique token to a user an a day

    """
    username = user.username
    password = user.password
    date = datetime.datetime.now()
    day = str(date.day)

    plain_text = username + password + day
    token = hashlib.sha256(plain_text.encode('utf-8')).hexdigest()

    return token

def forgot_password(request):
    """TODO: Docstring for forgot_password.
    Fixing html email
    Make testes
    make a app


    :request: recive the data with email to send a requesto of a new password
    :returns: render a page with  message to see your email if the emails exists
    and render an error if dont

    """

    def post(request):
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            token = _generate_token_(user)

            # send email
            text_plain = 'http://dustteam.com.br/accounts/reset_password/' + token
            html = """\
            <html>
                <head></head>
                <body>
                    <p><href=%s>Link para recuperar a senha </a>.</p>
                </body>
            <\html>
            """ % text_plain

            email_html = MIMEText(html, 'html')

            connection = mail.get_connection()
            connection.open()
            forgotten_password_mail = mail.EmailMessage(
        	    'Esqueceu sua senha?',
        	    email_html,
        	    'mds@sof2u.com',
        	    [email],
        	    connection=connection,
        	)
            forgotten_password_mail.send()

            context = {
                    'message':"Email enviado com sucesso",
                    'validator':"A recuperação de senha irá expirar após as " + \
                    "24hr do dia de hoje",
                    }

        except User.DoesNotExist as e:
            context = {
                    'message':"Este email não existe ou é invalido",
                    'validate':"Digite novamente"
                    }
        return context

    context_return = {}

    if request.method == "POST":
        context_return = post(request)

        return HttpResponse(
                json.dumps(context_return),
                'application/json'
                )
    else:
        template_name = "users/forgot_password.html"
        return render(request, template_name, context_return)

def confirm_email(request, token):
    """TODO: Docstring for confirm_email.

    :request: TODO
    :token: TODO
    :returns: TODO

    """
    if request.method == "GET":
        return render(request, "users/reset_password.html", {"token":token})
    else:
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            token = _generate_token_(user)
            if token == request.POST.get('token'):
                context = {
                        "message" : "O link está correto",
                        "is_valid": "yes",
                        "email": email,
                        }
            else:
                context = {
                        "message" : "Link Expirado!!",
                        "is_valid": "no",
                        }

        except User.DoesNotExist as email_error:
            context = {
                    'message':"Email inválido",
                    'is_valid':"no"
                    }

        return HttpResponse(
                json.dumps(context),
                'application/json'
                )

def reset_password(request):
    """TODO: Docstring for reset_password.
    :returns: TODO

    """
    if request.method == "POST":
        password = request.POST.get("pass")
        confirm_pass = request.POST.get("confirm_pass")
        email = request.POST.get("email")

        if password ==  confirm_pass:
            user = User.objects.get(email=email)
            user.set_password(password)
            user.save()
            message = "Senha alterada com sucesso"
            is_valid = "yes"
        else:
            message = "as senhas são diferentes"
            is_valid = "no"

        context = {
                "message": message,
                "is_valid": is_valid,
                }

        return HttpResponse(
                json.dumps(context),
                'application/json'
                )
