from django.test import Client, TestCase
from django.urls import reverse
from ..models import Post, Group, User


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
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.form_data = {'text': 'Текстовый пост из формы',
                          'group': PostFormTests.group.id
                          }

    def test_form_create_post(self):
        post_count = Post.objects.count()
        response = self.authorized_client.post(
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
        self.assertRedirects(response, reverse(
            'posts:profile', args=[PostFormTests.user.username]))

    def test_form_edit_post(self):
        self.authorized_client.post(
            reverse('posts:post_edit', args=[PostFormTests.post.id]),
            data=self.form_data)
        response = self.authorized_client.get(
            reverse('posts:post_detail', args=[PostFormTests.post.id]))
        self.assertEqual(response.context['post'].text, self.form_data['text'])
        self.form_data['text'] = 'Это новый текст'
        self.authorized_client.post(
            reverse('posts:post_edit', args=[PostFormTests.post.id]),
            data=(self.form_data))
        self.assertTrue(Post.objects.filter(
            text='Это новый текст',
            group=self.group.id,
            pk=self.post.pk).exists())
