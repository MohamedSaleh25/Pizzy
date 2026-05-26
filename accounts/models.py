from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.conf import settings
from products.models import Product


# Create your models here.
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    username = None
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = CustomUserManager()






class City(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name  

class Area(models.Model):
    name = models.CharField(max_length=100)
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='areas')
    
    def __str__(self):
        return f"{self.name} - {self.city.name}"


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    favorite_products = models.ManyToManyField(Product, blank=True, related_name='favorited_by')
    city = models.ForeignKey(City, on_delete=models.CASCADE, blank=True, null=True)
    area = models.ForeignKey(Area, on_delete=models.CASCADE, blank=True, null=True)
    street_name = models.CharField(max_length=50, blank=True)
    building_number = models.IntegerField(blank=True, null=True)
    floor_number = models.IntegerField(blank=True, null=True)
    flat_number = models.IntegerField(blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    save_info = models.BooleanField(default=False)


    
    def __str__(self):
        return self.user.email
    
class Client(models.Model):
    firstname = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    area = models.ForeignKey(Area, on_delete=models.CASCADE)
    street_name = models.CharField(max_length=50, blank=True)
    building_number = models.IntegerField(blank=True, null=True)
    floor_number = models.IntegerField(blank=True, null=True)
    flat_number = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f"{self.firstname} {self.lastname}"
    

# models.py
from django.db import models
from django.utils import timezone

class Coupon(models.Model):
    code = models.CharField(max_length=20, unique=True)
    discount_percent = models.PositiveIntegerField()

    active = models.BooleanField(default=True)

    start_date = models.DateTimeField(default=timezone.now)
    expiry_date = models.DateTimeField(null=True, blank=True)

    max_uses = models.PositiveIntegerField(default=1)
    used_count = models.PositiveIntegerField(default=0)

    users = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True)

    def is_valid(self):
        now = timezone.now()

        if not self.active:
            return False
        if self.expiry_date and now > self.expiry_date:
            return False
        if self.used_count >= self.max_uses:
            return False

        return True

    def __str__(self):
        return self.code