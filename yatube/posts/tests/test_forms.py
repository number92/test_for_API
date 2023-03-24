import tempfile
import shutil

from django.test import Client, TestCase, override_settings
from django.urls import reverse
from ..models import Post, Group, Comment, User
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
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

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        self.user = PostFormTests.user
        self.author = self.user
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_form_create_post(self):
        """Тест создания новой записи в бд """
        uploaded_test = SimpleUploadedFile(
            name='test_small.gif',
            content=self.small_gif,
            content_type='image/gif'
        )
        post_count = Post.objects.count()
        reverse('posts:profile', args=[self.author])
        form_data = {'text': 'Текстовый пост из формы',
                     'group': self.group.id,
                     'image': uploaded_test,
                     }
        self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True)
        self.assertEqual(
            Post.objects.count(), post_count + 1, 'Запись в базе не создана')
        self.assertEqual(
            Post.objects.last().image.name, 'posts/test_small.gif')

    def test_form_edit_post(self):
        """Тест изменений записи в бд при редактировании поста"""
        post_count = Post.objects.count()
        post = Post.objects.create(
            author=self.user,
            text='Тестовый пост',
            group=self.group,
        )
        uploaded_edit = SimpleUploadedFile(
            name='test_edit.gif',
            content=self.small_gif,
            content_type='image/gif')
        post_detail_redirect = reverse(
            'posts:post_detail', args=[post.id])
        form_data = {'text': 'Новый текст',
                     'group': self.group.id,
                     'image': uploaded_edit,
                     }
        response = self.authorized_client.post(
            reverse('posts:post_edit', args=[post.id]),
            data=form_data)
        self.assertEqual(Post.objects.last().text, 'Новый текст')
        self.assertRedirects(response, post_detail_redirect)
        self.assertEqual(
            Post.objects.count(), post_count + 1, 'Запись в базе не создана')
        self.assertEqual(
            Post.objects.last().image.name, 'posts/test_edit.gif')

    def test_add_comment_and_save_to_database(self):
        """Добавление комментария и сохранение в БД"""
        post = Post.objects.create(
            author=self.user,
            text='Тестовый пост',
            group=self.group,
        )
        comment_count = Comment.objects.count()
        form_data = {'text': 'Newcomment'}
        self.authorized_client.post(reverse(
            'posts:add_comment', kwargs={'post_id': post.id}),
            data=form_data,
            follow=True)
        self.assertEqual(Comment.objects.count(), comment_count + 1)

    # проверка добавления коментария не авторизов. польз. находится в test_urls
    # проверка создания поста не авторизов. польз. находится в test_views
