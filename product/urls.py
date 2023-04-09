# product/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('products/', views.product_list, name='product-list'),
    path('create/', views.product_create, name='product-create'),
    path('inbound/', views.inbound_create, name='inbound-create'),
    path('outbound/', views.outbound_create, name='outbound-create'),
    path('inventory/<int:pk>', views.product_inventory, name='inventory'),
]
