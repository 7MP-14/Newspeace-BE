from django import forms
from django.contrib.auth.forms import *
# from .models import Profile
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate

from django.contrib.auth.forms import ReadOnlyPasswordHashField
from .models import User

# class CustomUserCreationForm(UserCreationForm):
#     email = forms.EmailField(max_length=50, help_text='Required. Enter a valid email address.')
#     phone_number = forms.CharField(max_length=20, required=True)
#     notification_choice = forms.ChoiceField(
#         choices=[('email', 'Email'), ('sms', 'SMS')],
#         widget=forms.RadioSelect,
#         required=True,
#     )
#     agree_to_terms = forms.BooleanField(
#         required=True,
#         widget=forms.CheckboxInput,
#         help_text='I agree to the terms of service.',
#     )

#     class Meta(UserCreationForm.Meta):
#         model=get_user_model()
#         fields = UserCreationForm.Meta.fields + ('email', 'phone_number', 'notification_choice', 'agree_to_terms',)
    
#     def save(self, commit=True):
#         user = super().save(commit=False)
#         user.email = self.cleaned_data['email']
#         user.phone_number = self.cleaned_data['phone_number']
#         user.notification_choice = self.cleaned_data['notification_choice']
#         user.agree_to_terms = self.cleaned_data['agree_to_terms']
#         if commit:
#             user.save()
#             Profile.objects.create(user=user, 
#                                 phone_number=self.cleaned_data['phone_number'],
#                                 email=self.cleaned_data['email'],
#                                 notification_choice=self.cleaned_data['notification_choice'],
#                                 agree_to_terms=self.cleaned_data['agree_to_terms'])
#         return user

# class EmailAuthenticationForm(AuthenticationForm):
#     email = forms.EmailField(widget=forms.TextInput(attrs={'autofocus': True}))

#     def clean(self):
#         email = self.cleaned_data.get('email')
#         password = self.cleaned_data.get('password')

#         if email is not None and password:
#             self.user_cache = authenticate(self.request, email=email, password=password)
#             if self.user_cache is None:
#                 raise self.get_invalid_login_error()
#             else:
#                 self.confirm_login_allowed(self.user_cache)
#         return self.cleaned_data

class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(
        label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('email', 'phone_number','notification_choice','agree_to_terms')

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

    class Meta:
        model = User
        fields = ('email', 'password', 'phone_number','notification_choice','agree_to_terms',
                  'is_active', 'is_admin')

    def clean_password(self):
        return self.initial["password"]