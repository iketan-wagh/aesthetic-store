from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from decimal import Decimal
from .models import Cart, CartItem
from products.models import Product
from coupons.models import Coupon
from .context_processors import get_or_create_cart


def cart_view(request):
    cart = get_or_create_cart(request)
    # Upsell recommendations
    cart_product_ids = cart.items.values_list('product_id', flat=True)
    recommended_products = Product.objects.filter(is_active=True).exclude(id__in=cart_product_ids)[:3]

    context = {
        'recommended_products': recommended_products,
    }
    return render(request, 'cart/cart.html', context)


@require_POST
def add_to_cart(request):
    product_id = request.POST.get('product_id')
    quantity = int(request.POST.get('quantity', 1))
    
    if quantity <= 0:
        quantity = 1

    product = get_object_or_404(Product, id=product_id, is_active=True)
    
    if product.stock < 1:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.POST.get('format') == 'json':
            return JsonResponse({'status': 'error', 'message': f'{product.name} is currently out of stock.'}, status=400)
        messages.error(request, f'{product.name} is currently out of stock.')
        return redirect(product.get_absolute_url())

    cart = get_or_create_cart(request)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

    if not created:
        new_quantity = cart_item.quantity + quantity
        if new_quantity > product.stock:
            new_quantity = product.stock
            messages.warning(request, f"Limited to maximum available stock ({product.stock} items).")
        cart_item.quantity = new_quantity
        cart_item.save()
    else:
        if quantity > product.stock:
            quantity = product.stock
        cart_item.quantity = quantity
        cart_item.save()

    # Recalculate summary
    subtotal = cart.subtotal
    total_items = cart.total_items
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.POST.get('format') == 'json':
        return JsonResponse({
            'status': 'success',
            'message': f'Added {product.name} to your bag.',
            'product_name': product.name,
            'total_items': total_items,
            'subtotal': float(subtotal),
            'shipping_progress': cart.free_shipping_progress,
            'amount_to_free_shipping': float(cart.amount_to_free_shipping),
            'free_shipping_unlocked': cart.free_shipping_unlocked,
        })

    messages.success(request, f'Added {product.name} to your bag.')
    return redirect('cart:cart_view')


@require_POST
def update_cart_item(request):
    item_id = request.POST.get('item_id')
    action = request.POST.get('action') # 'increase', 'decrease', 'set'
    cart = get_or_create_cart(request)
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)

    if action == 'increase':
        if cart_item.quantity < cart_item.product.stock:
            cart_item.quantity += 1
            cart_item.save()
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.POST.get('format') == 'json':
                return JsonResponse({'status': 'warning', 'message': 'Maximum stock reached.'}, status=400)
            messages.warning(request, 'Maximum stock reached.')
            return redirect('cart:cart_view')
    elif action == 'decrease':
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
            cart_item = None
    elif action == 'set':
        qty = int(request.POST.get('quantity', 1))
        if qty <= 0:
            cart_item.delete()
            cart_item = None
        else:
            cart_item.quantity = min(qty, cart_item.product.stock)
            cart_item.save()

    subtotal = cart.subtotal
    total_items = cart.total_items

    # Check coupon in session
    discount = Decimal('0.00')
    coupon_code = request.session.get('applied_coupon_code')
    if coupon_code:
        coupon = Coupon.objects.filter(code=coupon_code, active=True).first()
        if coupon and coupon.is_valid(subtotal)[0]:
            discount = coupon.calculate_discount(subtotal)
        else:
            request.session.pop('applied_coupon_code', None)

    shipping = Decimal('0.00') if (subtotal == 0 or subtotal >= cart.free_shipping_threshold) else Decimal(str(cart.default_shipping_fee))
    total = max(Decimal('0.00'), subtotal - discount + shipping)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.POST.get('format') == 'json':
        return JsonResponse({
            'status': 'success',
            'item_id': item_id,
            'item_quantity': cart_item.quantity if cart_item else 0,
            'item_subtotal': float(cart_item.item_subtotal) if cart_item else 0,
            'cart_subtotal': float(subtotal),
            'cart_discount': float(discount),
            'cart_shipping': float(shipping),
            'cart_total': float(total),
            'total_items': total_items,
            'shipping_progress': cart.free_shipping_progress,
            'amount_to_free_shipping': float(cart.amount_to_free_shipping),
            'free_shipping_unlocked': cart.free_shipping_unlocked,
        })

    return redirect('cart:cart_view')


@require_POST
def remove_from_cart(request):
    item_id = request.POST.get('item_id')
    cart = get_or_create_cart(request)
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
    product_name = cart_item.product.name
    cart_item.delete()

    subtotal = cart.subtotal
    total_items = cart.total_items

    # Check coupon in session
    discount = Decimal('0.00')
    coupon_code = request.session.get('applied_coupon_code')
    if coupon_code:
        coupon = Coupon.objects.filter(code=coupon_code, active=True).first()
        if coupon and coupon.is_valid(subtotal)[0]:
            discount = coupon.calculate_discount(subtotal)
        else:
            request.session.pop('applied_coupon_code', None)

    shipping = Decimal('0.00') if (subtotal == 0 or subtotal >= cart.free_shipping_threshold) else Decimal(str(cart.default_shipping_fee))
    total = max(Decimal('0.00'), subtotal - discount + shipping)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.POST.get('format') == 'json':
        return JsonResponse({
            'status': 'success',
            'message': f'Removed {product_name} from your bag.',
            'cart_subtotal': float(subtotal),
            'cart_discount': float(discount),
            'cart_shipping': float(shipping),
            'cart_total': float(total),
            'total_items': total_items,
            'shipping_progress': cart.free_shipping_progress,
            'amount_to_free_shipping': float(cart.amount_to_free_shipping),
            'free_shipping_unlocked': cart.free_shipping_unlocked,
        })

    messages.success(request, f'Removed {product_name} from your bag.')
    return redirect('cart:cart_view')


def cart_drawer_data(request):
    cart = get_or_create_cart(request)
    items = []
    for itm in cart.items.select_related('product', 'product__category').all():
        items.append({
            'id': itm.id,
            'product_id': itm.product.id,
            'name': itm.product.name,
            'slug': itm.product.slug,
            'category': itm.product.category.name,
            'price': float(itm.unit_price),
            'quantity': itm.quantity,
            'subtotal': float(itm.item_subtotal),
            'image_url': itm.product.primary_image_url,
            'stock': itm.product.stock,
            'url': itm.product.get_absolute_url()
        })

    subtotal = cart.subtotal
    discount = Decimal('0.00')
    coupon_code = request.session.get('applied_coupon_code')
    applied_coupon_info = None
    if coupon_code:
        coupon = Coupon.objects.filter(code=coupon_code, active=True).first()
        if coupon and coupon.is_valid(subtotal)[0]:
            discount = coupon.calculate_discount(subtotal)
            applied_coupon_info = {'code': coupon.code, 'discount_percentage': coupon.discount_percentage}

    shipping = Decimal('0.00') if (subtotal == 0 or subtotal >= cart.free_shipping_threshold) else Decimal(str(cart.default_shipping_fee))
    total = max(Decimal('0.00'), subtotal - discount + shipping)

    return JsonResponse({
        'items': items,
        'total_items': cart.total_items,
        'subtotal': float(subtotal),
        'discount': float(discount),
        'shipping': float(shipping),
        'total': float(total),
        'applied_coupon': applied_coupon_info,
        'shipping_progress': cart.free_shipping_progress,
        'amount_to_free_shipping': float(cart.amount_to_free_shipping),
        'free_shipping_unlocked': cart.free_shipping_unlocked,
    })
