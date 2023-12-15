from django import forms
from django.contrib.auth.forms import *
from .models import Profile
from django.contrib.auth import get_user_model

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(max_length=50, help_text='Required. Enter a valid email address.')
    phone_number = forms.CharField(max_length=20, required=True)
    notification_choice = forms.ChoiceField(
        choices=[('email', 'Email'), ('sms', 'SMS')],
        widget=forms.RadioSelect,
        required=True,
    )
    agree_to_terms = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput,
        help_text='I agree to the terms of service.',
    )

    class Meta(UserCreationForm.Meta):
        model=get_user_model()
        fields = UserCreationForm.Meta.fields + ('email', 'phone_number', 'notification_choice', 'agree_to_terms',)
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.phone_number = self.cleaned_data['phone_number']
        user.notification_choice = self.cleaned_data['notification_choice']
        user.agree_to_terms = self.cleaned_data['agree_to_terms']
        if commit:
            user.save()
    # def save(self):
    #     user=super().save()
    #     Profile.objects.create(user=user, 
    #                            phone_number=self.cleaned_data['phone_number'],
    #                            email=self.cleaned_data['email'],
    #                            notification_choice=self.cleaned_data['notification_choice'],
    #                            agree_to_terms=self.cleaned_data['agree_to_terms'])
        return user

class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(widget=forms.TextInput(attrs={'autofocus': True}))
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Email'