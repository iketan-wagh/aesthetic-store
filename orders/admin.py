from django.contrib import admin
from .models import Order, OrderItem, PaymentTransaction


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'product_name', 'product_sku', 'price', 'quantity', 'subtotal')
    can_delete = False


class PaymentTransactionInline(admin.TabularInline):
    model = PaymentTransaction
    extra = 0
    readonly_fields = ('transaction_id', 'gateway', 'amount', 'status', 'created_at')
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'shipping_name', 'shipping_email', 'total_amount', 'order_status', 'payment_method', 'payment_status', 'created_at')
    list_filter = ('order_status', 'payment_method', 'payment_status', 'created_at')
    list_editable = ('order_status', 'payment_status')
    search_fields = ('order_number', 'shipping_name', 'shipping_email', 'shipping_phone', 'tracking_number')
    readonly_fields = ('order_number', 'subtotal', 'discount_amount', 'shipping_fee', 'total_amount', 'created_at', 'updated_at')
    inlines = [OrderItemInline, PaymentTransactionInline]
    fieldsets = (
        ('Order Reference', {
            'fields': ('order_number', 'user', 'order_status', 'tracking_number', 'created_at', 'updated_at')
        }),
        ('Customer & Shipping', {
            'fields': ('shipping_name', 'shipping_email', 'shipping_phone', 'shipping_address_line1', 'shipping_address_line2', 'shipping_landmark', 'shipping_city', 'shipping_state', 'shipping_pincode', 'order_notes')
        }),
        ('Payment & Financials', {
            'fields': ('payment_method', 'payment_status', 'payment_id', 'subtotal', 'discount_amount', 'coupon', 'coupon_code', 'shipping_fee', 'total_amount')
        }),
    )


@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'order', 'gateway', 'amount', 'status', 'created_at')
    list_filter = ('status', 'gateway')
    search_fields = ('transaction_id', 'order__order_number')
