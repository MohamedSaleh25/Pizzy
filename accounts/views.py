
from decimal import Decimal, InvalidOperation

from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth import get_user_model, login, authenticate
from django.views.decorators.csrf import ensure_csrf_cookie
from orders.models import Order, OrderDetail
from orders.views import get_paymob_token, create_paymob_order, get_payment_key
from project.settings import PAYMOB_IFRAME_ID
from products.models import Product
from .models import Client, UserProfile, Area, City
import re 
from django.contrib import messages
from django.contrib import auth

User = get_user_model()
# Create your views here.
def cart(request):
    order = None
    order_items = []
    cart_total = Decimal('0.00')
    try:
        coupon_discount = Decimal(str(request.session.get('coupon_discount', 0) or 0))
    except (InvalidOperation, TypeError, ValueError):
        coupon_discount = Decimal('0')
    coupon_code = request.session.get('coupon_code', '')
    shipping_Cost = 30


    if request.user.is_authenticated :
        order = Order.objects.filter(user=request.user, is_completed=False).first()
        if order:
            order_items = OrderDetail.objects.filter(order=order)
            cart_total = sum(item.total_price for item in order_items)
            if coupon_discount > cart_total:
                coupon_discount = cart_total
                request.session['coupon_discount'] = str(coupon_discount)

    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, 'Please login first to update cart.')
            return redirect('accounts:cart')

        if order:
            if request.POST.get('apply_coupon'):
                coupon_code = request.POST.get('coupon_code', '').strip().upper()
                if not coupon_code:
                    request.session.pop('coupon_discount', None)
                    request.session.pop('coupon_code', None)
                    messages.info(request, 'Coupon removed.')

                from .services import get_valid_coupon

                coupon = get_valid_coupon(coupon_code, request.user)
                if coupon:
                    discount_percent = coupon.discount_percent
                    discount = (cart_total * discount_percent) / 100
                    if discount > cart_total:
                        discount = cart_total
                    request.session['coupon_discount'] = str(discount)
                    request.session['coupon_code'] = coupon_code
                    messages.success(request, f'Coupon "{coupon_code}" applied. You saved {discount} EGP.')
                else:
                    request.session.pop('coupon_discount', None)
                    request.session.pop('coupon_code', None)
                    messages.error(request, 'Invalid coupon code.')
                return redirect('accounts:cart')

            remove_item_id = request.POST.get('remove_item')
            if remove_item_id:
                try:
                    remove_item_id = int(remove_item_id)
                except (ValueError, TypeError):
                    remove_item_id = None

                if remove_item_id:
                    OrderDetail.objects.filter(id=remove_item_id, order=order).delete()
                    return redirect('accounts:cart')

            for key, value in request.POST.items():
                if key.startswith('quantity_'):
                    try:
                        order_detail_id = int(key.split('_', 1)[1])
                        quantity = int(value)
                    except (ValueError, TypeError):
                        continue

                    if quantity < 1:
                        quantity = 1

                    order_detail = OrderDetail.objects.filter(id=order_detail_id, order=order).first()
                    if order_detail:
                      #  order_detail.quantity = quantity
                       # order_detail.save()
                         product = order_detail.product
                        
                        # الفحص: لو الكمية المطلوبة أكبر من المتاح في المخزن
                         if quantity > product.quantity_available:
                            if product.quantity_available <= 0:
                                messages.error(request, f'Sorry, "{product.name}" is Sold Out!')
                                order_detail.delete()  # احذفه من الكارت لأنه خلص تماماً
                            else:
                                messages.warning(request, f'Only {product.quantity_available} items available for "{product.name}".')
                                order_detail.quantity = product.quantity_available
                                order_detail.save()
                         else:
                            # لو الكمية متاحة تمام، بنحفظ عادي
                            order_detail.quantity = quantity
                            order_detail.save()
            return redirect('accounts:cart')
        return redirect('accounts:cart')

    grand_total = cart_total - coupon_discount + shipping_Cost
    if grand_total < 0:
        grand_total = 0

    return render(request, 'accounts/cart.html', {
        'order': order,
        'order_items': order_items,
        'cart_total': cart_total,
        'coupon_discount': coupon_discount,
        'coupon_code': coupon_code,
        'grand_total': grand_total,
    })


@ensure_csrf_cookie
def checkout(request):
     areas = Area.objects.all()
     cities = City.objects.all()
     is_added = request.session.pop('is_added', False)

     order = None
     order_items = []
     cart_total = 0
     try:
          coupon_discount = Decimal(str(request.session.get('coupon_discount', 0) or 0))
     except (InvalidOperation, TypeError, ValueError):
          coupon_discount = Decimal('0')
     shipping_Cost = 30

     if request.user.is_authenticated:
          order = Order.objects.filter(user=request.user, is_completed=False).first()
          if order:
               order_items = OrderDetail.objects.filter(order=order)
               cart_total = sum(item.total_price for item in order_items)
               if coupon_discount > cart_total:
                    coupon_discount = cart_total
                    request.session['coupon_discount'] = str(coupon_discount)

     grand_total = cart_total - coupon_discount + shipping_Cost
     if grand_total < 0:
          grand_total = 0

     if request.method == 'POST':
          action = request.POST.get('action')

               
          #------Login------------
          if action == 'login':
               email = request.POST.get('login_email')
               password = request.POST.get('login_password')
               has_error = False
               if not email:
                    messages.error(request, 'Email is required.', extra_tags='login')
                    has_error = True
               if not password:
                    messages.error(request, 'Password is required.', extra_tags='login')
                    has_error = True
               if not has_error:
                    user = authenticate(request, email=email, password=password)
                    if user:
                         if 'remember'  not in request.POST:
                              request.session.set_expiry(0)  
                         login(request, user)
                         messages.success(request, 'Login success', extra_tags='login')
                    else:
                         messages.error(request, 'Invalid email or password.', extra_tags='login')

          #------Register------------
          elif action == 'register':
               fname = request.POST.get('fname')
               lname = request.POST.get('lname')
               email = request.POST.get('signup_email')
               password = request.POST.get('signup_password')
               has_error = False
               is_added=False
               
               if not fname:
                    messages.error(request, 'First name is required.', extra_tags='register')
                    has_error = True
              
               if not lname:
                    messages.error(request, 'Last name is required.', extra_tags='register')
                    has_error = True
               
               if not email:
                    messages.error(request, 'Email is required.', extra_tags='register')
                    has_error = True
               
               if not password:
                    messages.error(request, 'Password is required.', extra_tags='register')                   
                    has_error = True
               if not has_error:
                    #check if email already exists
                    if User.objects.filter(email=email).exists():
                         messages.error(request, 'Email already exists.', extra_tags='register')
                    else:
                         patt = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                         if re.match(patt, email):
                              #add user
                              user = User.objects.create_user(email=email, first_name=fname, last_name=lname, password=password)
                              user.save()
                              login(request, user)
                              messages.success(request, 'Registration success', extra_tags='register')
                              request.session['is_added'] = True
                              return redirect('accounts:checkout')
                         else:
                              messages.error(request, 'Invalid email format.', extra_tags='register')
               return render(request, 'accounts/checkout.html', {
                                                  'fname': fname,
                                                  'lname': lname,
                                                  'email': email,
                                                  'is_added': is_added,
                                                  'areas': areas,
                                                  'cities': cities,
                                                  'order_items': order_items,
                                                  'cart_total': cart_total,
                                                  'coupon_discount': coupon_discount,
                                                  'grand_total': grand_total,
                                                  'shipping_Cost': shipping_Cost,
                                                  })
                              


          #------Checkout------------
          elif action == 'checkout':
                    if not request.user.is_authenticated:
                         messages.error(request, 'Please login first to place your order.', extra_tags='checkout')
                         return redirect('accounts:checkout')

                    fname2 = request.POST.get('fname2')
                    lname2 = request.POST.get('lname2')
                    order_email = request.POST.get('order_email')
                    phonenum=request.POST.get('phonenum')
                    city_id = request.POST.get('city')
                    area_id = request.POST.get('area')
                    
                    # Validate city and area are numeric
                    try:
                         city_id = int(city_id) if city_id else None
                         area_id = int(area_id) if area_id else None
                    except (ValueError, TypeError):
                         city_id = None
                         area_id = None
                    
                    city = City.objects.filter(id=city_id).first() if city_id else None
                    area = Area.objects.filter(id=area_id).first() if area_id else None
                    streetname = request.POST.get('streetname')
                    buildingnum = request.POST.get('buildingnum')
                    floornum = request.POST.get('floornum')
                    flatnum = request.POST.get('flatnum')  
                    save_info = request.POST.get('save_info')
                    has_error = False
                    
                    if not fname2:
                         messages.error(request, 'First name is required.', extra_tags='checkout')
                         has_error = True

                    if not lname2:
                         messages.error(request, 'Last name is required.', extra_tags='checkout')
                         has_error = True
                    if not order_email:
                         messages.error(request, 'Email is required.', extra_tags='checkout')
                         has_error = True     
                    if not phonenum:
                         messages.error(request, 'Phone number is required.', extra_tags='checkout')
                         has_error = True

                    elif not phonenum.isdigit():
                         messages.error(request, 'Phone number must contain numbers only.', extra_tags='checkout')
                         has_error = True

                    elif len(phonenum) != 11:
                         messages.error(request, 'Phone number must be exactly 11 digits.', extra_tags='checkout')
                         has_error = True
                    if not city:
                         messages.error(request, 'City is required.', extra_tags='checkout')
                         has_error = True
                    
                    if not area:
                         messages.error(request, 'Area is required.', extra_tags='checkout')
                         has_error = True
                    
                    if not streetname:
                         messages.error(request, 'Street name is required.', extra_tags='checkout')
                         has_error = True
                    
                    if not buildingnum:
                         messages.error(request, 'Building number is required.', extra_tags='checkout')
                         has_error = True
                    
                    if not floornum:
                         messages.error(request, 'Floor number is required.', extra_tags='checkout')
                         has_error = True
                    
                    if not flatnum:
                         messages.error(request, 'Flat number is required.', extra_tags='checkout')
                         has_error = True
                    
                    if not has_error:
                         user_obj = None
                         if request.user.is_authenticated and request.user.email == order_email:
                              user_obj = request.user
                         elif User.objects.filter(email=order_email).exists():
                              user_obj = User.objects.get(email=order_email)

                         if user_obj:
                              UserProfile.objects.update_or_create(
                                   user=user_obj,
                                   defaults={
                                        'phone_number': phonenum,
                                        'city': city,
                                        'area': area,
                                        'street_name': streetname,
                                        'building_number': buildingnum,
                                        'floor_number': floornum,
                                        'flat_number': flatnum,
                                        'save_info': save_info == 'on'
                                   }
                              )
                         else:
                              patt = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[A-Za-z]{2,}$'
                              if re.fullmatch(patt, order_email):
                                   Client.objects.update_or_create(
                                        email=order_email,
                                        defaults={
                                             'firstname': fname2,
                                             'lastname': lname2,
                                             'city': city,
                                             'area': area,
                                             'street_name': streetname,
                                             'building_number': buildingnum,
                                             'floor_number': floornum,
                                             'flat_number': flatnum
                                        }
                                   )
                              else:
                                   messages.error(request, 'Invalid email format.', extra_tags='checkout')
                                   return render(request, 'accounts/checkout.html', {
                                        'fname2': fname2,
                                        'lname2': lname2,
                                        'order_email': order_email,
                                        'streetname': streetname,
                                        'buildingnum': buildingnum,
                                        'floornum': floornum,
                                        'flatnum': flatnum,
                                        'areas': areas,
                                        'cities': cities,
                                   })

                         payment_method = request.POST.get('paymentMethod')
                         order = Order.objects.filter(user=request.user, is_completed=False).first()
                         if not order:
                              messages.error(request, 'No active cart found.', extra_tags='checkout')
                              return redirect('accounts:cart')

                         try:
                              coupon_discount = Decimal(str(request.session.get('coupon_discount', 0) or 0))
                         except (InvalidOperation, TypeError, ValueError):
                              coupon_discount = Decimal('0')
                         shipping_cost = 30
                         subtotal = order.total_price
                         grand_total = subtotal - coupon_discount + shipping_cost
                         if grand_total < 0:
                              grand_total = 0

                         order.first_name = fname2
                         order.last_name = lname2
                         order.email = order_email
                         order.phone_number = phonenum
                         order.city = city.name if city else ''
                         order.area = area.name if area else ''
                         order.street_name = streetname
                         order.building_number = buildingnum
                         order.floor_number = floornum
                         order.flat_number = flatnum
                         order.subtotal = subtotal
                         order.shipping_cost = shipping_cost
                         order.coupon_code = request.session.get('coupon_code', '')
                         order.coupon_discount = coupon_discount
                         order.grand_total = grand_total
                         order.payment_method = payment_method
                         order.payment_status = 'pending'
                         order.save()

                         if payment_method == 'cod':
                              for item in order_items:
                                try:
                                   for item in order_items:
                                        product = item.product
                                        
                                        # فحص أمان: لو الحقل مش متعرّف أو بـ None خليه بـ 0 عشان ميضربش
                                        if product.quantity_available is None:
                                             product.quantity_available = 0
                                        if product.quantity_sold is None:
                                             product.quantity_sold = 0
                                             
                                        product.quantity_available -= item.quantity
                                        product.quantity_sold += item.quantity
                                        product.save()
                                except Exception as e:
                                   # السطر ده هيطبع لك سبب المشكلة بالظبط في الـ Terminal باللون الأحمر
                                   print("\n❌❌ ERROR IN STOCK UPDATE:", str(e), "\n")   
                                   product.save()
                              order.is_completed = True
                              order.payment_status = 'paid'
                              order.save()
                              # Mark coupon as used
                              coupon_code = order.coupon_code
                              if coupon_code:
                                   from .services import mark_coupon_as_used
                                   mark_coupon_as_used(coupon_code, request.user)
                              request.session.pop('coupon_discount', None)
                              request.session.pop('coupon_code', None)
                              return redirect('accounts:order_success', order_id=order.id)

                         token = get_paymob_token()
                         amount_cents = int(grand_total * 100)
                         paymob_order = create_paymob_order(token, amount_cents, order.id)
                         paymob_id = paymob_order.get('id')
                         if not paymob_id:
                              messages.error(request, 'Paymob order creation failed.', extra_tags='checkout')
                              return redirect('accounts:checkout')

                         order.paymob_order_id = paymob_id
                         order.save()

                         billing_data = {
                              'first_name': fname2,
                              'last_name': lname2,
                              'email': order_email,
                              'phone_number': phonenum,
                              'city': city.name if city else '',
                              'country': 'EG',
                              'street': streetname,
                         }
                         payment_token = get_payment_key(token, paymob_id, amount_cents, billing_data=billing_data)
                         if not payment_token:
                              messages.error(request, 'Paymob payment key failed.', extra_tags='checkout')
                              return redirect('accounts:checkout')

                         iframe_id = PAYMOB_IFRAME_ID
                         paymob_url = f'https://accept.paymob.com/api/acceptance/iframes/{iframe_id}?payment_token={payment_token}'
                         return redirect(paymob_url)
                    return render(request, 'accounts/checkout.html', {
                         'fname2': fname2,
                         'lname2': lname2,
                         'order_email': order_email,
                         'streetname': streetname,
                         'buildingnum': buildingnum,
                         'floornum': floornum,
                         'flatnum': flatnum,
                         'areas': areas,
                         'cities': cities,
                         'order_items': order_items,
                         'cart_total': cart_total,
                         'coupon_discount': coupon_discount,
                         'grand_total': grand_total,
                         'shipping_Cost': shipping_Cost,
                    })
          else:    
               messages.error(request, 'Invalid action.')   
          return redirect('accounts:checkout')

     return render(request, 'accounts/checkout.html', {
          'areas': areas,
          'cities': cities,
          'is_added': is_added,
          'order_items': order_items,
          'cart_total': cart_total,
          'coupon_discount': coupon_discount,
          'grand_total': grand_total,
          'shipping_Cost': shipping_Cost,
     })
          

def order_success(request, order_id):
     order = Order.objects.filter(id=order_id, user=request.user).first()
     if not order:
          messages.error(request, 'Order not found.', extra_tags='checkout')
          return redirect('accounts:cart')

     return render(request, 'accounts/order_success.html', {
          'order': order,
     })


def logout(request):
     if request.user.is_authenticated:
          auth.logout(request)
     return redirect('pages:index')     





def product_favorite(request, product_id):
     if request.user.is_authenticated:
          pro_fav= get_object_or_404(Product, id=product_id)       
          if UserProfile.objects.filter(user=request.user, favorite_products=pro_fav).exists():
               messages.success(request, 'Product already in favorites.')
          else:
               user_profile, created = UserProfile.objects.get_or_create(user=request.user)
               user_profile.favorite_products.add(pro_fav)
               messages.success(request, 'Product added to favorites.')     
      
          

     else:
          messages.error(request, 'You need to be logged in to add products to favorites.')


     return redirect(request.META.get('HTTP_REFERER'))


def show_product_favorite(request):
     context=None
     if request.user.is_authenticated:
          userInfo=UserProfile.objects.get(user=request.user)
          pro=userInfo.favorite_products.all()
          context={
               'products':pro
          }
     else:
          messages.error(request, 'You need to log in.') 

     return render(request, 'products/wishlist.html', context)  


def remove_product_favorite(request, product_id):
     if request.user.is_authenticated:
          pro_fav= get_object_or_404(Product, id=product_id)       
          if UserProfile.objects.filter(user=request.user, favorite_products=pro_fav).exists():
               user_profile = UserProfile.objects.get(user=request.user)
               user_profile.favorite_products.remove(pro_fav)
               messages.success(request, 'Product removed from favorites.')
          else:
               messages.error(request, 'Product not found in favorites.')
     else:
          messages.error(request, 'You need to be logged in to remove products from favorites.')

     return redirect(request.META.get('HTTP_REFERER'))