from django.test import TestCase
from ..models import Group, Post, Comment, Follow, User


class PostModelTest(TestCase):
    @classmethod
    def setUp(self):
        self.user = User.objects.create_user(username='auth')
        self.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        self.post = Post.objects.create(
            author=self.user,
            text='Тестовый пост - Постовый тест',
        )
        self.comment = Comment.objects.create(
            post=self.post,
            text='Тестовый коментарий',
            author=self.user
        )
        self.follow = Follow.objects.create(
            user=User.objects.create_user(username='Test'),
            author=self.post.author
        )

    def test_models_have_correct__str__(self):
        """Проверяем, что у моделей корректно работает __str__."""
        str__models = [
            (self.post.text[:15], str(self.post)),
            (self.group.title, str(self.group.title)),
            (self.comment.text[:15], str(self.comment)),
            ((f'{self.follow.user}, {self.follow.author.username}'),
             str(self.follow))]
        for str__model, expected in str__models:
            with self.subTest():
                self.assertEqual(expected, str__model)
