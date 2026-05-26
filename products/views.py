from django.shortcuts import get_object_or_404, render
from products.models import Category, Occasion, Product, SubCategory

# Create your views here.
def shop(request):
    categories = Category.objects.all()      
    products = Product.objects.filter(is_active=True)
    occasions = Occasion.objects.all()

    name=None
    see=None
    s=None
    if 'q' in request.GET:
        name=request.GET['q']
        if name:
            products = products.filter(name__icontains=name)

    if 'see' in request.GET:
        see=request.GET['see']
        if see:
            categories = categories.filter(name__icontains=see)

    if 's' in request.GET:
        s=request.GET['s']
        if s == 'popularity':
            products = products.order_by('-istopfeatured', '-published_date')
        elif s == 'high':
            products = products.order_by('-price', '-published_date')
        elif s == 'low':
            products = products.order_by('price', '-published_date')
        elif s == 'best_selling':
            products = products.order_by('-isbestseller', '-published_date')

    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    selected_occasions = request.GET.getlist('occasion')

    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)
    if selected_occasions:
        products = products.filter(occasion__id__in=selected_occasions).distinct()

    return render(request, 'products/shop.html', {
        'categories': categories,
        'products': products,
        'occasions': occasions,
        'selected_min_price': min_price or '',
        'selected_max_price': max_price or '',
        'selected_occasions': selected_occasions,
        
    })



def shop_by_subcategory(request, slug):
    categories = Category.objects.all()
    subcategory = get_object_or_404(SubCategory, slug=slug)
    products = Product.objects.filter(subcategory=subcategory, is_active=True)
    occasions = Occasion.objects.all()

    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    selected_occasions = request.GET.getlist('occasion')

    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)
    if selected_occasions:
        products = products.filter(occasion__id__in=selected_occasions).distinct()

    return render(request, 'products/shop.html', {
        'categories': categories,
        'subcategory': subcategory,
        'products': products,
        'occasions': occasions,
        'selected_min_price': min_price or '',
        'selected_max_price': max_price or '',
        'selected_occasions': selected_occasions,
    })

def shop_detail(request, pro_id):
    product = get_object_or_404(Product, id=pro_id)
    images = product.images.all()
    products = Product.objects.filter(istopfeatured=True, is_active=True).exclude(id=product.id)[:4]
    return render(request, 'products/shop-detail.html', {'product': product, 'images': images, 'products': products})

def wishlist(request):
     return render(request, 'products/wishlist.html')   




