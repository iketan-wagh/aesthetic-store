from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from products.models import Category, Product


class ProductCatalogTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name='Drinkware',
            slug='drinkware',
            tagline='Aesthetic hydration rituals'
        )
        self.product = Product.objects.create(
            name='Aura Copper Bottle',
            slug='aura-copper-bottle',
            sku='NOMA-BOT-TEST',
            category=self.category,
            price=Decimal('1499.00'),
            discount_price=Decimal('1299.00'),
            stock=20,
            short_description='Minimal copper bottle',
            description='Detailed description',
            badge='BESTSELLER',
            tags='Sustainable, Bestseller, Everyday',
            is_active=True
        )

    def test_product_pricing_and_discounts(self):
        self.assertTrue(self.product.has_discount)
        self.assertEqual(self.product.current_price, Decimal('1299.00'))
        self.assertEqual(self.product.discount_percent, 13)
        self.assertTrue(self.product.in_stock)

    def test_shop_view(self):
        response = self.client.get(reverse('products:shop'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Aura Copper Bottle')

    def test_product_detail_view(self):
        response = self.client.get(reverse('products:product_detail', kwargs={'slug': self.product.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Aura Copper Bottle')
        self.assertContains(response, '1299')

    def test_search_api(self):
        response = self.client.get(reverse('products:search_api') + '?q=Aura')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['count'], 1)
        self.assertEqual(data['results'][0]['name'], 'Aura Copper Bottle')
