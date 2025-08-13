from django.db import models
from django.contrib.auth.models import AbstractUser
from users.managers import CustomUserManager
# Create your models here.

class User(AbstractUser):
    SELLER = 'Seller'
    BUYER = 'Buyer'

    ROLE_CHOICES = [
        (SELLER,'Seller'),
        (BUYER,'Buyer')
    ]

    username = None
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=8, choices=ROLE_CHOICES)
    address = models.TextField(blank=True, null= True)
    phone_number = models.CharField(max_length=15, blank=True, null= True)


    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email