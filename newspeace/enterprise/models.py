from django.db import models
from datetime import datetime, timedelta
from django.utils import timezone  # test_0106_josephh

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
    # create_dt = models.DateTimeField(default=datetime.now())
    create_dt = models.DateTimeField(default=timezone.now)  # test_0106_josephh / 마이이그래션 해야 되는지??
    
    def __str__(self):
        return str(self.enterprise)







