from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('checkout/', views.checkout_view, name='checkout'),
    path('process-checkout/', views.process_checkout, name='process_checkout'),
    path('razorpay/create/', views.create_razorpay_order, name='create_razorpay_order'),
    path('razorpay/verify/', views.verify_razorpay_payment, name='verify_razorpay_payment'),
    path('success/<str:order_number>/', views.order_success, name='order_success'),
    path('detail/<str:order_number>/', views.order_detail, name='order_detail'),
    path('detail/<str:order_number>/receipt/', views.order_detail, name='detail'),
]
