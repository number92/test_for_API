import tempfile
import shutil
from django.core.cache import cache
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from ..models import Post, Group, Comment, Follow, User
from django import forms
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from http import HTTPStatus

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class ViewsPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Test')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост - пишем тест',
            group=cls.group,
            image=cls.uploaded
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        cache.clear()
        self.user = ViewsPagesTests.user
        self.author = self.user
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            (reverse('posts:posts')): 'posts/index.html',
            (reverse('posts:group_list', args=[ViewsPagesTests.group.slug])):
            'posts/group_list.html',
            (reverse('posts:profile', args=[self.user.username])):
            'posts/profile.html',
            (reverse('posts:post_detail', args=[ViewsPagesTests.post.pk])):
            'posts/post_detail.html',
            (reverse('posts:post_create')): 'posts/create_post.html',
            (reverse('posts:post_edit', args=[ViewsPagesTests.post.id])):
            'posts/create_post.html'
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:posts'))
        post = response.context['page_obj'][0]
        context_index = {
            response.context.get('post_list').count(): Post.objects.count(),
            response.context.get('page_obj').number: 1,
            post.image: ViewsPagesTests.post.image,
            response.context.get('title'): "Последние обновления на сайте",
        }
        for context, expected in context_index.items():
            with self.subTest(context=context, expected=expected):
                self.assertEqual(context, expected)

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:group_list', args=[self.post.group.slug]))
        self.assertEqual(
            response.context.get('title'),
            f"Записи сообщества {ViewsPagesTests.group.slug}")
        self.assertEqual(response.context.get('group'), ViewsPagesTests.group)
        self.assertEqual(
            response.context.get('post_list').count(), Group.objects.count())
        post = response.context['post_list'][0]
        self.assertEqual(post.image, ViewsPagesTests.post.image)
        self.assertQuerysetEqual(
            response.context.get('page_obj').object_list,
            self.group.posts.all(), transform=lambda x: x)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:profile', args=[self.user.username]))
        self.assertEqual(response.context.get('author'), self.author)
        self.assertQuerysetEqual(
            response.context.get('page_obj').object_list,
            list(self.author.posts.all()), transform=lambda x: x)
        post = response.context['page_obj'][0]
        self.assertEqual(post.image, ViewsPagesTests.post.image)
        self.assertEqual(response.context.get('post_count'),
                         self.author.posts.count())

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        Comment.objects.create(
            post=self.post,
            text='Тестовый коментарий',
            author=self.user)
        comments_count = Comment.objects.count()
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id}))
        self.assertEqual(len(
            response.context.get('post_comments')), comments_count)
        self.assertEqual(response.context.get('form').fields['text'].label,
                         'Текст коментария')
        post = response.context.get('post')
        self.assertEqual(post.text, ViewsPagesTests.post.text)
        self.assertEqual(post.image, ViewsPagesTests.post.image)
        self.assertEqual(response.context.get('post_count'),
                         self.author.posts.count())
        self.assertEqual(
            response.context.get('title'),
            f'Пост {self.post.text[:30]}')

    def test_create_post_page_show_correct_context(self):
        """Шаблон create_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_create'))
        form_fields = {
            'group': forms.fields.ChoiceField,
            'text': forms.fields.CharField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_page_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_edit', args=[ViewsPagesTests.post.id]))
        self.assertEqual(response.context.get('form').instance.id,
                         ViewsPagesTests.post.id)
        self.assertTrue(response.context.get('is_edit'), {'is_edit': True})

    def test_post_exists_on_pages(self):
        """При создании поста с группой, он появляется на страницах:
        index, group_list, profile"""
        reverse_name = {
            'index': self.authorized_client.get(reverse('posts:posts')),
            'group_list': self.authorized_client.get(reverse(
                'posts:group_list', args=[self.post.group.slug])),
            'profile': self.authorized_client.get(reverse(
                'posts:profile', args=[self.user.username])),
        }
        for name in reverse_name:
            with self.subTest(name=name):
                post_count = Post.objects.count()
                self.assertEqual(Post.objects.count(), (post_count))
                Post.objects.create(
                    author=self.user,
                    text=f'Этот пост отображается на странице {name}',
                    group=ViewsPagesTests.group)
                expected = (post_count + 1)
                self.assertEqual(Post.objects.count(), expected)

    def test_post_exists_another_group_page(self):
        """Пост не попал в группу, для которой не был предназначен"""
        Group.objects.create(
            title='Другая тест-группа',
            slug='another-test-slug',
            description='Тестовое 1111'
        )
        response = self.authorized_client.get(reverse(
            'posts:group_list', args=['another-test-slug']))
        count_post = len(response.context.get('post_list'))
        self.assertEqual(count_post, 0)
        self.assertEqual(Post.objects.count(), 1)

    def test_guest_can_not_move_to_creat_post_page(self):
        """Неавторизованный пользователь не может перейти на на страницу
        создания поста /create"""
        response = self.guest_client.post(
            reverse('posts:post_create'),
        )
        self.assertNotEqual(response.status_code, HTTPStatus.OK)

    def test_redirect_guest_user(self):
        """Неавторизованного пользователя перенаправляет со страниц
        /create/, posts/<int:post_id>/edit/ на страницу auth/login"""
        post = Post.objects.create(
            author=self.user,
            text='Тестовый пост',
            group=self.group,
        )
        url_names = (
            ('/create/'),
            (f'/posts/{post.id}/edit/'))
        for url in url_names:
            with self.subTest(url=url):
                login_url = reverse('login')
                target_url = f'{login_url}?next={url}'
                response = self.guest_client.get(url)
                self.assertRedirects(response, target_url)

    def test_cache_working_in_index_page(self):
        """Проверяет работу кэша на главной странице"""
        Post.objects.create(
            author=self.user,
            text='Пост для кэша',
            group=self.group,
        )
        self.guest_client.get(reverse('posts:posts'))
        Post.objects.first().delete()
        self.assertContains(self.guest_client.get(reverse('posts:posts')),
                            'Пост для кэша', status_code=200)
        cache.clear()
        self.assertNotContains(self.guest_client.get(reverse('posts:posts')),
                               'Пост для кэша')

    def test_user_follow(self):
        """Авторизованный пользователь может подписываться на
          других пользователей"""
        followoer_user = User.objects.create_user(username='Follower')
        self.authorized_client.force_login(followoer_user)
        self.authorized_client.get(reverse('posts:profile_follow',
                                           args=[self.post.author.username]))
        self.assertEqual(Follow.objects.count(), 1)

    def test_user_unfollow(self):
        """Авторизованный пользователь может отписываться от
          других пользователей"""
        Follow.objects.create(
            user=self.user,
            author=ViewsPagesTests.post.author)
        self.authorized_client.get(reverse('posts:profile_unfollow',
                                           args=[self.user.username]))
        self.assertEqual(Follow.objects.count(), 0)

    def test_new_post_is_visible_to_subscribers(self):
        """Новая запись видна в ленте у подписчиков"""
        Post.objects.create(
            author=self.user,
            text='Подписка'
        )
        Follow.objects.create(
            user=self.user,
            author=self.post.author)
        response = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertIn(self.post, response.context['page_obj'])

    def test_new_post_is_visible_to_unsubscribers(self):
        """Новая запись не видна в ленте у тех кто не подписан"""
        Post.objects.create(
            author=self.user,
            text='Подписка'
        )
        response = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertNotIn(self.post, response.context['page_obj'])


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Test')
        cls.auth_user = User.objects.create_user(username='auth_user_Test')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.bulk_create(
            [
                Post(
                    author=cls.user,
                    text=f'Тестовый пост - {i}',
                    group=cls.group,)
                for i in range(13)
            ]
        )

    def test_first_page_contains_ten_records(self):
        """ Проверка: количество постов на 'posts:posts', 'posts:group_list',
        'posts:profile' на первой странице равно 10."""
        urls = (
            reverse('posts:posts'),
            reverse('posts:group_list', kwargs={'slug': self.group.slug}),
            reverse('posts:profile', kwargs={'username': self.user.username})
        )
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(len(
                response.context.get('page_obj').object_list), 10)

    def test_second_page_contains_three_records(self):
        """ Проверка: на второй странице должно быть три поста."""
        urls = (
            reverse('posts:posts') + '?page=2',
            reverse('posts:group_list',
                    kwargs={'slug': self.group.slug}) + '?page=2',
            reverse('posts:profile',
                    kwargs={'username': self.user.username}) + '?page=2',
        )
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(
                len(response.context.get('page_obj').object_list), 3)
