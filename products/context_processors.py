from decimal import Decimal, InvalidOperation

from .models import Category
from orders.models import Advertisement, Order, OrderDetail


def categories_processor(request):
    categories = Category.objects.all()
    order = None
    order_items = []
    cart_item_count = 0
    cart_total = 0
    shipping_Cost = 30
    coupon_discount = 0
    coupon_code = ''
    grand_total = 0

    if request.user.is_authenticated:
        order = Order.objects.filter(user=request.user, is_completed=False).first()
        if order:
            order_items = OrderDetail.objects.filter(order=order)
            cart_item_count = sum(item.quantity for item in order_items)
            cart_total = sum(item.quantity * item.price for item in order_items)
            try:
                coupon_discount = Decimal(str(request.session.get('coupon_discount', 0) or 0))
            except (InvalidOperation, TypeError, ValueError):
                coupon_discount = Decimal('0')
            coupon_code = request.session.get('coupon_code', '')
            if coupon_discount > cart_total:
                coupon_discount = cart_total
            grand_total = cart_total - coupon_discount + shipping_Cost
        else:
            grand_total = cart_total + shipping_Cost
    else:
        grand_total = cart_total + shipping_Cost

    return {
        'categories': categories,
        'order': order,
        'order_items': order_items,
        'cart_item_count': cart_item_count,
        'cart_total': cart_total,
        'shipping_Cost': shipping_Cost,
        'coupon_discount': coupon_discount,
        'coupon_code': coupon_code,
        'grand_total': grand_total,
        }





def advertisement_list(request):
    ads = Advertisement.objects.all()
    return {
        'ads': ads
    }