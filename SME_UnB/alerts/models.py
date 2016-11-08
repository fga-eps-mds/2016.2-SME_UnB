from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from enum import Enum
import pusher
from django.core import serializers
from datetime import datetime
from django.core.mail import send_mail
from django.conf import settings

# Create your models here.


class Alert(models.Model):
    status = models.BooleanField()
    description = models.CharField(max_length=50)
    creation_date = models.DateTimeField(default=datetime.now())
    local = models.CharField(max_length=50)
    priority = models.IntegerField()
    user = models.ForeignKey(User)

    class Meta:
        permissions = (
            ("can_check_alerts", "Can Check Alerts"),
        )


class UserNotification(object):

    @staticmethod
    def send_notification(id_user, message, local, priority):
        APP_ID = '259103'
        APP_KEY = '01346f7690ac693e7adb'
        APP_SECRET = '20bf35aeec654118b90c'
        NOTIFICATION_PREFIX = 'notification_'
        CREATE_EVENT = 'create'

        alertJson = UserNotification.__create_alert__(id_user,
                                                      message,
                                                      local, priority)

        pusher_client = pusher.Pusher(app_id=APP_ID,
                                      key=APP_KEY,
                                      secret=APP_SECRET,
                                      ssl=True)

        pusher_client.trigger(NOTIFICATION_PREFIX + str(id_user),
                              CREATE_EVENT,
                              alertJson)

    @staticmethod
    def __create_alert__(id_user, message, local, priority):
        user = User.objects.get(id=id_user)

        alert = Alert(user=user,
                      status=False,
                      description=message,
                      local=local,
                      priority=priority)

        alertJson = serializers.serialize('json', [alert, ])

        if priority == 4:
            print "chegou"
            send_mail('Subject here',
                      'Here is the message.',
                      settings.EMAIL_HOST_USER,
                      [user.email],
                      fail_silently=False)

            alert.save()

        return alertJson


class PriorityOfNotification(Enum):
    DANGEROUS = 4
    HIGH = 3
    MEDIUM = 2
    LOW = 1
