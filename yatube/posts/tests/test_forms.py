from django.test import Client, TestCase
from django.urls import reverse
from ..models import Post, Group, User
from http import HTTPStatus


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Test')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост - пишем тест',
            group=cls.group
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.form_data = {'text': 'Текстовый пост из формы',
                          'group': PostFormTests.group.id
                          }

    def test_form_create_post(self):
        """Тест создания новой записи в бд """
        post_count = Post.objects.count()
        self.authorized_client.post(
            reverse('posts:post_create'),
            data=self.form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertTrue(Post.objects.filter(
            text='Текстовый пост из формы',
            group=self.group.id,
            pk=post_count + 1
        ).exists())

    def test_form_edit_post(self):
        """Тест изменений записи в бд при редактировании поста"""
        self.authorized_client.post(
            reverse('posts:post_edit', args=[PostFormTests.post.id]),
            data=self.form_data)
        self.form_data['text'] = 'Это новый текст'
        self.authorized_client.post(
            reverse('posts:post_edit', args=[PostFormTests.post.id]),
            data=(self.form_data))
        self.assertTrue(Post.objects.filter(
            text='Это новый текст',
            group=self.group.id,
            pk=self.post.pk).exists())

    def test_guest_can_not_move_to_creat_post_page(self):
        """Неавторизованный пользователь не может перейти на на страницу
        создания поста /create"""
        response = self.guest_client.post(
            reverse('posts:post_create'),
        )
        self.assertNotEqual(response.status_code, HTTPStatus.OK)

    def test_urls_correct_status_code(self):
        """Неавторизованного пользователя перенаправляет со страниц
        /create,posts/<int:post_id>/edit/ на страницу auth/login"""
        url_names = (
            ('/create/'),
            (f'/posts/{PostFormTests.post.id}/edit/'))
        for url in url_names:
            with self.subTest(url=url):
                login_url = reverse('login')
                target_url = f'{login_url}?next={url}'
                response = self.guest_client.get(url)
                self.assertRedirects(response, target_url)
