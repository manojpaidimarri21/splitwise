from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.exceptions import ValidationError
# Create your models here.


EVENT_TYPE_CHOICES =(
    ("equal", "equal"),
    ("unequal", "unequal"),
)

class Friend(models.Model):
    user1 = models.ForeignKey(User,on_delete=models.CASCADE, related_name="user1Friend")
    user2 = models.ForeignKey(User,on_delete=models.CASCADE, related_name="user2Friend")
    
    def __str__(self):
        return self.user1.username + '-' + self.user2.username 
    
class Group(models.Model):
    groupName = models.CharField(max_length=128)
    groupAdmin = models.ForeignKey(settings.AUTH_USER_MODEL,default=1,on_delete=models.CASCADE)
    member = models.ForeignKey(User,on_delete=models.CASCADE, related_name="member")
    
    def __str__(self):
        return self.groupName + '-' + self.groupAdmin.username + '-' + self.member.username

## user 1 red ----- amount positive
class Debt(models.Model):
    groupName = models.CharField(max_length=128)
    groupAdmin = models.ForeignKey(User,on_delete=models.CASCADE, related_name="DebtAdmin",default=1)
    user1 = models.ForeignKey(User,on_delete=models.CASCADE, related_name="user1Debt")
    user2 = models.ForeignKey(User,on_delete=models.CASCADE, related_name="user2Debt")
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.groupName + '-' + self.user1.username + '-' + self.user2.username 

##user 1 paid to user 2 amount positive
class settlement(models.Model):
    groupName = models.CharField(max_length=128)
    groupAdmin = models.ForeignKey(User,on_delete=models.CASCADE, related_name="SettleAdmin",default=1)
    user1 = models.ForeignKey(User,on_delete=models.CASCADE, related_name="user1settlement")
    user2 = models.ForeignKey(User,on_delete=models.CASCADE, related_name="user2settlement")
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    done_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.groupName + '-' + self.user1.username + '-' + self.user2.username 


class Event(models.Model):
    groupName = models.CharField(max_length=128)
    groupAdmin = models.ForeignKey(User,on_delete=models.CASCADE, related_name="EventAdmin",default=1)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,default=1,on_delete=models.CASCADE)
    payers = models.CharField(max_length=256)
    bearers = models.CharField(max_length=256)
    description = models.CharField(max_length=256)
    created_at = models.DateTimeField(auto_now_add=True)
    eventType = models.CharField(max_length=9,choices=EVENT_TYPE_CHOICES,default="equal")
    def __str__(self):
        return self.groupName + '-' + self.payers + '-' + self.bearers + '-' + self.description +  '-'+ self.eventType
    