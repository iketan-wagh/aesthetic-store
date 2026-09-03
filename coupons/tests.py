from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from coupons.models import Coupon
from products.models import Category, Product


class CouponTests(TestCase):
    def setUp(self):
        self.coupon = Coupon.objects.create(
            code='NOMA10',
            discount_percentage=10,
            min_order_value=Decimal('499.00'),
            active=True
        )
        self.category = Category.objects.create(name='Drinkware', slug='drinkware')
        self.tumbler = Product.objects.create(
            name='Cloud Reusable Tumbler',
            slug='cloud-reusable-tumbler',
            sku='NOMA-TUM-TEST',
            category=self.category,
            price=Decimal('999.00'),
            stock=10,
            is_active=True
        )

    def test_coupon_discount_calculation(self):
        discount = self.coupon.calculate_discount(Decimal('1000.00'))
        self.assertEqual(discount, Decimal('100.00'))

    def test_apply_coupon_ajax(self):
        # Add item to cart first
        self.client.post(
            reverse('cart:add_to_cart'),
            {'product_id': self.tumbler.id, 'quantity': 1},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )

        # Apply coupon
        response = self.client.post(
            reverse('coupons:apply_coupon'),
            {'code': 'NOMA10'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['coupon_code'], 'NOMA10')
        self.assertEqual(data['discount_amount'], 99.90)
