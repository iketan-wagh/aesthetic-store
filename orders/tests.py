import json
import hmac
import hashlib
from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from django.conf import settings
from django.contrib.auth.models import User
from products.models import Category, Product
from orders.models import Order, PaymentTransaction


class OrderTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testcustomer', password='password123', email='test@example.com')
        self.category = Category.objects.create(name='Workspace', slug='workspace')
        self.bamboo = Product.objects.create(
            name='Bamboo Desk Edit',
            slug='bamboo-desk-edit',
            sku='NOMA-DSK-TEST',
            category=self.category,
            price=Decimal('699.00'),
            stock=10,
            is_active=True
        )

    def test_unauthenticated_checkout_redirects_to_login(self):
        response = self.client.get(reverse('orders:checkout'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('accounts:login'), response.url)

    def test_razorpay_order_initiation_and_verification(self):
        # Log in customer
        self.client.force_login(self.user)

        # 1. Add item to cart
        self.client.post(
            reverse('cart:add_to_cart'),
            {'product_id': self.bamboo.id, 'quantity': 1},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )

        # 2. Call create_razorpay_order
        init_res = self.client.post(
            reverse('orders:create_razorpay_order'),
            content_type='application/json'
        )
        self.assertEqual(init_res.status_code, 200)
        init_data = init_res.json()
        self.assertEqual(init_data['status'], 'success')
        self.assertTrue('razorpay_order_id' in init_data)
        self.assertEqual(init_data['amount'], 79800)

        # 3. Generate valid test HMAC-SHA256 signature
        order_id = init_data['razorpay_order_id']
        payment_id = 'pay_live_test123456'
        key_secret = getattr(settings, 'RAZORPAY_KEY_SECRET', '')
        msg = f"{order_id}|{payment_id}".encode()
        valid_signature = hmac.new(key_secret.encode(), msg, hashlib.sha256).hexdigest()

        # 4. Call verify_razorpay_payment
        verify_payload = {
            'razorpay_payment_id': payment_id,
            'razorpay_order_id': order_id,
            'razorpay_signature': valid_signature,
            'full_name': 'Ketan Wagh',
            'email': 'ketan@example.com',
            'phone': '+91 9876543210',
            'address_line1': '100 Feet Road',
            'city': 'Bengaluru',
            'state': 'Karnataka',
            'pincode': '560038'
        }
        verify_res = self.client.post(
            reverse('orders:verify_razorpay_payment'),
            data=json.dumps(verify_payload),
            content_type='application/json'
        )
        self.assertEqual(verify_res.status_code, 200)
        verify_data = verify_res.json()
        self.assertEqual(verify_data['status'], 'success')
        
        order = Order.objects.get(order_number=verify_data['order_number'])
        self.assertEqual(order.payment_status, 'PAID')
        self.assertEqual(order.payment_id, payment_id)
        self.assertTrue(PaymentTransaction.objects.filter(transaction_id=payment_id, status='SUCCESS').exists())

        # Stock reduced from 10 to 9
        self.bamboo.refresh_from_db()
        self.assertEqual(self.bamboo.stock, 9)
