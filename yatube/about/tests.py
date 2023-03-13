from django.test import Client, TestCase
from http import HTTPStatus


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_status_code_about_app(self):
        """Проверка доступности адресов 'about/tech/', 'about/author/'."""
        urls = ['/about/author/', '/about/tech/']
        for url in urls:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_uses_correct_template_guest_client(self):
        """URL-адрес использует соответствующий шаблон,
        если пользователь = гость"""
        url_names = {'/about/author/': 'about/author.html',
                     '/about/tech/': 'about/tech.html'}
        for url, template in url_names.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertTemplateUsed(response, template)
