# # Create your models here.
from django.db import models
from accounts.models import User
from django.utils import timezone


class Article(models.Model):
    title = models.TextField()
    detail = models.TextField()
    category = models.CharField(max_length=50)
    link = models.URLField()
    img = models.URLField()
    create_dt = models.DateTimeField(default=timezone.now)
    write_dt = models.DateTimeField(default=timezone.now)
    sentiment = models.IntegerField(default=0)
    
    # def __str__(self):
    #     return self.category
    
    def __str__(self):
        return f"[{str(self.id)}]  {self.title[:40]}"
    
class KeywordCount(models.Model):
    name = models.CharField(max_length=100)
    count = models.IntegerField(default=0)
    
class MyNews(models.Model):
    user = models.ManyToManyField(User)
    newsid = models.IntegerField(default=0)
    title = models.TextField()
    link = models.URLField()
    img = models.URLField()
    save_dt = models.DateTimeField(default=timezone.now)
    
class TemporalyArticle(models.Model):
    title = models.TextField()
    detail = models.TextField()
    category = models.CharField(max_length=50)
    link = models.URLField()
    img = models.URLField()
    create_dt = models.DateTimeField(default=timezone.now)
    write_dt = models.DateTimeField(default=timezone.now)
    