from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext as _
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin

class EmailUserManager(BaseUserManager):
    pass

class UserPermissions(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    can_acess_graphics = models. BooleanField()
    can_acess_report = models. BooleanField()
