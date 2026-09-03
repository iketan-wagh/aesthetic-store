from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from products.models import Category, Product, ProductImage
from coupons.models import Coupon
from reviews.models import Review
from accounts.models import Address


class Command(BaseCommand):
    help = 'Seeds initial database for NOMA Gen-Z sustainable lifestyle brand'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('[INFO] Starting NOMA Database Seed...'))

        # Create Superusers
        ketan_user, k_created = User.objects.get_or_create(
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

        admin_user, a_created = User.objects.get_or_create(
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

        # Create Demo Customers for reviews
        demo_users = [
            ('ananya_m', 'Ananya', 'Mehta', 'ananya@example.com'),
            ('rohan_v', 'Rohan', 'Verma', 'rohan@example.com'),
            ('kavya_s', 'Kavya', 'Sharma', 'kavya@example.com'),
            ('arjun_d', 'Arjun', 'Deshmukh', 'arjun@example.com'),
            ('tanya_k', 'Tanya', 'Kapoor', 'tanya@example.com'),
        ]
        created_users = []
        for uname, fname, lname, email in demo_users:
            u, created = User.objects.get_or_create(
                username=uname,
                defaults={'first_name': fname, 'last_name': lname, 'email': email}
            )
            if created:
                u.set_password('password123')
                u.save()
                # Create demo address
                Address.objects.get_or_create(
                    user=u,
                    full_name=f"{fname} {lname}",
                    phone="+91 98765 43210",
                    address_line1="Apartment 4B, Emerald Heights",
                    address_line2="12th Main, Indiranagar",
                    city="Bengaluru",
                    state="Karnataka",
                    pincode="560038",
                    is_default=True,
                    address_type="HOME"
                )
            created_users.append(u)

        # 1. Categories
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
                'description': 'Mindfully crafted accents, natural soy scents, and slow-living essentials for your personal sanctuary.',
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
                'description': 'Eco-conscious, Instagram-worthy gift sets and aesthetics that spark joy.',
                'display_order': 6,
                'is_featured': True
            },
            {
                'name': 'New Drops',
                'slug': 'new-drops',
                'tagline': 'Fresh seasonal arrivals',
                'description': 'Our latest limited batches, small-batch ceramics, and curated sustainable swaps.',
                'display_order': 7,
                'is_featured': True
            },
        ]

        cat_instances = {}
        for cdata in categories_data:
            cat, _ = Category.objects.get_or_create(
                slug=cdata['slug'],
                defaults=cdata
            )
            cat_instances[cdata['slug']] = cat
        self.stdout.write(self.style.SUCCESS(f'[SUCCESS] Seeded {len(cat_instances)} Categories.'))

        # 2. Products Data (5 Exact products from prompt)
        products_data = [
            {
                'name': 'Aura Copper Bottle',
                'slug': 'aura-copper-bottle',
                'sku': 'NOMA-BOT-01',
                'category': cat_instances['drinkware'],
                'price': Decimal('1499.00'),
                'discount_price': Decimal('1299.00'),
                'stock': 40,
                'short_description': 'A minimalist copper bottle designed to turn everyday hydration into a beautiful ritual.',
                'description': (
                    'The Aura Copper Bottle brings ancient Ayurvedic water rituals into the contemporary aesthetic home. '
                    'Meticulously spun from pure, high-grade single-source copper with an ultra-matte brushed exterior finish, '
                    'this bottle feels luxurious in the hand and looks striking on any bedside table or desk.\n\n'
                    'Copper naturally infuses your drinking water with trace minerals while remaining 100% plastic-free. '
                    'Featuring an airtight, leakproof silicone-sealed copper cap and a balanced silhouette.'
                ),
                'badge': 'BESTSELLER',
                'tags': 'Sustainable, Bestseller, Everyday, Drinkware',
                'materials': '100% Pure High-Grade Ayurvedic Copper, food-safe leakproof silicone seal',
                'dimensions': '900ml (30.4 fl oz) | Height: 26cm | Base Diameter: 7.2cm | Weight: 280g',
                'care_instructions': 'Hand rinse with warm water and lemon/salt mixture weekly. Never place in microwave or dishwasher. For still water only.',
                'sustainability_notes': 'Single-element metal that is infinitely recyclable. Replaces an estimated 1,400+ single-use plastic bottles over 5 years of daily use.',
                'packaging_notes': '100% plastic-free recycled unbleached kraft box, printed with water-based soy inks.',
                'lifespan_notes': 'Engineered to last for decades. Develops a natural, distinctive patina over time.',
                'is_featured': True,
                'is_bestseller': True,
                'is_new_drop': False,
            },
            {
                'name': 'Copper Water Recharge Balls',
                'slug': 'copper-water-recharge-balls',
                'sku': 'NOMA-WEL-02',
                'category': cat_instances['wellness'],
                'price': Decimal('799.00'),
                'discount_price': None,
                'stock': 65,
                'short_description': 'Reusable copper accessories designed for a thoughtful water-care ritual.',
                'description': (
                    'Turn any existing glass pitcher, carafe, or bedside water bottle into an intentional mineralizing station. '
                    'Our Copper Water Recharge Balls are hand-turned from solid 99.8% pure copper spheres. '
                    'Simply drop them into your daily water vessel overnight to allow subtle, natural copper ionization to infuse your water.\n\n'
                    'Comes as a curated set of 4 solid spheres in an unbleached organic cotton drawstring bag.'
                ),
                'badge': 'NEW',
                'tags': 'Wellness, Reusable, New, Ritual',
                'materials': 'Solid artisan-forged 99.8% pure natural copper',
                'dimensions': 'Set of 4 spheres | 2.5cm diameter each | Total weight: 140g',
                'care_instructions': 'Rinse before first use. Soak for 5 minutes in mild lemon juice or tamarind paste every fortnight to restore natural luster.',
                'sustainability_notes': 'Zero-waste water enhancement. No disposable filter cartridges, no microplastics, and zero recurring waste.',
                'packaging_notes': 'Organic GOTS-certified cotton pouch inside a compostable recycled paperboard tube.',
                'lifespan_notes': 'Indefinite reusable lifespan — solid metal that never degrades.',
                'is_featured': True,
                'is_bestseller': False,
                'is_new_drop': True,
            },
            {
                'name': 'Cloud Reusable Tumbler',
                'slug': 'cloud-reusable-tumbler',
                'sku': 'NOMA-TUM-03',
                'category': cat_instances['drinkware'],
                'price': Decimal('999.00'),
                'discount_price': Decimal('899.00'),
                'stock': 50,
                'short_description': 'A clean, reusable tumbler designed for coffee runs, study sessions and everyday carry.',
                'description': (
                    'The Cloud Reusable Tumbler is sculpted for your favorite iced matcha, hot flat white, or infused water on the move. '
                    'Featuring double-wall vacuum insulation with a cloud-soft matte ceramic-feel powder coat that resists condensation.\n\n'
                    'Fitted with a splash-resistant ergonomic sliding lid that accommodates reusable glass and bamboo straws. '
                    'Fits comfortably into standard cup holders and tote bag pockets.'
                ),
                'badge': 'NOMA_PICK',
                'tags': 'Reusable, Everyday, Gen-Z Pick, Tumbler',
                'materials': '18/8 Pro-Grade Double-Wall Stainless Steel, BPA-free Tritan slider lid',
                'dimensions': '480ml (16 oz) | Height: 17.8cm | Top Diameter: 8.6cm | Weight: 260g',
                'care_instructions': 'Top-rack dishwasher safe lid. Hand-wash body with warm soapy water to preserve soft matte coating.',
                'sustainability_notes': 'Keeps beverages cold for 18 hours or hot for 8 hours. Replaces 400+ single-use coffee cups per year for regular coffee drinkers.',
                'packaging_notes': 'Zero-plastic recycled kraft cylinder with water-based non-toxic inks.',
                'lifespan_notes': 'Built for 5+ years of intense everyday use.',
                'is_featured': True,
                'is_bestseller': True,
                'is_new_drop': False,
            },
            {
                'name': 'Bamboo Desk Edit',
                'slug': 'bamboo-desk-edit',
                'sku': 'NOMA-DSK-04',
                'category': cat_instances['workspace'],
                'price': Decimal('699.00'),
                'discount_price': None,
                'stock': 35,
                'short_description': 'A minimalist bamboo organizer for creating a calmer, cleaner workspace.',
                'description': (
                    'Declutter your creative corner and bring organic warmth to your digital workspace. '
                    'The Bamboo Desk Edit is CNC-machined from single-slab sustainably harvested Moso bamboo, '
                    'featuring custom recessed grooves for your smartphone, fountain pens, sticky notes, and everyday trinkets.\n\n'
                    'Satin plant-oil finish highlights the natural wood grain while soft cork feet prevent desktop scratches.'
                ),
                'badge': 'LIMITED',
                'tags': 'Sustainable, Workspace, Minimal, Bamboo',
                'materials': '100% Sustainably Harvested Moso Bamboo, natural plant-based linseed oil finish, natural cork base pads',
                'dimensions': '24cm Length × 14cm Width × 4.2cm Height | Weight: 320g',
                'care_instructions': 'Wipe clean with a dry or lightly damp cloth. Keep away from direct standing water.',
                'sustainability_notes': 'Moso bamboo reaches maturity in 3-5 years without synthetic fertilizers or heavy machinery. 100% biodegradable.',
                'packaging_notes': 'FSC-certified unbleached cardboard box with paper sealing tape.',
                'lifespan_notes': 'Durable solid bamboo built to endure 10+ years of creative work.',
                'is_featured': True,
                'is_bestseller': False,
                'is_new_drop': False,
            },
            {
                'name': 'Slow Sunday Soy Candle',
                'slug': 'slow-sunday-soy-candle',
                'sku': 'NOMA-CND-05',
                'category': cat_instances['home-living'],
                'price': Decimal('599.00'),
                'discount_price': None,
                'stock': 80,
                'short_description': 'A hand-poured soy wax candle created for slow evenings and cozy spaces.',
                'description': (
                    'Infuse your sanctuary with the grounding notes of amber, hinoki wood, warm cedar, and subtle tonka bean. '
                    'Slow Sunday is hand-poured in small batches using 100% renewable domestic soy wax and lead-free organic cotton wicks.\n\n'
                    'Housed in a reusable matte earthenware ceramic tumbler that can be repurposed as a desktop pen holder or succulent planter once burned.'
                ),
                'badge': 'NEW',
                'tags': 'Home, Relax, Giftable, Soy Wax',
                'materials': '100% Pure Soy Wax, Lead-free unbleached cotton wick, Phthalate-free botanical oils, matte stoneware ceramic vessel',
                'dimensions': '220g (7.8 oz) | 50+ Hours Clean Burn Time | Height: 9cm | Diameter: 7.8cm',
                'care_instructions': 'Trim wick to 6mm before every burn. Allow wax to melt to container edges on first burn to prevent tunneling.',
                'sustainability_notes': 'Clean-burning plant wax with zero petroleum paraffin. Vessel is 100% reusable.',
                'packaging_notes': 'Compostable paperboard box with seed-embedded paper label you can plant in soil.',
                'lifespan_notes': '50+ hours burn time; permanent reusable ceramic cup.',
                'is_featured': True,
                'is_bestseller': False,
                'is_new_drop': True,
            },
        ]

        created_products = []
        for pdata in products_data:
            prod, _ = Product.objects.get_or_create(
                slug=pdata['slug'],
                defaults=pdata
            )
            # Create a sample ProductImage record
            ProductImage.objects.get_or_create(
                product=prod,
                is_primary=True,
                defaults={'alt_text': f"{prod.name} - Studio Aesthetic View"}
            )
            created_products.append(prod)
        self.stdout.write(self.style.SUCCESS(f'[SUCCESS] Seeded {len(created_products)} Products.'))

        # 3. Coupons
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

        # 4. Verified Seed Customer Reviews
        reviews_data = [
            (
                created_products[0], # Aura Copper Bottle
                created_users[0], # Ananya
                5,
                'Genuinely transformed my desk aesthetic',
                'I get compliments on this bottle every single day at my studio. The matte copper finish is so subtle and premium — not tacky or overly shiny. Feels wonderful to drink from!'
            ),
            (
                created_products[0],
                created_users[1], # Rohan
                5,
                'Solid build and zero leaks',
                'Been using it daily for 3 weeks. Water genuinely tastes crisper and cooler in the morning. Great conscious packaging too — 10/10 unboxing vibe.'
            ),
            (
                created_products[1], # Copper Recharge Balls
                created_users[2], # Kavya
                5,
                'Such a clever minimalist idea',
                'Dropped two into my glass bedside pitcher. It makes the everyday routine feel like an intentional ritual. Love the linen pouch.'
            ),
            (
                created_products[2], # Cloud Tumbler
                created_users[3], # Arjun
                5,
                'Replaced my disposable coffee cups completely',
                'Keeps my iced matcha frosty for 6+ hours during work sessions. The texture of the powder coat is so satisfying.'
            ),
            (
                created_products[3], # Bamboo Desk Edit
                created_users[4], # Tanya
                5,
                'Instant Pinterest desk vibe',
                'The bamboo grain is gorgeous and it holds my phone at the perfect angle for video calls. Clean, minimal, zero plastic.'
            ),
            (
                created_products[4], # Slow Sunday Candle
                created_users[0], # Ananya
                5,
                'The coziest evening scent',
                'Hinoki and amber notes are super subtle and comforting, not overwhelming or synthetic. Ceramic jar will make the cutest pencil holder later.'
            ),
        ]

        for prod, usr, rating, title, comment in reviews_data:
            Review.objects.get_or_create(
                product=prod,
                user=usr,
                defaults={
                    'rating': rating,
                    'title': title,
                    'comment': comment,
                    'is_verified_purchase': True,
                    'is_approved': True
                }
            )
        self.stdout.write(self.style.SUCCESS(f'[SUCCESS] Seeded {len(reviews_data)} Customer Reviews.'))
        self.stdout.write(self.style.SUCCESS('[SUCCESS] NOMA Database seeding completed successfully!'))
