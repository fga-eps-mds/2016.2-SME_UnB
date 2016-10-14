"""Directly data manager,logic appliations so as to theirs rules"""
from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.base_user import BaseUserManager
import pusher


class EmailUserManager(BaseUserManager):
    pass

class UserPermissions(models.Model):

    class Meta:
        permissions = (
            ("can_delete_user", "Can delete Users"),
            ("can_edit_user", "Can edit Users"),
        )


class UserNotification(object):
    APP_ID = '259103'
    APP_KEY = '01346f7690ac693e7adb'
    APP_SECRET = '20bf35aeec654118b90c'
    NOTIFICATION_PREFIX = 'notification_'
    CREATE_EVENT = 'create'

    @classmethod
    def send_notification(self, id, message):
        pusher_client = pusher.Pusher(
          app_id=APP_ID,
          key=APP_KEY,
          secret=APP_SECRET,
          ssl=True
        )
        pusher_client.trigger(NOTIFICATION_PREFIX + str(id), CREATE_EVENT, message)
