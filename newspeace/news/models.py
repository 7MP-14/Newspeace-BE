from django.db import models
from accounts.models import User

# Create your models here.
    
class Keywords(models.Model):
    # user = models.ManyToManyField('User')
    article = models.ManyToManyField("Article", blank=True)
    keyword = models.CharField(max_length=100, null=True, blank=True)
    
    def __str__(self):        
        return self.keyword
    
class Article(models.Model):
    # user = models.ManyToManyField('User')
    category = models.CharField(max_length=30)
    title = models.TextField()
    content = models.TextField()
    articleUrl = models.URLField()
    articleImgUrl = models.URLField()
    
    def __str__(self):
        return self.category
    
