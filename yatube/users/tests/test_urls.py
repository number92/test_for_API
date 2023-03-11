from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from http import HTTPStatus

User = get_user_model()


class UsersUrlTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Testname')

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_correct_response_signup_templ(self):
        """Проверка доступности адреса '/auth/signup/'."""
        response = self.guest_client.get('/auth/signup/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_status_code_ok(self):
        """Проверка доступности URL-адресов"""
        url_names = ['/auth/signup/', '/auth/login/', '/auth/reset/done/',
                     '/auth/password_reset/', '/auth/password_reset/done/',
                     '/auth/reset/<uidb64>/<token>/',
                     '/auth/password_change/done/', '/auth/password_change/',
                     '/auth/logout/']
        for url in url_names:
            response = self.authorized_client.get(url)
            if response.status_code != 200:
                print(url, response.status_code)
            self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_uses_correct_template_authorized_client(self):
        """URL-адрес использует соответствующий шаблон,
        если пользователь авторизован."""
        urls = {
            '/auth/signup/': 'users/signup.html',
            '/auth/login/': 'users/login.html',
            '/auth/reset/done/': 'users/password_reset_complete.html',
            '/auth/password_reset/done/': 'users/password_reset_done.html',
            '/auth/password_reset/': 'users/password_reset_form.html',
            '/auth/password_change/done/': 'users/password_change_done.html',
            '/auth/password_change/': 'users/password_change_form.html',
            '/auth/logout/': 'users/logged_out.html'}
        for url, template in urls.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_correct_response_unexisting_page_templ(self):
        """Проверка ответа для не существующей страницы."""
        response = self.authorized_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
