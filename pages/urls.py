from django.urls import path
from . import views

app_name = 'pages'

urlpatterns = [
    path('', views.index, name='index'), 
    path('about/', views.about, name='about'), 
    path('contact-us/', views.contact_us, name='contact_us'),  
]