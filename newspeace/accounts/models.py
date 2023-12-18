from django.db import models
from django.conf import settings
from django.contrib.auth.models import (BaseUserManager, AbstractBaseUser)

class UserManager(BaseUserManager):
    def create_user(self, email, phone_number, notification_choice, agree_to_terms, password=None):
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            phone_number=phone_number,
            notification_choice=notification_choice,
            agree_to_terms=agree_to_terms,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, phone_number, notification_choice, agree_to_terms, password):
        user = self.create_user(
            email,
            password=password,
            phone_number=phone_number,
            notification_choice=notification_choice,
            agree_to_terms=agree_to_terms,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    email = models.EmailField(
        verbose_name='email',
        max_length=255,
        unique=True,
    )
    phone_number=models.CharField(max_length=20)
    notification_choice = models.CharField(
        max_length=10,
        choices=[('email', 'Email'), ('sms', 'SMS')],
        default='email',
    )
    agree_to_terms = models.BooleanField()

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['phone_number','notification_choice','agree_to_terms']

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin
# class User(AbstractUser):
#     pass

# # auth의 user 모델과 1:1 관계 user의 프로필 테이블
# class Profile(models.Model):
#     user=models.OneToOneField(User, on_delete=models.CASCADE)
#     email=models.CharField(max_length=50)
#     phone_number=models.CharField(max_length=20)
#     notification_choice = models.CharField(
#         max_length=10,
#         choices=[('email', 'Email'), ('sms', 'SMS')],
#         default='email',
#     )
#     agree_to_terms = models.BooleanField()

