from django.urls import path
from . import views 

app_name = 'accounts'

urlpatterns = [
    path('cart/', views.cart, name='cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('order-success/<int:order_id>/', views.order_success, name='order_success'),
    path('logout/', views.logout, name='logout'),
    path('product_favorite/<int:product_id>/', views.product_favorite, name='product_favorite'),
    path('show_product_favorite', views.show_product_favorite,name='show_product_favorite'),
    path('remove_product_favorite/<int:product_id>/', views.remove_product_favorite, name='remove_product_favorite'),
]