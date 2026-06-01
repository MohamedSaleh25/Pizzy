from datetime import datetime
from django.db import models
from django.utils.text import slugify

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(blank=True, unique=True, null=True)
    image = models.ImageField(upload_to='category_images/%Y/%m/%d/', null=True, blank=True)
    def subcategories_count(self):
        return self.subcategories.count()

    def save(self, *args, **kwargs): 
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)    
    def __str__(self):
        return self.name    


class SubCategory(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(blank=True, unique=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories')
    image = models.ImageField(upload_to='subcategory_images/%Y/%m/%d/', null=True, blank=True)

    def product_count(self):
        return self.products.count()
    def save(self, *args, **kwargs): 
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)    
    def __str__(self):
        return self.name



class Occasion(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name
    


class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    old_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    image = models.ImageField(upload_to='product_images/%Y/%m/%d/')
    quantity_available = models.IntegerField(default=5)  # الكمية المتاحة
    quantity_sold = models.IntegerField(default=0)
    subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE, related_name='products', null=True, blank=True)
    is_new = models.BooleanField(default=False)
    is_on_sale = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    isbestseller = models.BooleanField(default=False)
    istopfeatured = models.BooleanField(default=False)
    occasion = models.ManyToManyField(Occasion, blank=True, related_name='products')
    published_date = models.DateTimeField(default=datetime.now)

    def __str__(self):
        return self.name
        
    @property
    def is_sold_out(self):
        return self.quantity_available <= 0    

    class Meta:
        ordering = ['-published_date']


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='product_images/%Y/%m/%d/')
    is_primary = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.product.name} - Image {self.order}"     