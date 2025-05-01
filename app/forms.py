import random

import django.forms as forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field
from crispy_forms.layout import Submit

from django.contrib.auth.models import User

from app.models import Profile, Tag, Question, Answer


class LoginForm(forms.Form):
    login = forms.CharField(required=False, label='Login')
    password = forms.CharField(widget=forms.PasswordInput, required=False, label='Password')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Log in'))

        self.helper.layout = Layout(
            Field('login', 'password', autocomplete='off'),
        )

    def clean(self):
        login = self.cleaned_data.get('login')
        password = self.cleaned_data.get('password')
        if not login or not password:
            raise forms.ValidationError('Please enter login and password')
        return self.cleaned_data


class SignupForm(forms.Form):
    username = forms.CharField(required=False)
    email = forms.CharField(widget=forms.EmailInput, required=False)
    nickname = forms.CharField(required=False)
    password = forms.CharField(widget=forms.PasswordInput, required=False)
    repeat_password = forms.CharField(widget=forms.PasswordInput, required=False)
    avatar = forms.ImageField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Sign up'))

        self.helper.layout = Layout(
            Field('username', 'email', 'nickname', 'password', 'repeat_password', 'avatar', autocomplete='off'),
        )

    def clean(self):
        username = self.cleaned_data.get('username')
        email = self.cleaned_data.get('email')
        nickname = self.cleaned_data.get('nickname')
        password = self.cleaned_data.get('password')
        repeat_password = self.cleaned_data.get('repeat_password')
        if not username or not email or not nickname or not password or not repeat_password:
            raise forms.ValidationError('Please enter username, email, nickname, password and repeat password')
        if password != repeat_password:
            raise forms.ValidationError('Passwords do not match')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Username already exists')
        return self.cleaned_data

    def save(self):
        user = User(username=self.cleaned_data.get('username'), email=self.cleaned_data.get('email'))
        user.set_password(self.cleaned_data.get('password'))
        user.save()
        profile = Profile(user=user, nickname=self.cleaned_data.get('nickname'))
        profile.avatar = random.choice(['img/kitten.jpg', 'img/puppy.jpg', 'img/fox.jpg'])
        profile.save()
        return user


class AskForm(forms.Form):
    title = forms.CharField(required=False)
    text = forms.CharField(widget=forms.Textarea, required=False)
    tags = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Ask'))

        self.helper.layout = Layout(
            Field('title', 'text', 'tags', autocomplete='off'),
        )

    def parse_tags(self):
        tags = self.cleaned_data.get('tags')
        tags = tags.replace(' ', '')
        return tags.split(',')

    def clean(self):
        title = self.cleaned_data.get('title')
        text = self.cleaned_data.get('text')
        tags = self.parse_tags()
        if not title or not text or not tags:
            raise forms.ValidationError('Please enter title, text and tags')
        if len(tags) > 3:
            self.add_error('tags', 'Too many tags (more then 3).')
        if Question.objects.filter(title=title).exists():
            self.add_error('title', 'Question with this title already exists')
        return self.cleaned_data

    def save(self, user):
        question = Question(title=self.cleaned_data.get('title'), text=self.cleaned_data.get('text'), author=user)
        question.save()
        for tag in self.parse_tags():
            question.tags.add(Tag.objects.get_or_create(name=tag)[0])
        return question


class AnswerForm(forms.Form):
    text = forms.CharField(widget=forms.Textarea, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Answer'))

        self.helper.layout = Layout(
            Field('text', autocomplete='off'),
        )

    def clean(self):
        text = self.cleaned_data.get('text')
        if not text:
            self.add_error('text', 'Please enter text')
        return self.cleaned_data

    def save(self, question, user):
        answer = Answer(text=self.cleaned_data.get('text'), question=question, author=user)
        answer.save()
        return answer


class ProfileEditForm(forms.Form):
    login = forms.CharField(required=False)
    email = forms.CharField(widget=forms.EmailInput, required=False)
    nickname = forms.CharField(required=False)
    avatar = forms.ImageField(required=False)

    def __init__(self, *args, **kwargs):
        username = kwargs['user'].username
        email = kwargs['user'].email
        nickname = kwargs['user'].profile.nickname
        avatar = kwargs['user'].profile.avatar

        kwargs.pop('user')

        super().__init__(*args, **kwargs)

        self.fields['login'].initial = username
        self.fields['email'].initial = email
        self.fields['nickname'].initial = nickname
        self.fields['avatar'].initial = avatar

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Save'))

        self.helper.layout = Layout(
            Field('login', 'email', 'nickname', 'avatar', autocomplete='off')
        )

    def clean(self):
        username = self.cleaned_data.get('login')
        email = self.cleaned_data.get('email')
        nickname = self.cleaned_data.get('nickname')
        if not username or not email or not nickname:
            raise forms.ValidationError('Please enter login, email and nickname')
        if User.objects.filter(username=username).exists() and username != self.fields['login'].initial:
            self.add_error('login', 'Username already exists')
        return self.cleaned_data

    def save(self, user):
        user.username = self.cleaned_data.get('login')
        user.email = self.cleaned_data.get('email')
        user.save()
        user.profile.nickname = self.cleaned_data.get('nickname')
        user.profile.avatar = self.cleaned_data.get('avatar')
        user.profile.save()
        return user
