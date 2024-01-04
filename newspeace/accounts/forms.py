from django import forms
from django.contrib.auth.forms import *
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate

from django.contrib.auth.forms import ReadOnlyPasswordHashField
from .models import *
from django.db.models import Q


class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(
        label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('email', 'name')

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()
    keyword_input = forms.CharField(max_length=255, required=False)
    delete_keywords = forms.ModelMultipleChoiceField(
        queryset=Keyword.objects.none(),  # 초기 queryset을 빈 상태로 설정
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label='삭제할 키워드',
    )

    class Meta:
        model = User
        fields = ('email', 'password', 'name', 'emailNotice')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 초기 queryset을 현재 유저의 키워드로 설정
        self.fields['delete_keywords'].queryset = self.instance.keywords.all()

    def clean_keyword_input(self):
        keywords_text = self.cleaned_data.get('keyword_input')
        if keywords_text:
            keywords = [keyword.strip() for keyword in keywords_text.split(',')]
            return keywords
        return []

    def save(self, commit=True):
        user = super().save(commit=False)

        # 키워드 추가
        keywords = self.cleaned_data.get('keyword_input')
        if keywords:
            for keyword_text in keywords:
                keyword, created = Keyword.objects.get_or_create(keyword_text=keyword_text)
                if created or not user.keywords.filter(Q(keyword_text__iexact=keyword_text)).exists():
                    user.keywords.add(keyword)

        # 키워드 삭제
        delete_keywords = self.cleaned_data.get('delete_keywords')
        if delete_keywords:
            user.keywords.remove(*delete_keywords)

        if commit:
            user.save()

        return user

    def clean_password(self):
        return self.initial["password"]
