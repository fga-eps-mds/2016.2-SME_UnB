"""Directly data manager,logic appliations so as to theirs rules"""
from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.base_user import BaseUserManager


class EmailUserManager(BaseUserManager):
    pass

class UserPermissions(models.Model):
    
    class Meta:
        permissions = (
            ("can_delete_user", "Can delete Users"),
            ("can_edit_user", "Can edit Users"),
        )
