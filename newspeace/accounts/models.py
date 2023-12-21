from django.db import models
from django.conf import settings
from django.contrib.auth.models import (BaseUserManager, AbstractBaseUser)

class UserManager(BaseUserManager):
    def create_user(self, email, name, phone_number, emailNotice=None, smsNotice=None, password=None):
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            name=name,
            phone_number=phone_number,
            emailNotice=emailNotice,
            smsNotice=smsNotice,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, phone_number, emailNotice, smsNotice, password):
        user = self.create_user(
            email,
            name=name,
            phone_number=phone_number,
            emailNotice=emailNotice,
            smsNotice=smsNotice,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user
    
# keyword 테이블 user와 n:m 관계이다.
class Keyword(models.Model):
    keyword_text = models.CharField(max_length=255)
    ratio = models.IntegerField(null=True) # 임시로.. 추후에 긍/부 비율을 나타내야 하는 것에 따라 수정 필요.
    
    def __str__(self):
        return self.keyword_text

class User(AbstractBaseUser):
    email = models.EmailField(
        verbose_name='email',
        max_length=255,
        unique=True,
    )
    name=models.CharField(max_length=20)
    phone_number=models.CharField(max_length=20)
    emailNotice = models.BooleanField(null=True, blank=True)
    smsNotice = models.BooleanField(null=True, blank=True)
    keywords = models.ManyToManyField(Keyword, blank=True)
    
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)   # 이메일 인증 완료 여부

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name','phone_number','emailNotice','smsNotice']

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin




