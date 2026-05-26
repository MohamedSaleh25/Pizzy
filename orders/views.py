from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone

from project.settings import PAYMOB_API_KEY, PAYMOB_INTEGRATION_ID, PAYMOB_IFRAME_ID
from .models import  Product, Order, OrderDetail

def add_to_cart(request):
    if request.method != 'POST':
        messages.error(request, 'Invalid request.')
        return redirect(request.META.get('HTTP_REFERER', '/'))

    if not request.user.is_authenticated:
        messages.error(request, 'Please login first.')
        return redirect(request.META.get('HTTP_REFERER', '/'))

    product_id = request.POST.get('product_id')
    quantity = request.POST.get('quantity', '1')

    if not product_id:
        messages.error(request, 'Product not found.')
        return redirect(request.META.get('HTTP_REFERER', '/'))

    try:
        quantity = int(quantity)
        if quantity < 1:
            quantity = 1
    except (TypeError, ValueError):
        quantity = 1

    product = get_object_or_404(Product, id=product_id)
    order = Order.objects.filter(user=request.user, is_completed=False).first()

    if not order:
        order = Order.objects.create(
            user=request.user,
            created_at=timezone.now(),
            is_completed=False
        )

    order_detail, created = OrderDetail.objects.get_or_create(
        order=order,
        product=product,
        defaults={'quantity': quantity, 'price': product.price}
    )

    if not created:
        order_detail.quantity += quantity
        order_detail.save()

    messages.success(request, 'Product added to cart successfully.')
    #return redirect('/accounts/cart/')
    return redirect(request.META.get('HTTP_REFERER', '/'))



import requests

def get_paymob_token():
    url = "https://accept.paymob.com/api/auth/tokens"
    r = requests.post(url, json={"api_key": PAYMOB_API_KEY})
    return r.json()["token"]


def create_paymob_order(token, amount_cents, order_id):
    url = "https://accept.paymob.com/api/ecommerce/orders"

    data = {
        "auth_token": token,
        "delivery_needed": "false",
        "amount_cents": amount_cents,
        "currency": "EGP",
        "merchant_order_id": order_id,
        "items": []
    }

    r = requests.post(url, json=data)
    return r.json()

def get_payment_key(token, paymob_order_id, amount_cents, billing_data=None):
    url = "https://accept.paymob.com/api/acceptance/payment_keys"

    if billing_data is None:
        billing_data = {
            "first_name": "Guest",
            "last_name": "User",
            "email": "guest@example.com",
            "phone_number": "01000000000",
            "city": "Cairo",
            "country": "EG",
            "street": "street"
        }

    data = {
        "auth_token": token,
        "amount_cents": amount_cents,
        "expiration": 3600,
        "order_id": paymob_order_id,
        "integration_id": PAYMOB_INTEGRATION_ID,
        "billing_data": billing_data,
        "currency": "EGP"
    }

    r = requests.post(url, json=data)
    return r.json().get("token")



from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def paymob_webhook(request):
    data = json.loads(request.body)

    if data.get("success"):
        order_id = data["order"]["merchant_order_id"]

        order = Order.objects.get(id=order_id)
        order.is_completed = True
        order.payment_status = "paid"
        order.save()
        # Mark coupon as used
        coupon_code = order.coupon_code
        if coupon_code:
            from accounts.services import mark_coupon_as_used
            mark_coupon_as_used(coupon_code, order.user)

    return JsonResponse({"status": "ok"})


