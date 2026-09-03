from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from products.models import Product, Category
from reviews.models import Review


def home(request):
    featured_products = Product.objects.filter(is_active=True, is_featured=True).select_related('category').prefetch_related('images', 'reviews')
    new_drops = Product.objects.filter(is_active=True).select_related('category').prefetch_related('images', 'reviews').order_by('-is_new_drop', '-created_at')[:4]
    bestsellers = Product.objects.filter(is_active=True, is_bestseller=True).select_related('category').prefetch_related('images', 'reviews')[:4]
    if not bestsellers.exists():
        bestsellers = Product.objects.filter(is_active=True).select_related('category').prefetch_related('images', 'reviews')[:4]
        
    categories = Category.objects.all().order_by('display_order')
    reviews = Review.objects.filter(is_approved=True).select_related('product', 'user')[:6]

    context = {
        'featured_products': featured_products,
        'new_drops': new_drops,
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
            'message': 'Welcome to Aesthetic Store! Keep an eye on your inbox for quiet drops and secret edits.'
        })
    return JsonResponse({
        'status': 'error',
        'message': 'Please enter a valid email address.'
    }, status=400)


def robots_txt(request):
    lines = [
        "User-agent: *",
        "Disallow: /admin/",
        "Disallow: /account/",
        "Disallow: /orders/checkout/",
        "Sitemap: " + request.build_absolute_uri('/sitemap.xml')
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")


def sitemap_xml(request):
    products = Product.objects.filter(is_active=True)
    categories = Category.objects.all()
    
    xml = ['<?xml version="1.0" encoding="UTF-8"?>']
    xml.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
    
    # Static pages
    for path in ['', '/shop/', '/our-story/', '/sustainable-living/', '/faq/', '/contact/']:
        url = request.build_absolute_uri(path)
        xml.append(f'  <url><loc>{url}</loc><changefreq>weekly</changefreq><priority>0.8</priority></url>')
        
    # Categories
    for cat in categories:
        url = request.build_absolute_uri(f'/shop/?category={cat.slug}')
        xml.append(f'  <url><loc>{url}</loc><changefreq>weekly</changefreq><priority>0.7</priority></url>')

    # Products
    for p in products:
        url = request.build_absolute_uri(p.get_absolute_url())
        xml.append(f'  <url><loc>{url}</loc><changefreq>daily</changefreq><priority>0.9</priority></url>')
        
    xml.append('</urlset>')
    return HttpResponse("\n".join(xml), content_type="application/xml")


def error_404(request, exception=None):
    return render(request, 'core/404.html', status=404)


def error_500(request):
    return render(request, 'core/500.html', status=500)


def error_403(request, exception=None):
    return render(request, 'core/403.html', status=403)
