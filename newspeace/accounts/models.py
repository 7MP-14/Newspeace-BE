from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    pass

# auth의 user 모델과 1:1 관계 user의 프로필 테이블
class Profile(models.Model):
    user=models.OneToOneField(User, on_delete=models.CASCADE)
    email=models.CharField(max_length=50)
    phone_number=models.CharField(max_length=20)
    notification_choice = models.CharField(
        max_length=10,
        choices=[('email', 'Email'), ('sms', 'SMS')],
        default='email',
    )
    agree_to_terms = models.BooleanField()

