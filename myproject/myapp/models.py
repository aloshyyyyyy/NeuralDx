from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class user_table(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15)
    place = models.CharField(max_length=100)
    login=models.ForeignKey(User,on_delete=models.CASCADE)



    def __str__(self):
        return self.name

class Prediction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='predictions/')
    result = models.CharField(max_length=50)
    confidence = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.result} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"