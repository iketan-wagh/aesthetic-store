from django.contrib import admin
from .models import UserProfile, Address


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'newsletter_subscribed', 'created_at')
    search_fields = ('user__username', 'user__email', 'phone_number')


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'phone', 'city', 'state', 'pincode', 'address_type', 'is_default')
    list_filter = ('address_type', 'is_default', 'state')
    search_fields = ('user__username', 'full_name', 'phone', 'city', 'pincode')
