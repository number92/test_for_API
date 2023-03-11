from django import forms
from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ("text", "group")
        labels = {"text": "Коментарий",
                  "group": "Группа"}
        help_texts = {"text": "Ваш коментарий",
                      "group": "Выберите группу"}

    def clean_text(self):
        data = self.cleaned_data["text"]
        if not data.strip():
            raise forms.ValidationError('Вы не можете отправить пустой пост')
        return data
