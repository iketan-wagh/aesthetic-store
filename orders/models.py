import uuid
from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal
from products.models import Product
from coupons.models import Coupon


class Order(models.Model):
    ORDER_STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('PACKED', 'Packed'),
        ('SHIPPED', 'Shipped'),
        ('OUT_FOR_DELIVERY', 'Out for Delivery'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
    )

    PAYMENT_METHOD_CHOICES = (
        ('UPI', 'UPI Instant Pay (Google Pay, PhonePe, Paytm)'),
        ('CARD', 'Credit / Debit Card (Visa, Mastercard, RuPay)'),
        ('NETBANKING', 'Net Banking (All Indian Banks)'),
        ('COD', 'Cash on Delivery'),
        ('ONLINE_TEST', 'Online Payment (Razorpay Simulated Gateway)'),
    )

    PAYMENT_STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('PAID', 'Paid'),
        ('FAILED', 'Failed'),
        ('REFUNDED', 'Refunded'),
    )

    order_number = models.CharField(max_length=50, unique=True, editable=False, db_index=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    
    # Customer Details
    shipping_name = models.CharField(max_length=150)
    shipping_email = models.EmailField()
    shipping_phone = models.CharField(max_length=20)
    
    # Shipping Address
    shipping_address_line1 = models.CharField(max_length=255)
    shipping_address_line2 = models.CharField(max_length=255, blank=True, default='')
    shipping_landmark = models.CharField(max_length=100, blank=True, default='')
    shipping_city = models.CharField(max_length=100)
    shipping_state = models.CharField(max_length=100)
    shipping_pincode = models.CharField(max_length=10)
    
    # Financials
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    shipping_fee = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Coupon
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    coupon_code = models.CharField(max_length=50, blank=True, default='')
    
    # Statuses
    order_status = models.CharField(max_length=25, choices=ORDER_STATUS_CHOICES, default='CONFIRMED')
    payment_method = models.CharField(max_length=25, choices=PAYMENT_METHOD_CHOICES, default='ONLINE_TEST')
    payment_status = models.CharField(max_length=25, choices=PAYMENT_STATUS_CHOICES, default='PENDING')
    payment_id = models.CharField(max_length=100, blank=True, default='')
    
    # Logistics
    tracking_number = models.CharField(max_length=100, blank=True, default='')
    order_notes = models.TextField(blank=True, default='')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{self.order_number} - {self.shipping_name}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = f"NOMA-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    @property
    def full_shipping_address(self):
        parts = [self.shipping_address_line1]
        if self.shipping_address_line2:
            parts.append(self.shipping_address_line2)
        if self.shipping_landmark:
            parts.append(f"Near {self.shipping_landmark}")
        parts.append(f"{self.shipping_city}, {self.shipping_state} - {self.shipping_pincode}")
        return ", ".join(parts)

    @property
    def total_items_count(self):
        return sum(item.quantity for item in self.items.all())


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    product_name = models.CharField(max_length=200)
    product_sku = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity}x {self.product_name} in {self.order.order_number}"

    def save(self, *args, **kwargs):
        self.subtotal = self.price * self.quantity
        super().save(*args, **kwargs)


class PaymentTransaction(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='transactions')
    transaction_id = models.CharField(max_length=100, unique=True)
    gateway = models.CharField(max_length=50, default='Razorpay_Simulated')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50, default='SUCCESS')
    response_payload = models.TextField(blank=True, default='{}')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Txn #{self.transaction_id} ({self.status}) for Order {self.order.order_number}"
