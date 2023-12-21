# # Create your models here.
from django.db import models
from accounts.models import User

class Article(models.Model):
    title = models.TextField()
    detail = models.TextField()
    category = models.CharField(max_length=50)
    link = models.URLField()
    img = models.URLField()
    
    def __str__(self):
        return self.category
    
class KeywordCount(models.Model):
    name = models.CharField(max_length=100)
    count = models.IntegerField(default=0)
    
class MyNews(models.Model):
    user = models.ManyToManyField(User)
    title = models.TextField()
    link = models.URLField()
    img = models.URLField()