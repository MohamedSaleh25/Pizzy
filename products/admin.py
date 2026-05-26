from django.contrib import admin
from .models import Category, Product, Occasion, ProductImage, SubCategory
# Register your models here.
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Occasion)
admin.site.register(ProductImage)
admin.site.register(SubCategory)