from django.db import models

# Create your models here.
class GradeSheet(models.Model):
    id = models.AutoField 
    reg_no = models.CharField(max_length=10, default="")
    name = models.CharField(max_length=50, default="")
    session = models.CharField(max_length=8, default="")
    courses = models.CharField(max_length=1000, default="")
    obtained = models.CharField(max_length=1000, default="") 