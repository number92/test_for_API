from django.test import Client, TestCase
from http import HTTPStatus


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_correct_response_about_author_templ(self):
        """Проверка доступности адреса 'about/author/'."""
        response = self.guest_client.get('/about/author/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_correct_response_about_tech_templ(self):
        """Проверка доступности адреса 'about/tech/'."""
        response = self.guest_client.get('/about/tech/')
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
