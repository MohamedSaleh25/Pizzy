# services.py
from .models import Coupon


def get_valid_coupon(code, user):
    try:
        coupon = Coupon.objects.get(code=code.upper())
    except Coupon.DoesNotExist:
        return None

    if not coupon.is_valid():
        return None

    return coupon


def mark_coupon_as_used(coupon_code, user):
    """Increment coupon usage count and add user to coupon users list."""
    try:
        coupon = Coupon.objects.get(code=coupon_code.upper())
        coupon.used_count += 1
        coupon.save()
        if user and user.is_authenticated:
            coupon.users.add(user)
    except Coupon.DoesNotExist:
        pass