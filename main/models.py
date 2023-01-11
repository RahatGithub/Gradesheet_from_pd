from django.db import models

# Create your models here.
class GradeSheet(models.Model):
    id = models.AutoField 
    reg_no = models.CharField(max_length=10, default="")
    name = models.CharField(max_length=50, default="")
    institute = models.CharField(max_length=100, default="")
    department = models.CharField(max_length=100, default="")
    session = models.CharField(max_length=10, default="")
    results = models.CharField(max_length=1000, default="")
    status = models.BooleanField(default=False)