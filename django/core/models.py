from django.db import models

# Create your models here.
class PoliceStation(models.Model):
    
    email = models.EmailField(max_length=254)
    zip_code = models.CharField(max_length=8)
    street_name = models.CharField(max_length=50)
    street_number = models.IntegerField()
    city = models.CharField(max_length=50)

class Wello(models.Model):

    police_station = models.ForeignKey("PoliceStation", on_delete=models.CASCADE)
    plate_number = models.CharField(max_length=10,unique=True)

class ConnectedAssistant(models.Model):

    serial_number = models.CharField(max_length=20,unique=True)
    listenning = models.BooleanField(default=False)
    turn_on = models.BooleanField(default=False)

class Agent(models.Model):
    
    registration_number = models.IntegerField(primary_key=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)

class Patrol(models.Model):

    agent = models.ForeignKey("Agent", on_delete=models.CASCADE)
    wello = models.ForeignKey("Wello",  on_delete=models.CASCADE)
    connected_assistant = models.ForeignKey("ConnectedAssistant", on_delete=models.CASCADE)
    start = models.DateTimeField(auto_now=True, auto_now_add=False)
    end = models.DateTimeField(null=True)

class Detection(models.Model):

    sound_nature = models.CharField(max_length=20)
    detected_at = models.DateTimeField(auto_now=True, auto_now_add=False)
    seen_by_agent = models.BooleanField(default=False)
    confirmed_by_agent = models.BooleanField(default=False)
    false_positive = models.BooleanField(default=False)
    message_sent = models.BooleanField(default=False)
    comment = models.TextField()
    patrol = models.ForeignKey("Patrol", on_delete=models.CASCADE)

class AlertTemplate(models.Model):
    alert_code = models.IntegerField(primary_key=True)
    alert_message = models.TextField()

    
