from django.urls import path
from . import views     

app_name = 'products'

urlpatterns = [
    path('', views.shop, name='shop'),
    path('in/<int:pro_id>/', views.shop_detail, name='shop_detail'),
    path('wishlist/', views.wishlist, name='wishlist'),
    path('shop_by_subcategory/<slug:slug>/', views.shop_by_subcategory, name='shop_by_subcategory'),
]          