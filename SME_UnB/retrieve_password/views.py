#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
import os

from django.http import JsonResponse
import json
import logging
import hashlib
import datetime

def _generate_token_(user):
    """
    _genarate_token_ : Takes a serie of arguments and generate a hash with them
    :user: is a user witch like changes the password
    :returns: unique hash token with username, password, date.day
    """

    username = user.username
    password = user.password
    date = datetime.datetime.now()
    day = str(date.day)

    plain_text = username + password + day
    token = hashlib.sha256(plain_text.encode('utf-8')).hexdigest()

    return token

def forgot_password(request):
    """
    forgot_password :
    :request: recive the data with email to send a requesto of a new password
    :returns: render a page with  message to see your email if the emails exists
    and render an error if dont
    """

    def post(request):
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            token = _generate_token_(user)
            print(token)
            # send email
            password_change_message = "A password reset has been requested for\
            the SME_UnB username: " + user.username + "\n\nIf you did not make\
            this request, it is safe to ignore this email.\n\nIf you do\
            actualy want to reset your password, please visit this link: \n\n"

            link_plain = 'localhost:3000/retrieve_password/reset/' + token

            connection = mail.get_connection()
            connection.open()
            forgotten_password_mail = mail.EmailMessage(
        	    'Esqueceu sua senha?',
        	    password_change_message + link_plain,
        	    'mds@sof2u.com',
        	    [email],
        	    connection=connection,
        	)
            forgotten_password_mail.send()

            context = {
                    'message':"Email enviado com sucesso",
                    'validate':"A recuperação de senha irá expirar após as " + \
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
        template_name = "retrieve_password/forgot_password.html"
        return render(request, template_name, context_return)

def confirm_email(request, token):
    """TODO: Docstring for confirm_email.
    :request: TODO
    :token: TODO
    :returns: TODO

    """
    if request.method == "GET":
        return render(request, "retrieve_password/reset_password.html", \
        {"token":token})
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
        print(password + "\n" + confirm_pass)
        password = request.POST.get("inputPassword")
        confirm_pass = request.POST.get("confirmPassword")
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
