from django.contrib import admin
from .models import Coupon, CouponUsage


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_percentage', 'max_discount_amount', 'min_order_value', 'active', 'used_count', 'usage_limit', 'valid_to')
    list_filter = ('active', 'valid_from', 'valid_to')
    list_editable = ('active',)
    search_fields = ('code',)


@admin.register(CouponUsage)
class CouponUsageAdmin(admin.ModelAdmin):
    list_display = ('coupon', 'user', 'discount_amount', 'used_at')
    list_filter = ('used_at',)
    search_fields = ('coupon__code', 'user__username')
