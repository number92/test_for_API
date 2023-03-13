from django.test import TestCase
from ..models import Group, Post, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост - Постовый тест',
        )

    def test_models_have_correct__str__(self):
        """Проверяем, что у модели Post , Group корректно работает __str__."""
        str__models = {PostModelTest.post.text[:15]: str(PostModelTest.post),
                       PostModelTest.group.title: str(PostModelTest.group)}
        for str__model, expected in str__models.items():
            with self.subTest(str__model=str__model, expected=expected):
                self.assertEqual(expected, str__model)
