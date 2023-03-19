from django import forms
from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ("text", "group", 'image',)

    def clean_text(self):
        data = self.cleaned_data["text"]
        if not data.strip():
            raise forms.ValidationError('Вы не можете отправить пустой пост')
        return data


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)

    def clean_text(self):
        data = self.cleaned_data["text"]
        if not data.strip():
            raise forms.ValidationError('Вы не можете отправить пустой пост')
        return data
