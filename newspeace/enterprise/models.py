from django.db import models
from datetime import datetime, timedelta
from django.utils import timezone

# Create your models here.
    
class Enterprise(models.Model):
    name = models.CharField(max_length=50, unique=True)
    code = models.CharField(max_length=20, blank=True)
    
    def __str__(self):
        return str(self.name)
    
    
class EnterpriseGraph(models.Model):
    enterprise = models.ForeignKey(Enterprise, on_delete=models.PROTECT)
    negative = models.SmallIntegerField(default=0)
    present = models.BigIntegerField(default=0)
    create_dt = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return str(self.enterprise)