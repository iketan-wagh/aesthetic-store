from products.models import Category
from django.conf import settings


def global_context(request):
    categories = Category.objects.all().order_by('display_order', 'name')
    return {
        'nav_categories': categories,
        'brand_name': 'Aesthetic Store',
        'brand_tagline': 'Good things. Better vibes.',
        'brand_philosophy': "Beautiful things shouldn't cost the planet.",
        'announcement_text': 'FREE SHIPPING ON ORDERS ABOVE ₹999 ✦',
        'free_shipping_threshold': getattr(settings, 'FREE_SHIPPING_THRESHOLD', 999),
        'default_shipping_fee': getattr(settings, 'DEFAULT_SHIPPING_FEE', 99),
    }
