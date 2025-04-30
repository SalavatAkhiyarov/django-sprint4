from django import forms
from django.contrib.auth import get_user_model

from .models import Post, Comments

User = get_user_model()


class CreatePost(forms.ModelForm):
    class Meta:
        model = Post
        exclude = ('author', 'created_at')
        widgets = {'pub_date': forms.DateTimeInput(attrs={'type': 'datetime-local'})}


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email')


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comments
        fields = ('text',)
