from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from decimal import Decimal
from products.models import Product


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='carts')
    session_key = models.CharField(max_length=40, null=True, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart #{self.id} ({self.user.username if self.user else self.session_key})"

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def subtotal(self):
        return sum(item.item_subtotal for item in self.items.all())

    @property
    def free_shipping_threshold(self):
        return getattr(settings, 'FREE_SHIPPING_THRESHOLD', 999)

    @property
    def default_shipping_fee(self):
        return getattr(settings, 'DEFAULT_SHIPPING_FEE', 99)

    @property
    def shipping_fee(self):
        if self.subtotal == 0 or self.subtotal >= self.free_shipping_threshold:
            return Decimal('0.00')
        return Decimal(str(self.default_shipping_fee))

    @property
    def free_shipping_unlocked(self):
        return self.subtotal >= self.free_shipping_threshold

    @property
    def amount_to_free_shipping(self):
        diff = Decimal(str(self.free_shipping_threshold)) - self.subtotal
        return max(Decimal('0.00'), diff)

    @property
    def free_shipping_progress(self):
        if self.free_shipping_threshold == 0:
            return 100
        progress = int((self.subtotal / Decimal(str(self.free_shipping_threshold))) * 100)
        return min(100, max(0, progress))

    @property
    def total(self):
        return self.subtotal + self.shipping_fee


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('cart', 'product')
        ordering = ['added_at']

    def __str__(self):
        return f"{self.quantity}x {self.product.name} in Cart #{self.cart_id}"

    @property
    def unit_price(self):
        return self.product.current_price

    @property
    def item_subtotal(self):
        return self.product.current_price * self.quantity
