from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from decimal import Decimal


class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True, db_index=True)
    discount_percentage = models.PositiveIntegerField(help_text="Percentage discount (e.g. 10 for 10% off)")
    max_discount_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Optional maximum discount cap in ₹")
    min_order_value = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), help_text="Minimum cart subtotal in ₹ to apply coupon")
    valid_from = models.DateTimeField(default=timezone.now)
    valid_to = models.DateTimeField(null=True, blank=True)
    active = models.BooleanField(default=True)
    usage_limit = models.PositiveIntegerField(default=5000)
    used_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.code} ({self.discount_percentage}% OFF)"

    def is_valid(self, subtotal=Decimal('0.00')):
        now = timezone.now()
        if not self.active:
            return False, "This coupon is no longer active."
        if self.valid_to and now > self.valid_to:
            return False, "This coupon has expired."
        if self.used_count >= self.usage_limit:
            return False, "This coupon usage limit has been reached."
        if subtotal < self.min_order_value:
            return False, f"Minimum order value of ₹{self.min_order_value} required for this coupon."
        return True, "Valid coupon"

    def calculate_discount(self, subtotal):
        if subtotal <= 0:
            return Decimal('0.00')
        raw_discount = (Decimal(str(self.discount_percentage)) / Decimal('100')) * subtotal
        if self.max_discount_amount and raw_discount > self.max_discount_amount:
            return self.max_discount_amount
        return round(raw_discount, 2)


class CouponUsage(models.Model):
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, related_name='usages')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2)
    used_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.coupon.code} used on {self.used_at.strftime('%Y-%m-%d')}"
