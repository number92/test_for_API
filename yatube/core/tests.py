from django.test import TestCase
from django.test import Client


class TemplatesErrorTest(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_404_error_page(self):
        """Проверка доступности шаблона для ошибки 404"""
        response = self.guest_client.get('/nonexist-page/')
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, 'core/404.html')
