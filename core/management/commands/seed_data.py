from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from products.models import Category, Product, ProductImage
from coupons.models import Coupon
from reviews.models import Review
from accounts.models import Address


class Command(BaseCommand):
    help = 'Seeds initial and updated database for Aesthetic Store'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('[INFO] Starting Database Seed & Sync...'))

        # 1. Create Superusers
        ketan_user, _ = User.objects.get_or_create(
            username='ketanwagh',
            defaults={
                'email': 'iketanwagh@gmail.com',
                'first_name': 'Ketan',
                'last_name': 'Wagh',
                'is_staff': True,
                'is_superuser': True
            }
        )
        ketan_user.set_password('Ketan@wagh1')
        ketan_user.is_staff = True
        ketan_user.is_superuser = True
        ketan_user.save()
        self.stdout.write(self.style.SUCCESS('[SUCCESS] Superuser provisioned: ketanwagh / Ketan@wagh1'))

        admin_user, _ = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@aestheticstore.com',
                'first_name': 'Store',
                'last_name': 'Admin',
                'is_staff': True,
                'is_superuser': True
            }
        )
        admin_user.set_password('Ketan@wagh1')
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.save()

        # 2. Categories
        categories_data = [
            {
                'name': 'Drinkware',
                'slug': 'drinkware',
                'tagline': 'Aesthetic hydration rituals',
                'description': 'Elevate your daily water and coffee routine with clean, endlessly reusable vessels.',
                'display_order': 1,
                'is_featured': True
            },
            {
                'name': 'Home & Living',
                'slug': 'home-living',
                'tagline': 'Warmth, mood and conscious calm',
                'description': 'Mindfully crafted accents, natural gemstones, and slow-living essentials for your personal sanctuary.',
                'display_order': 2,
                'is_featured': True
            },
            {
                'name': 'Workspace',
                'slug': 'workspace',
                'tagline': 'Calm, decluttered desks',
                'description': 'Clean lines, organic bamboo, and desk accessories designed to inspire deep focus.',
                'display_order': 3,
                'is_featured': True
            },
            {
                'name': 'Wellness',
                'slug': 'wellness',
                'tagline': 'Everyday grounding rituals',
                'description': 'Simple, beautiful tools for mindful morning routines and natural wellbeing.',
                'display_order': 4,
                'is_featured': True
            },
            {
                'name': 'Everyday Carry',
                'slug': 'everyday-carry',
                'tagline': 'Essentials for life on the go',
                'description': 'Durable, minimal accessories crafted for daily commutes and conscious mobility.',
                'display_order': 5,
                'is_featured': True
            },
            {
                'name': 'Gifting',
                'slug': 'gifting',
                'tagline': 'Thoughtful things for favorite humans',
                'description': 'Eco-conscious gift sets and aesthetics that spark joy.',
                'display_order': 6,
                'is_featured': True
            },
        ]

        Category.objects.filter(slug='new-drops').delete()

        cat_instances = {}
        for cdata in categories_data:
            cat, _ = Category.objects.update_or_create(
                slug=cdata['slug'],
                defaults=cdata
            )
            cat_instances[cdata['slug']] = cat
        self.stdout.write(self.style.SUCCESS(f'[SUCCESS] Synced {len(cat_instances)} Categories.'))

        # 3. User's Active Products & Imagery
        products_data = [
            {
                'name': 'Royal Ornate Pure Copper Water Bottle',
                'slug': 'royal-ornate-pure-copper-water-bottle',
                'sku': 'NOMA-COPPER-ORNATE-001',
                'category': cat_instances['drinkware'],
                'price': Decimal('2199.00'),
                'discount_price': Decimal('1799.00'),
                'stock': 8,
                'short_description': 'A timeless copper bottle with an intricate ornamental finish, designed to bring traditional craftsmanship and everyday wellness into a modern lifestyle.',
                'description': (
                    "Our Royal Ornate Copper Water Bottle features a rich copper body wrapped in an intricate black-and-copper ornamental pattern. "
                    "Its elegant cylindrical silhouette and warm metallic finish make it more than just a water bottle — it's a refined everyday accessory.\n\n"
                    "Inspired by the traditional use of copper vessels, this bottle is designed for storing drinking water while adding a touch of heritage to your daily routine.\n\n"
                    "Whether kept on your work desk, bedside table, dining table, or carried throughout the day, its distinctive design makes it equally suited to personal use and thoughtful gifting.\n\n"
                    "Highlights:\n"
                    "• Copper construction\n"
                    "• Intricate ornamental exterior design\n"
                    "• Premium copper-finish cap\n"
                    "• Tall, elegant cylindrical form\n"
                    "• Suitable for everyday water storage\n"
                    "• Traditional-inspired wellness aesthetic\n"
                    "• Reusable alternative to disposable plastic bottles\n"
                    "• Suitable for home, office and gifting\n\n"
                    "Please note: Traditional wellness practices around storing water in copper vessels are widely known, but this product should not be considered a medical treatment or a substitute for professional medical advice."
                ),
                'badge': 'BESTSELLER',
                'tags': 'Sustainable, Copper, Drinkware, Wellness, Bestseller',
                'materials': 'Copper body with decorative black-and-copper ornamental exterior finish and copper-finish metal cap.',
                'dimensions': 'Height: 22 cm | Diameter: 7 cm | Capacity: 950ml',
                'care_instructions': (
                    "Hand wash with mild soap and water.\n"
                    "Dry thoroughly after washing.\n"
                    "Avoid abrasive scrubbers and harsh chemical cleaners.\n"
                    "Do not use a dishwasher.\n"
                    "Avoid storing highly acidic beverages such as lemon water or fruit juices for extended periods.\n"
                    "To maintain the copper's appearance, use a copper-safe cleaning method when required.\n"
                    "Store completely dry when not in use."
                ),
                'sustainability_notes': 'Reusable copper construction designed for long-term everyday use, helping reduce dependence on disposable plastic water bottles. Copper is also a durable material that can be maintained over time rather than frequently replaced.',
                'packaging_notes': 'Packaged in protective, minimal packaging designed to protect the copper surface and ornamental finish during transit.',
                'lifespan_notes': 'Built to endure for years with simple hand washing and care.',
                'is_featured': True,
                'is_bestseller': True,
                'is_new_drop': False,
                'is_active': True,
                'images': [
                    'products/royal-ornate-pure-copper-water-bottle1.jpeg',
                    'products/royal-ornate-pure-copper-water-bottle3.jpeg',
                    'products/royal-ornate-pure-copper-water-bottle2.jpeg',
                ]
            },
            {
                'name': 'Seven Chakra Gemstone Tree of Life',
                'slug': 'seven-chakra-gemstone-tree-of-life',
                'sku': 'NOMA-HOME-GEMTREE-001',
                'category': cat_instances['home-living'],
                'price': Decimal('999.00'),
                'discount_price': Decimal('699.00'),
                'stock': 10,
                'short_description': 'A vibrant handcrafted gemstone tree inspired by the Tree of Life, bringing color, character, and a meaningful decorative touch to your space.',
                'description': (
                    "A little tree for your space. A lot of character for your home.\n\n"
                    "The Seven Chakra Gemstone Tree of Life is a handcrafted decorative piece featuring colorful natural-looking gemstone chips arranged across delicate golden branches and a sculpted tree trunk.\n\n"
                    "Designed to symbolize growth, balance, and abundance, its colorful branches make it an eye-catching addition to desks, shelves, bedside tables, meditation corners, living rooms, and workspaces.\n\n"
                    "Its compact form also makes it a thoughtful gift for housewarmings, birthdays, festive occasions, and anyone who enjoys meaningful décor inspired by nature and traditional symbolism.\n\n"
                    "Highlights:\n"
                    "• Tree of Life inspired design\n"
                    "• Multicolored gemstone-chip branches\n"
                    "• Hand-wired decorative branches\n"
                    "• Sculpted tree-style trunk\n"
                    "• Decorative gemstone-filled base\n"
                    "• Suitable for home and workspace décor\n"
                    "• Compact statement piece\n"
                    "• Ideal for gifting\n"
                    "• Inspired by chakra and traditional décor symbolism"
                ),
                'badge': 'FEATURED',
                'tags': 'Gemstone, Home Decor, Tree of Life, Chakra, Gifting',
                'materials': 'Natural gemstone chips, decorative metal wire branches, sculpted resin/wood-effect trunk and base.',
                'dimensions': 'Height: 18 cm | Base Width: 6 cm | Weight: 250g',
                'care_instructions': (
                    "Keep indoors and away from prolonged moisture.\n"
                    "Clean gently with a soft, dry cloth.\n"
                    "Avoid dropping or bending the gemstone branches.\n"
                    "Handle the branches carefully when repositioning the tree.\n"
                    "Keep away from harsh cleaning chemicals.\n"
                    "Keep away from prolonged direct sunlight to help preserve the decorative finish."
                ),
                'sustainability_notes': 'Designed as a reusable decorative piece that can be enjoyed for years with proper care. Its nature-inspired design offers a long-lasting alternative to short-lived seasonal décor.',
                'packaging_notes': 'Packed in protective, gift-ready packaging designed to safeguard the delicate gemstone branches and decorative base during delivery.',
                'lifespan_notes': 'Permanent decorative craft piece.',
                'is_featured': True,
                'is_bestseller': False,
                'is_new_drop': True,
                'is_active': True,
                'images': [
                    'products/seven-chakra-gemstone-tree-of-life1.jpeg',
                    'products/seven-chakra-gemstone-tree-of-life2.jpeg',
                    'products/seven-chakra-gemstone-tree-of-life3.jpeg',
                ]
            }
        ]

        # Clean up old placeholder products if present
        allowed_slugs = [p['slug'] for p in products_data]
        Product.objects.exclude(slug__in=allowed_slugs).delete()

        created_products = []
        for pdata in products_data:
            img_list = pdata.pop('images', [])
            prod, _ = Product.objects.update_or_create(
                slug=pdata['slug'],
                defaults=pdata
            )
            
            # Sync product images
            ProductImage.objects.filter(product=prod).delete()
            for idx, img_path in enumerate(img_list):
                ProductImage.objects.create(
                    product=prod,
                    image=img_path,
                    is_primary=(idx == 0),
                    alt_text=f"{prod.name} angle {idx + 1}"
                )
            created_products.append(prod)

        self.stdout.write(self.style.SUCCESS(f'[SUCCESS] Seeded and synced {len(created_products)} active store products.'))

        # 4. Coupons
        noma_coupon, _ = Coupon.objects.get_or_create(
            code='NOMA10',
            defaults={
                'discount_percentage': 10,
                'max_discount_amount': Decimal('500.00'),
                'min_order_value': Decimal('499.00'),
                'active': True,
                'valid_from': timezone.now(),
                'usage_limit': 10000
            }
        )
        self.stdout.write(self.style.SUCCESS(f'[SUCCESS] Seeded Coupon: {noma_coupon.code} (10% OFF)'))
        self.stdout.write(self.style.SUCCESS('[SUCCESS] Database sync completed successfully!'))
