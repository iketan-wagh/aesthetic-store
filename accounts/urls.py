from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('google/login/', views.google_login_view, name='google_login'),
    path('google/callback/', views.google_callback_view, name='google_callback'),
    path('', views.profile_view, name='profile'),
    path('address/new/', views.address_create, name='address_create'),
    path('address/<int:pk>/edit/', views.address_edit, name='address_edit'),
    path('address/<int:pk>/delete/', views.address_delete, name='address_delete'),
    path('address/<int:pk>/default/', views.address_set_default, name='address_set_default'),
]
