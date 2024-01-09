from django.db import models
from django.conf import settings
from django.contrib.auth.models import (BaseUserManager, AbstractBaseUser)
from django.utils import timezone

class UserManager(BaseUserManager):
    def create_user(self, email, name, emailNotice=None, password=None):
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            name=name,
            emailNotice=emailNotice,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, emailNotice, password):
        user = self.create_user(
            email,
            name=name,
            emailNotice=emailNotice,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user
    
# keyword 테이블 user와 n:m 관계이다.
class Keyword(models.Model):
    keyword_text = models.CharField(max_length=255)
    ratio = models.IntegerField(default=0) # 임시로.. 추후에 긍/부 비율을 나타내야 하는 것에 따라 수정 필요./완료
    # code = models.CharField(max_length=10, null=True)
    
    def __str__(self):
        return self.keyword_text

class User(AbstractBaseUser):
    email = models.EmailField(
        verbose_name='email',
        max_length=255,
        unique=True,
    )
    name=models.CharField(max_length=20)
    emailNotice = models.BooleanField(null=True, blank=True, default=False)
    keywords = models.ManyToManyField(Keyword, blank=True)
    
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(null=True, default=False)   # 이메일 인증 완료 여부

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name','emailNotice']

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin


# # keyword 테이블과 1:m 관계이다.
# class NegativeKeywordInfo(models.Model):
#     keyword = models.ForeignKey(Keyword, on_delete=models.CASCADE)
#     create_dt = models.DateTimeField(default=timezone.now)
#     negative = models.SmallIntegerField(default=0)
#     present = models.BigIntegerField(default=0)
    
#     def __str__(self):
#         return str(self.keyword_id) + str(self.keyword)


