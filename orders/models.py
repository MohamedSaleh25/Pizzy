from django.db import models
from django.contrib.auth.models import User
from products.models import Product
from project import settings
# Create your models here.
class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    is_completed = models.BooleanField(default=False)

    first_name = models.CharField(max_length=150, blank=True, null=True)
    last_name = models.CharField(max_length=150, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone_number = models.CharField(max_length=50, blank=True, null=True)
    city = models.CharField(max_length=200, blank=True, null=True)
    area = models.CharField(max_length=200, blank=True, null=True)
    street_name = models.CharField(max_length=255, blank=True, null=True)
    building_number = models.CharField(max_length=50, blank=True, null=True)
    floor_number = models.CharField(max_length=50, blank=True, null=True)
    flat_number = models.CharField(max_length=50, blank=True, null=True)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    coupon_code = models.CharField(max_length=50, blank=True, null=True)
    coupon_discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    grand_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    PAYMENT_METHODS = (
        ("card", "Card"),
        ("wallet", "Wallet"),
        ("cod", "Cash on Delivery"),
    )
    payment_method = models.CharField(max_length=20, null=True, blank=True)

    payment_status = models.CharField(
        max_length=20,
        default="pending"
    )

    paymob_order_id = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"Order {self.id} - {self.user.email}"

    @property
    def total_price(self):
        return sum(item.total_price for item in self.items.all())
    


class OrderDetail(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    @property
    def total_price(self):
        return self.quantity * self.price    



class Advertisement(models.Model):
    title = models.CharField(max_length=255)
    def __str__(self):
        return self.title