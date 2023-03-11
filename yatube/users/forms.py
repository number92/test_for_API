from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

User = get_user_model()


class CreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('first_name', 'last_name', 'username', 'email')
        labels = {
            'first_name': 'Имя',
            'last_name': 'Фамилия',
            'username': 'Пользователь',
            'email': 'Электронный адрес'}
        help_texts = {
            'first_name': 'Введите имя',
            'last_name': 'Введите фамилию',
            'username': 'Введите имя пользователя',
            'email': 'Введите электронный адрес'}
