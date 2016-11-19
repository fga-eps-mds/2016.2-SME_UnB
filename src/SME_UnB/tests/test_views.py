from django.test import TestCase


class SMETest(TestCase):
    def test_index_page(self):
        response = self.client.get('')

        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, 'index.html')
