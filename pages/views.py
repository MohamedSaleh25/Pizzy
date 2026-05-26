from django.conf import settings
from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import render
from django.db.models import Q
from products.models import Product
# Create your views here.
def index(request):
    # Show products that are either top featured or best seller
    products = Product.objects.filter(Q(istopfeatured=True) | Q(isbestseller=True))
    return render(request, 'pages/index.html', {'products': products})

def about(request):
    return render(request, 'pages/about.html')

def contact_us(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        subject = request.POST.get('msg_subject', '').strip()
        message = request.POST.get('message', '').strip()

        if not name or not email or not subject or not message:
            return HttpResponse('Please fill in all required fields.', status=400)

        full_subject = f'Contact form: {subject}'
        full_message = f'Name: {name}\nEmail: {email}\n\n{message}'

        try:
            send_mail(
                full_subject,
                full_message,
                settings.EMAIL_HOST_USER,
                [settings.CONTACT_EMAIL],
                fail_silently=False,
            )
            return HttpResponse('success')
        except Exception as exc:
            return HttpResponse(f'There was an error sending email: {exc}', status=500)

    return render(request, 'pages/contact-us.html')