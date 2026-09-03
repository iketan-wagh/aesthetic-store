from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('', views.cart_view, name='cart_view'),
    path('add/', views.add_to_cart, name='add_to_cart'),
    path('update/', views.update_cart_item, name='update_cart_item'),
    path('remove/', views.remove_from_cart, name='remove_from_cart'),
    path('drawer-data/', views.cart_drawer_data, name='cart_drawer_data'),
]
