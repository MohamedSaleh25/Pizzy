from django.urls import path    
from . import views

app_name = 'profiles'

urlpatterns = [
    path('my_account/', views.my_account, name='my_account'),
    path('my_orders/', views.my_orders, name='orders'),
    path('edit_login/', views.edit_info, name='editlogin'),
    path('edit_addresses', views.editaddresses, name='editaddresses'),
   # path('message/', views.message, name='message'),

]