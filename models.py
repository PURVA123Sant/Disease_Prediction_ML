from datetime import datetime
from django.db import models


class Appointment(models.Model):
    doctor = models.CharField(max_length=40)
    patient = models.CharField(max_length=3000)
    disease = models.CharField(max_length=200,null=True)
    date = models.DateField(default=datetime.today())
    email = models.CharField(max_length=200,default='user@gmail.com')
    # considering over the world, max length of a mobile number can be 15 digits
    phone = models.CharField(max_length=15,default='9898989898')

class Doctor(models.Model):
    name = models.CharField(max_length=100)
    speciality = models.CharField(max_length=100,default="Gastrologist")
    qualification = models.CharField(max_length=100,default="MD")

