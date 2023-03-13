from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from http import HTTPStatus

from django.urls import reverse
from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Testname')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='testovyi-slag',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост - Постовый тест',
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.author_post_client = Client()
        self.author_post_client.force_login(PostModelTest.post.author)

    def test_urls_correct_status_code(self):
        """
        Проверка доступности url адресов:
        '/',
        'group/<slug:slug>/',
        'profile/<str:username>/',
        'posts/<int:post_id>/',
        'create/',
        'posts/<int:post_id>/edit/'
        """
        url_names = (
            ('/'),
            (f'/group/{PostModelTest.group.slug}/'),
            (f'/profile/{PostModelTest.user.username}/'),
            (f'/posts/{PostModelTest.post.id}/'),
            ('/create/'),
            (f'/posts/{PostModelTest.post.id}/edit/'))
        for url in url_names:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_uses_correct_template_guest_client(self):
        """URL-адрес использует соответствующий шаблон,
        если пользователь = гость"""
        url_names = {
            '/': 'posts/index.html',
            f'/group/{PostModelTest.group.slug}/': 'posts/group_list.html',
            f'/profile/{PostModelTest.user.username}/': 'posts/profile.html',
            f'/posts/{PostModelTest.post.id}/': 'posts/post_detail.html'}
        for url, template in url_names.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_urls_uses_correct_template_authorized_client(self):
        """URL-адрес использует соответствующий шаблон,
        если пользователь авторизован."""
        url_names = {
            '/create/': 'posts/create_post.html',
            f'/posts/{PostModelTest.post.id}/edit/': 'posts/create_post.html'}
        for url, template in url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_correct_response_unexisting_page_templ(self):
        """Проверка ответа для не существующей страницы."""
        response = self.authorized_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_post_edit_url_available_to_the_author(self):
        """Страница '/posts/<int:post_id>/edit/'доступна автору."""
        if self.user == self.post.author:
            response = self.authorized_client.get(
                f'/posts/{PostModelTest.post.id}/edit/')
            self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_correct_status_code(self):
        """Проверка недоступности url адресов для неавторизованноого
        пользователя: 'create/', 'posts/<int:post_id>/edit/'"""
        url_names = (
            ('/create/'),
            (f'/posts/{PostModelTest.post.id}/edit/'))
        for url in url_names:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_urls_correct_status_code(self):
        """Неавторизованного пользователя перенаправляет со страниц
        /create,posts/<int:post_id>/edit/ на страницу auth/login"""
        url_names = (
            ('/create/'),
            (f'/posts/{PostModelTest.post.id}/edit/'))
        for url in url_names:
            with self.subTest(url=url):
                login_url = reverse('login')
                target_url = f'{login_url}?next={url}'
                response = self.guest_client.get(url)
                self.assertRedirects(response, target_url)
