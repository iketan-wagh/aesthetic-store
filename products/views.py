from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, F
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from .models import Product, Category
from reviews.models import Review


def shop(request):
    products = Product.objects.filter(is_active=True).select_related('category').prefetch_related('images', 'reviews')
    categories = Category.objects.all().order_by('display_order')

    # Category Filter
    selected_category_slug = request.GET.get('category', '').strip()
    selected_category = None
    if selected_category_slug and selected_category_slug != 'all':
        selected_category = Category.objects.filter(slug=selected_category_slug).first()
        if selected_category:
            products = products.filter(category=selected_category)

    # Search query
    query = request.GET.get('q', '').strip()
    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(short_description__icontains=query) |
            Q(tags__icontains=query) |
            Q(category__name__icontains=query)
        ).distinct()

    # Price filter
    min_price = request.GET.get('min_price', '').strip()
    max_price = request.GET.get('max_price', '').strip()
    if min_price:
        try:
            products = products.filter(price__gte=float(min_price))
        except ValueError:
            pass
    if max_price:
        try:
            products = products.filter(price__lte=float(max_price))
        except ValueError:
            pass

    # Availability filter
    in_stock_only = request.GET.get('in_stock', '').strip()
    if in_stock_only in ['true', '1', 'yes']:
        products = products.filter(stock__gt=0)

    # Sorting
    sort_by = request.GET.get('sort', 'featured')
    if sort_by == 'newest':
        products = products.order_by('-created_at')
    elif sort_by == 'price_low_high':
        products = products.order_by('price')
    elif sort_by == 'price_high_low':
        products = products.order_by('-price')
    elif sort_by == 'bestselling':
        products = products.order_by('-is_bestseller', '-view_count')
    else: # Default: featured
        products = products.order_by('-is_featured', '-created_at')

    # Pagination
    total_count = products.count()
    paginator = Paginator(products, 12)
    page = request.GET.get('page', 1)
    try:
        products_page = paginator.page(page)
    except (PageNotAnInteger, EmptyPage):
        products_page = paginator.page(1)

    context = {
        'products': products_page,
        'categories': categories,
        'selected_category': selected_category,
        'selected_category_slug': selected_category_slug,
        'sort_by': sort_by,
        'query': query,
        'min_price': min_price,
        'max_price': max_price,
        'in_stock_only': in_stock_only,
        'total_count': total_count,
    }
    return render(request, 'products/shop.html', context)


def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    return redirect(f"/shop/?category={category.slug}")


def product_detail(request, slug):
    product = get_object_or_404(Product.objects.select_related('category'), slug=slug, is_active=True)
    
    # Increment view count
    Product.objects.filter(pk=product.pk).update(view_count=F('view_count') + 1)
    
    # Related products
    related_products = list(Product.objects.filter(
        category=product.category,
        is_active=True
    ).exclude(pk=product.pk).prefetch_related('images', 'reviews')[:4])
    
    if len(related_products) < 4:
        existing_pks = [p.pk for p in related_products] + [product.pk]
        additional = list(Product.objects.filter(is_active=True).exclude(pk__in=existing_pks).prefetch_related('images', 'reviews')[:4 - len(related_products)])
        related_products += additional

    # Reviews
    reviews = product.reviews.filter(is_approved=True).select_related('user')
    user_has_reviewed = False
    if request.user.is_authenticated:
        user_has_reviewed = product.reviews.filter(user=request.user).exists()

    context = {
        'product': product,
        'related_products': related_products,
        'reviews': reviews,
        'user_has_reviewed': user_has_reviewed,
    }
    return render(request, 'products/detail.html', context)


def search_api(request):
    q = request.GET.get('q', '').strip()
    if not q:
        return JsonResponse({'results': [], 'categories': []})

    products = Product.objects.filter(
        is_active=True
    ).filter(
        Q(name__icontains=q) |
        Q(description__icontains=q) |
        Q(short_description__icontains=q) |
        Q(tags__icontains=q) |
        Q(category__name__icontains=q)
    ).select_related('category')[:8]

    matching_categories = Category.objects.filter(
        Q(name__icontains=q) | Q(description__icontains=q)
    )[:4]

    results = []
    for p in products:
        results.append({
            'id': p.id,
            'name': p.name,
            'slug': p.slug,
            'category': p.category.name,
            'price': float(p.price),
            'discount_price': float(p.discount_price) if p.discount_price else None,
            'current_price': float(p.current_price),
            'badge': p.badge if p.badge != 'NONE' else None,
            'image_url': p.primary_image_url,
            'url': p.get_absolute_url(),
        })

    cat_results = []
    for c in matching_categories:
        cat_results.append({
            'id': c.id,
            'name': c.name,
            'slug': c.slug,
            'url': f"/shop/?category={c.slug}"
        })

    return JsonResponse({
        'results': results,
        'categories': cat_results,
        'count': len(results)
    })


def product_fallback_redirect(request):
    """Graceful redirect to catalog if /shop/product/ is accessed without a slug."""
    return redirect('products:shop')


def category_fallback_redirect(request):
    """Graceful redirect to catalog if /shop/category/ is accessed without a slug."""
    return redirect('products:shop')
