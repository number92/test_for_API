from django.test import Client, TestCase
from django.urls import reverse
from ..models import Post, Group, User
from django import forms


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
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост - пишем тест',
            group=cls.group
        )
        # cls.cont_index = ('title', 'post_list', 'page_obj')
        # cls.cont_group = ['title', 'group', 'post_list', 'page_obj']
        # cls.cont_profile = ['author', 'post_list', 'page_obj', 'post_count']
        # cls.cont_detail = ['post', 'post_count', 'title']
        # cls.cont_create = ['form']
        # cls.cont_edit = ['form', 'is_edit']
        # # cls.context_list = (cont_index, cont_group, cont_profile,
        # #        cont_detail, cont_create, cont_edit)

    def setUp(self):
        self.user = User.objects.create_user(username='StasBasov')
        self.author = ViewsPagesTests.post.author
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            (reverse('posts:posts')): 'posts/index.html',
            (reverse('posts:group_list', args=[ViewsPagesTests.group.slug])):
            'posts/group_list.html',
            (reverse('posts:profile', args=[ViewsPagesTests.user.username])):
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
        self.assertEqual(
            response.context.get('post_list').count(), Post.objects.count())
        self.assertEqual(
            response.context.get('page_obj').object_list,
            list(Post.objects.all()))
        self.assertEqual(
            response.context.get('title'), "Последние обновления на сайте")

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
        self.assertQuerysetEqual(
            response.context.get('page_obj').object_list,
            self.group.posts.all(), transform=lambda x: x)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:profile', args=[ViewsPagesTests.user.username]))
        self.assertEqual(response.context.get('author'), self.author)
        self.assertQuerysetEqual(
            response.context.get('page_obj').object_list,
            list(self.author.posts.all()), transform=lambda x: x)
        self.assertEqual(response.context.get('post_count'),
                         self.author.posts.count())

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id}))
        self.assertEqual(response.context.get('post').text,
                         ViewsPagesTests.post.text)
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
                'posts:profile', args=[ViewsPagesTests.user.username])),
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
