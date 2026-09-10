from django.test import TestCase
from django.urls import reverse
from products.models import Category, Product


class CoreAndSEOTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name='Drinkware',
            slug='drinkware',
            tagline='Pure hydration essentials'
        )
        self.product = Product.objects.create(
            name='Royal Ornate Pure Copper Water Bottle',
            slug='royal-ornate-pure-copper-water-bottle',
            sku='NOMA-TEST-01',
            category=self.category,
            price=2199.00,
            discount_price=1799.00,
            short_description='Pure copper bottle with royal pattern.',
            is_active=True
        )

    def test_robots_txt(self):
        response = self.client.get('/robots.txt')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/plain; charset=utf-8')
        content = response.content.decode('utf-8')
        self.assertIn('User-agent: *', content)
        self.assertIn('Disallow: /admin/', content)
        self.assertIn('Disallow: /orders/checkout/', content)
        self.assertIn('Sitemap: http://testserver/sitemap.xml', content)

    def test_sitemap_xml(self):
        response = self.client.get('/sitemap.xml')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/xml; charset=utf-8')
        content = response.content.decode('utf-8')
        self.assertIn('<urlset', content)
        self.assertIn('http://testserver/', content)
        self.assertIn('http://testserver/shop/', content)
        self.assertIn('http://testserver/shop/?category=drinkware', content)
        self.assertIn('http://testserver/shop/product/royal-ornate-pure-copper-water-bottle/', content)
        self.assertIn('<image:image>', content)

    def test_core_pages_status_and_seo(self):
        pages = [
            'core:home',
            'core:our_story',
            'core:sustainable_living',
            'core:faq',
            'core:contact',
            'core:shipping_policy',
            'core:returns_policy',
            'core:privacy_policy',
            'core:terms_conditions',
        ]
        for page_name in pages:
            url = reverse(page_name)
            res = self.client.get(url)
            self.assertEqual(res.status_code, 200, f"Page {page_name} failed with status {res.status_code}")
            # Ensure title tag and meta tags exist
            self.assertContains(res, '<title>')
            self.assertContains(res, 'House of Aesthetics')
            self.assertContains(res, 'meta name="description"')
            self.assertContains(res, 'rel="canonical"')
            self.assertContains(res, 'application/ld+json')

    def test_product_detail_schema_and_meta(self):
        url = self.product.get_absolute_url()
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, '"@type": "Product"')
        self.assertContains(res, '"Royal Ornate Pure Copper Water Bottle"')
        self.assertContains(res, '"@type": "BreadcrumbList"')
        self.assertContains(res, 'og:type" content="product"')
