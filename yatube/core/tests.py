from django.test import TestCase
from django.test import Client


class TemplatesErrorTest(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_404_error_page(self):
        response = self.guest_client.get('/nonexist-page/')
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response.templates, 'core/404.html')
