from django.test import TestCase
from django.test import Client
from django.contrib.auth.models import User, Permission
from mock import Mock, MagicMock, patch
from django.core.mail import send_mail
from alerts.models import *

import unittest

class TestAlertEmail(unittest.TestCase):
    def setUp(self):
        self.user = User.objects.get_or_create(
            username='testuser',
            email='teste@email.com'
        )

    @patch('django.contrib.auth.models.User')
    def test_sending_email_when_criticaly_notified(self, user_class_mock):
        send_mail = Mock()
        Alert = Mock()
        UserNotification.send_notification(1, "Critical Alert", "local_test", 4)
        self.assertEqual(send_mail.called, True)
