from django.shortcuts import redirect, render
from accounts.models import UserProfile, Area, City
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from orders.models import Order

# Create your views here.
def my_account(request):
    return render(request, 'profiles/my-account.html')


def my_orders(request):
    if request.user.is_anonymous:
        messages.error(request, 'Please log in to see your orders.')
        return redirect('profiles:my_account')

    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'profiles/my-orders.html', {
        'orders': orders,
    })


def signin(request):
    return render(request, 'accounts/signin.html')

def edit_info(request):
    if request.user.is_anonymous:
        context = {
            'first_name': '',
            'last_name': '',
            'edit_email': '',
            'password': '',
            'phone_number': '',
        }
        return render(request, 'profiles/editlogin.html', context)
    
    userprofile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST' and 'btnsave' in request.POST:
        first_name = request.POST.get('editFirstName', '')
        last_name = request.POST.get('editLastName', '')
        phone_number = request.POST.get('edit_phone', '')
        current_password = request.POST.get('current_password', '')
        new_password = request.POST.get('new_password', '').strip()


        
            #messages.error(request, 'Current password is incorrect.')
            #return redirect('profiles:editlogin')
     
        request.user.first_name = first_name
        request.user.last_name = last_name
        userprofile.phone_number = phone_number

        if new_password:
            if request.user.check_password(current_password):
                request.user.set_password(new_password)
                request.user.save()
                update_session_auth_hash(request, request.user)
                
            else:
                messages.error(request, 'Current password is incorrect. Please try again.')
                return redirect('profiles:editlogin')
        
        
        else:
            request.user.save()

        
        userprofile.save()
        messages.success(request, 'Your information has been updated successfully.')
        return redirect('profiles:editlogin')
    
    # GET request
    context = {
        'first_name': request.user.first_name,
        'last_name': request.user.last_name,
        'edit_email': request.user.email,
        'phone_number': userprofile.phone_number,
    }
    return render(request, 'profiles/editlogin.html', context)   
                

            
def editaddresses(request):
    if request.user.is_anonymous:
        context = {
            'city': '',
            'area': '',
            'streetname': '',
            'buildingnum': '',
            'floornum': '',
            'flatnum': '',
            'areas': Area.objects.all(),
            'cities': City.objects.all(),
        }
        return render(request, 'profiles/editaddresses.html', context)
    
    userprofile, created = UserProfile.objects.get_or_create(user=request.user)
    areas = Area.objects.all()
    cities = City.objects.all()

    if request.method == 'POST' and 'btnedit' in request.POST:
        city_id = request.POST.get('city')
        area_id = request.POST.get('area')
        streetname = request.POST.get('streetname', '')
        buildingnum = request.POST.get('buildingnum', '')
        floornum = request.POST.get('floornum', '')
        flatnum = request.POST.get('flatnum', '')

        # Validate city and area are numeric
        try:
            city_id = int(city_id) if city_id else None
            area_id = int(area_id) if area_id else None
        except (ValueError, TypeError):
            city_id = None
            area_id = None

        city = City.objects.filter(id=city_id).first() if city_id else None
        area = Area.objects.filter(id=area_id).first() if area_id else None

        userprofile.city = city
        userprofile.area = area
        userprofile.street_name = streetname
        userprofile.building_number = int(buildingnum) if buildingnum.isdigit() else None
        userprofile.floor_number = int(floornum) if floornum.isdigit() else None
        userprofile.flat_number = int(flatnum) if flatnum.isdigit() else None
        userprofile.save()

        messages.success(request, 'Your address has been updated successfully.')
        context = {
            'city': city,
            'area': area,
            'streetname': streetname,
            'buildingnum': buildingnum,
            'floornum': floornum,
            'flatnum': flatnum,
            'areas': areas,
            'cities': cities,
        }
        return render(request, 'profiles/editaddresses.html', context)

    # GET request
    context = {
        'city': userprofile.city,
        'area': userprofile.area,
        'streetname': userprofile.street_name,
        'buildingnum': userprofile.building_number,
        'floornum': userprofile.floor_number,
        'flatnum': userprofile.flat_number,
        'areas': areas,
        'cities': cities,
    }
    return render(request, 'profiles/editaddresses.html', context)



