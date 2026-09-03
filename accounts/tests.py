from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from django.core import mail
from orders.models import Order
from accounts.models import Address


class AccountSecurityTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='alice', password='password123', email='alice@example.com')
        self.user2 = User.objects.create_user(username='bob', password='password123', email='bob@example.com')
        
        self.alice_address = Address.objects.create(
            user=self.user1,
            full_name='Alice Wonderland',
            phone='+91 9988776655',
            address_line1='100 Alice Road',
            city='Bengaluru',
            state='Karnataka',
            pincode='560001'
        )

        self.alice_order = Order.objects.create(
            user=self.user1,
            order_number='AST-ALICE-1234',
            shipping_name='Alice Wonderland',
            shipping_email='alice@example.com',
            shipping_phone='+91 9988776655',
            shipping_address_line1='100 Alice Road',
            shipping_city='Bengaluru',
            shipping_state='Karnataka',
            shipping_pincode='560001',
            subtotal=999,
            shipping_fee=0,
            discount_amount=0,
            total_amount=999,
            payment_method='ONLINE_TEST',
            payment_status='PAID',
            order_status='CONFIRMED'
        )

    def test_profile_requires_login(self):
        response = self.client.get(reverse('accounts:profile'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue('/account/login/' in response.url)

    def test_profile_orders_tab(self):
        self.client.login(username='alice', password='password123')
        response = self.client.get(reverse('accounts:profile') + '?tab=orders')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'AST-ALICE-1234')
        self.assertContains(response, 'View Receipt')

    def test_cross_user_address_access_denied(self):
        self.client.login(username='bob', password='password123')
        response = self.client.get(reverse('accounts:address_edit', kwargs={'pk': self.alice_address.pk}))
        self.assertEqual(response.status_code, 404)

    def test_cross_user_order_detail_access_denied(self):
        self.client.login(username='bob', password='password123')
        response = self.client.get(reverse('orders:order_detail', kwargs={'order_number': self.alice_order.order_number}))
        self.assertEqual(response.status_code, 302)
        self.assertTrue('/account/login/' in response.url or response.url == '/')

    def test_unauthenticated_order_detail_access_denied(self):
        response = self.client.get(reverse('orders:order_detail', kwargs={'order_number': self.alice_order.order_number}))
        self.assertEqual(response.status_code, 302)

    def test_welcome_email_sent_on_registration(self):
        # Register a brand new user
        reg_data = {
            'username': 'riya_sharma',
            'first_name': 'Riya',
            'last_name': 'Sharma',
            'email': 'riya@example.com',
            'password': 'StrongPassword123!',
            'password2': 'StrongPassword123!',
            'newsletter': True,
        }
        response = self.client.post(reverse('accounts:register'), data=reg_data, follow=True)
        self.assertEqual(response.status_code, 200)
        
        self.assertTrue(User.objects.filter(username='riya_sharma').exists())
        
        self.assertEqual(len(mail.outbox), 1)
        sent_email = mail.outbox[0]
        self.assertEqual(sent_email.to, ['riya@example.com'])
        self.assertIn('Welcome to Aesthetic Store', sent_email.subject)
        self.assertIn('AESTHETIC10', sent_email.body)

    def test_google_login_flow_and_account_creation(self):
        # 1. Access Google Login Endpoint
        res = self.client.get(reverse('accounts:google_login'))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'Sign in with Google')

        # 2. Complete Google OAuth Callback with new Google User
        cb_res = self.client.post(
            reverse('accounts:google_callback'),
            data={'email': 'tanya_google@example.com', 'first_name': 'Tanya'},
            follow=True
        )
        self.assertEqual(cb_res.status_code, 200)
        
        # User is created and logged in
        new_user = User.objects.get(email='tanya_google@example.com')
        self.assertEqual(new_user.first_name, 'Tanya')
        self.assertEqual(int(self.client.session['_auth_user_id']), new_user.pk)

        # Welcome email is dispatched to Google user too
        google_welcome_email = [e for e in mail.outbox if 'tanya_google@example.com' in e.to]
        self.assertEqual(len(google_welcome_email), 1)
        self.assertIn('AESTHETIC10', google_welcome_email[0].body)
