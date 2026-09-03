import json
from decimal import Decimal
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from orders.models import Order
from products.models import Product, Category


class DashboardSecurityAndFunctionalityTests(TestCase):
    def setUp(self):
        self.staff_user = User.objects.create_superuser(username='admin_staff', password='staffpassword123', email='admin@aestheticstore.com')
        self.normal_user = User.objects.create_user(username='normal_customer', password='customerpass123', email='customer@example.com')

        self.category = Category.objects.create(name='Wellness', slug='wellness')
        self.candle = Product.objects.create(
            name='Soy Candle Edit',
            slug='soy-candle-edit',
            sku='AST-CNDL-01',
            category=self.category,
            price=Decimal('899.00'),
            stock=12,
            is_active=True
        )

        self.order = Order.objects.create(
            user=self.normal_user,
            order_number='AST-ORD-9988',
            shipping_name='Rohan Verma',
            shipping_email='rohan@example.com',
            shipping_phone='+91 9988776655',
            shipping_address_line1='Flat 402, Lotus Apartments',
            shipping_city='Mumbai',
            shipping_state='Maharashtra',
            shipping_pincode='400001',
            subtotal=899,
            shipping_fee=0,
            discount_amount=0,
            total_amount=899,
            payment_method='ONLINE_TEST',
            payment_status='PAID',
            order_status='CONFIRMED'
        )

    def unlock_dashboard_session(self):
        """Helper to authenticate staff and unlock dashboard session via password gate."""
        self.client.login(username='admin_staff', password='staffpassword123')
        self.client.post(reverse('dashboard:auth'), data={'password': 'staffpassword123'}, follow=True)

    def test_non_staff_cannot_access_dashboard(self):
        # 1. Unauthenticated user redirects to auth gate
        res = self.client.get(reverse('dashboard:home'))
        self.assertEqual(res.status_code, 302)
        self.assertIn('/dashboard/auth/', res.url)

        # 2. Normal customer logged in is denied access
        self.client.login(username='normal_customer', password='customerpass123')
        res = self.client.get(reverse('dashboard:home'))
        self.assertEqual(res.status_code, 302)
        self.assertEqual(res.url, '/')

    def test_staff_must_pass_password_gate(self):
        # Staff is logged in, but has not entered dashboard password yet
        self.client.login(username='admin_staff', password='staffpassword123')
        res = self.client.get(reverse('dashboard:home'))
        self.assertEqual(res.status_code, 302)
        self.assertIn('/dashboard/auth/', res.url)

        # Entering wrong password fails
        fail_res = self.client.post(reverse('dashboard:auth'), data={'password': 'wrongpassword'})
        self.assertEqual(fail_res.status_code, 200)
        self.assertContains(fail_res, 'Incorrect admin password')

        # Entering correct password succeeds and grants access
        success_res = self.client.post(reverse('dashboard:auth'), data={'password': 'staffpassword123'}, follow=True)
        self.assertEqual(success_res.status_code, 200)
        self.assertContains(success_res, 'Operations Overview')

    def test_staff_can_lock_dashboard(self):
        self.unlock_dashboard_session()

        # Lock session
        lock_res = self.client.get(reverse('dashboard:lock'), follow=True)
        self.assertEqual(lock_res.status_code, 200)

        # Attempting to access dashboard again redirects to auth gate
        res = self.client.get(reverse('dashboard:home'))
        self.assertEqual(res.status_code, 302)
        self.assertIn('/dashboard/auth/', res.url)

    def test_staff_order_search_by_address_and_phone(self):
        self.unlock_dashboard_session()

        # Search by City
        search_res = self.client.get(reverse('dashboard:orders') + '?q=Mumbai')
        self.assertEqual(search_res.status_code, 200)
        self.assertContains(search_res, 'AST-ORD-9988')

        # Search by Phone
        phone_res = self.client.get(reverse('dashboard:orders') + '?q=9988776655')
        self.assertEqual(phone_res.status_code, 200)
        self.assertContains(phone_res, 'AST-ORD-9988')

    def test_staff_order_status_update(self):
        self.unlock_dashboard_session()

        update_payload = {
            'order_status': 'SHIPPED',
            'tracking_number': 'BLUEDART-889900'
        }
        res = self.client.post(
            reverse('dashboard:order_update_status', kwargs={'order_number': self.order.order_number}),
            data=json.dumps(update_payload),
            content_type='application/json',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(res.status_code, 200)
        self.order.refresh_from_db()
        self.assertEqual(self.order.order_status, 'SHIPPED')
        self.assertEqual(self.order.tracking_number, 'BLUEDART-889900')

    def test_staff_inventory_stock_update(self):
        self.unlock_dashboard_session()

        stock_payload = {'stock': 25}
        res = self.client.post(
            reverse('dashboard:product_update_stock', kwargs={'pk': self.candle.pk}),
            data=json.dumps(stock_payload),
            content_type='application/json'
        )
        self.assertEqual(res.status_code, 200)
        self.candle.refresh_from_db()
        self.assertEqual(self.candle.stock, 25)
