from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from http import HTTPStatus
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

    def test_correct_response_index_templ(self):
        """Проверка доступности адреса '/'."""
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_correct_response_group_templ(self):
        """Проверка доступности адреса '/group/<slug:slug>/'."""
        response = self.guest_client.get(
            f'/group/{PostModelTest.group.slug}/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_correct_response_profile_templ(self):
        """Проверка доступности адреса '/profile/<str:username>/'."""
        response = self.guest_client.get(
            f'/profile/{PostModelTest.user.username}/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_correct_response_post_detail_templ(self):
        """Проверка доступности адреса 'posts/<int:post_id>/'."""
        response = self.guest_client.get(
            f'/posts/{PostModelTest.post.id}/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_correct_response_post_create_templ(self):
        """Проверка доступности адреса '/create/'."""
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_correct_response_post_edit_templ(self):
        """Проверка доступности адреса 'posts/<int:post_id>/edit/'."""
        response = self.authorized_client.get(
            f'/posts/{PostModelTest.post.id}/edit/')
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
