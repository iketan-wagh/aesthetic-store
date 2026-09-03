from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.shop, name='shop'),
    path('category/', views.category_fallback_redirect, name='category_fallback'),
    path('category/<slug:slug>/', views.category_detail, name='category_detail'),
    path('product/', views.product_fallback_redirect, name='product_fallback'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('api/search/', views.search_api, name='search_api'),
]
