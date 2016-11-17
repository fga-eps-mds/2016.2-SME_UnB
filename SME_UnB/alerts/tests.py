from django.contrib.auth.models import User
from mock import Mock, patch

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
        UserNotification.send_notification(1,
                                           "Critical Alert",
                                           "local_test", 4)
        self.assertEqual(send_mail.called, True)
