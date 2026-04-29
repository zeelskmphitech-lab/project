from django.db import models
from django.contrib.auth.models import AbstractUser

class Users(AbstractUser):
    email = models.EmailField(unique=True)
    is_seller = models.BooleanField(default=False)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name','is_seller']
    def __str__(self):
        return f"{self.email}"