from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from products.models import Category, Product
from cart.models import Cart, CartItem


class CartTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Home', slug='home')
        self.candle = Product.objects.create(
            name='Slow Sunday Soy Candle',
            slug='slow-sunday-soy-candle',
            sku='NOMA-CND-TEST',
            category=self.category,
            price=Decimal('599.00'),
            stock=15,
            short_description='Soy candle',
            description='Slow evenings',
            is_active=True
        )

    def test_add_to_cart_ajax(self):
        response = self.client.post(
            reverse('cart:add_to_cart'),
            {'product_id': self.candle.id, 'quantity': 1},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['total_items'], 1)
        self.assertEqual(data['subtotal'], 599.00)
        self.assertFalse(data['free_shipping_unlocked'])

    def test_free_shipping_threshold_met(self):
        # Adding 2 candles (2 x 599 = 1198 >= 999)
        self.client.post(
            reverse('cart:add_to_cart'),
            {'product_id': self.candle.id, 'quantity': 2},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        response = self.client.get(reverse('cart:cart_drawer_data'))
        data = response.json()
        self.assertEqual(data['total_items'], 2)
        self.assertEqual(data['subtotal'], 1198.00)
        self.assertTrue(data['free_shipping_unlocked'])
        self.assertEqual(data['shipping'], 0.00)
