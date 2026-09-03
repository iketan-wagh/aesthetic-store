from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_home, name='home'),
    path('auth/', views.dashboard_auth_view, name='auth'),
    path('lock/', views.dashboard_lock_view, name='lock'),
    path('orders/', views.dashboard_orders, name='orders'),
    path('orders/<str:order_number>/update-status/', views.dashboard_order_update_status, name='order_update_status'),
    path('orders/<str:order_number>/slip/', views.dashboard_order_slip, name='order_slip'),
    path('inventory/', views.dashboard_inventory, name='inventory'),
    path('inventory/<int:pk>/update-stock/', views.dashboard_product_update_stock, name='product_update_stock'),
    path('customers/', views.dashboard_customers, name='customers'),
    path('coupons/', views.dashboard_coupons, name='coupons'),
]
