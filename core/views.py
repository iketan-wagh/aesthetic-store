from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from products.models import Product, Category
from reviews.models import Review


def home(request):
    featured_products = Product.objects.filter(is_active=True, is_featured=True).select_related('category').prefetch_related('images', 'reviews')
    bestsellers = Product.objects.filter(is_active=True, is_bestseller=True).select_related('category').prefetch_related('images', 'reviews')[:4]
    if not bestsellers.exists():
        bestsellers = Product.objects.filter(is_active=True).select_related('category').prefetch_related('images', 'reviews')[:4]
        
    categories = Category.objects.exclude(slug='new-drops').order_by('display_order')
    reviews = Review.objects.filter(is_approved=True).select_related('product', 'user')[:6]

    context = {
        'featured_products': featured_products,
        'bestsellers': bestsellers,
        'categories': categories,
        'reviews': reviews,
    }
    return render(request, 'core/home.html', context)


def our_story(request):
    return render(request, 'core/our_story.html')


def sustainable_living(request):
    return render(request, 'core/sustainable_living.html')


def faq(request):
    return render(request, 'core/faq.html')


def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        return render(request, 'core/contact.html', {'success': True, 'name': name})
    return render(request, 'core/contact.html')


def shipping_policy(request):
    return render(request, 'core/shipping_policy.html')


def returns_policy(request):
    return render(request, 'core/returns_policy.html')


def privacy_policy(request):
    return render(request, 'core/privacy_policy.html')


def terms_conditions(request):
    return render(request, 'core/terms_conditions.html')


@require_POST
def newsletter_subscribe(request):
    email = request.POST.get('email', '').strip()
    if email and '@' in email:
        return JsonResponse({
            'status': 'success',
            'message': 'Welcome to House of Aesthetics! Keep an eye on your inbox for quiet drops and secret edits.'
        })
    return JsonResponse({
        'status': 'error',
        'message': 'Please enter a valid email address.'
    }, status=400)


def robots_txt(request):
    sitemap_url = request.build_absolute_uri('/sitemap.xml')
    lines = [
        "User-agent: *",
        "Allow: /",
        "Allow: /shop/",
        "Allow: /our-story/",
        "Allow: /sustainable-living/",
        "Allow: /faq/",
        "Allow: /contact/",
        "Allow: /shipping-policy/",
        "Allow: /returns-policy/",
        "Allow: /privacy-policy/",
        "Allow: /terms/",
        "Allow: /static/",
        "Allow: /media/",
        "",
        "# Disallow private customer and transactional endpoints",
        "Disallow: /admin/",
        "Disallow: /account/",
        "Disallow: /cart/",
        "Disallow: /wishlist/",
        "Disallow: /orders/checkout/",
        "Disallow: /orders/verify/",
        "Disallow: /dashboard/",
        "Disallow: /api/",
        "",
        "# Host and Sitemap declaration",
        f"Sitemap: {sitemap_url}",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain; charset=utf-8")


def sitemap_xml(request):
    products = Product.objects.filter(is_active=True).select_related('category').prefetch_related('images')
    categories = Category.objects.all()
    
    xml = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"',
        '        xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">',
    ]
    
    # 1. Homepage (Top Priority)
    home_url = request.build_absolute_uri('/')
    xml.append('  <url>')
    xml.append(f'    <loc>{home_url}</loc>')
    xml.append('    <changefreq>daily</changefreq>')
    xml.append('    <priority>1.0</priority>')
    xml.append('  </url>')
    
    # 2. Main Store Catalog
    shop_url = request.build_absolute_uri('/shop/')
    xml.append('  <url>')
    xml.append(f'    <loc>{shop_url}</loc>')
    xml.append('    <changefreq>daily</changefreq>')
    xml.append('    <priority>0.9</priority>')
    xml.append('  </url>')
    
    # 3. Category Landing Pages
    for cat in categories:
        cat_url = request.build_absolute_uri(f'/shop/?category={cat.slug}')
        xml.append('  <url>')
        xml.append(f'    <loc>{cat_url}</loc>')
        xml.append('    <changefreq>weekly</changefreq>')
        xml.append('    <priority>0.8</priority>')
        xml.append('  </url>')

    # 4. Product Detail Pages with Rich Google Image Sitemap Tags
    for p in products:
        prod_url = request.build_absolute_uri(p.get_absolute_url())
        last_mod = p.updated_at.strftime('%Y-%m-%d')
        xml.append('  <url>')
        xml.append(f'    <loc>{prod_url}</loc>')
        xml.append(f'    <lastmod>{last_mod}</lastmod>')
        xml.append('    <changefreq>daily</changefreq>')
        xml.append('    <priority>0.9</priority>')
        
        # Add primary image
        img_url = request.build_absolute_uri(p.primary_image_url)
        xml.append('    <image:image>')
        xml.append(f'      <image:loc>{img_url}</image:loc>')
        xml.append(f'      <image:title>{p.name} - House of Aesthetics</image:title>')
        xml.append(f'      <image:caption>{p.short_description}</image:caption>')
        xml.append('    </image:image>')
        
        # Add gallery images if any
        for gallery_img in p.images.all()[:3]:
            g_url = request.build_absolute_uri(gallery_img.image_url)
            xml.append('    <image:image>')
            xml.append(f'      <image:loc>{g_url}</image:loc>')
            xml.append(f'      <image:title>{p.name} detail view</image:title>')
            xml.append('    </image:image>')
            
        xml.append('  </url>')

    # 5. High-Value Editorial & Content Pages
    content_pages = [
        ('/our-story/', '0.8', 'monthly'),
        ('/sustainable-living/', '0.8', 'monthly'),
        ('/faq/', '0.7', 'monthly'),
        ('/contact/', '0.7', 'monthly'),
        ('/shipping-policy/', '0.5', 'yearly'),
        ('/returns-policy/', '0.5', 'yearly'),
        ('/privacy-policy/', '0.4', 'yearly'),
        ('/terms/', '0.4', 'yearly'),
    ]
    for path, priority, freq in content_pages:
        page_url = request.build_absolute_uri(path)
        xml.append('  <url>')
        xml.append(f'    <loc>{page_url}</loc>')
        xml.append(f'    <changefreq>{freq}</changefreq>')
        xml.append(f'    <priority>{priority}</priority>')
        xml.append('  </url>')
        
    xml.append('</urlset>')
    return HttpResponse("\n".join(xml), content_type="application/xml; charset=utf-8")


def error_404(request, exception=None):
    return render(request, 'core/404.html', status=404)


def error_500(request):
    return render(request, 'core/500.html', status=500)


def error_403(request, exception=None):
    return render(request, 'core/403.html', status=403)
