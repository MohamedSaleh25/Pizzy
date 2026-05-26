from django.contrib import admin
from .models import City, Area, CustomUser, UserProfile ,Client, Coupon

# Register your models here.
admin.site.register(City)
admin.site.register(Area)   
admin.site.register(CustomUser)
admin.site.register(UserProfile)
admin.site.register(Client) 
admin.site.register(Coupon)