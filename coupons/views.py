from django.shortcuts import redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from decimal import Decimal
from .models import Coupon
from cart.context_processors import get_or_create_cart


@require_POST
def apply_coupon(request):
    code = request.POST.get('code', '').strip().upper()
    cart = get_or_create_cart(request)
    subtotal = cart.subtotal

    if not code:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.POST.get('format') == 'json':
            return JsonResponse({'status': 'error', 'message': 'Please enter a coupon code.'}, status=400)
        messages.error(request, 'Please enter a coupon code.')
        return redirect('cart:cart_view')

    coupon = Coupon.objects.filter(code=code).first()
    if not coupon:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.POST.get('format') == 'json':
            return JsonResponse({'status': 'error', 'message': f"Coupon '{code}' is not valid."}, status=404)
        messages.error(request, f"Coupon '{code}' is not valid.")
        return redirect('cart:cart_view')

    is_valid, msg = coupon.is_valid(subtotal)
    if not is_valid:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.POST.get('format') == 'json':
            return JsonResponse({'status': 'error', 'message': msg}, status=400)
        messages.error(request, msg)
        return redirect('cart:cart_view')

    # Apply to session
    request.session['applied_coupon_code'] = coupon.code
    discount = coupon.calculate_discount(subtotal)
    shipping = Decimal('0.00') if (subtotal == 0 or subtotal >= cart.free_shipping_threshold) else Decimal(str(cart.default_shipping_fee))
    total = max(Decimal('0.00'), subtotal - discount + shipping)

    success_msg = f"Coupon '{coupon.code}' applied! You saved ₹{discount:.2f}"
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.POST.get('format') == 'json':
        return JsonResponse({
            'status': 'success',
            'message': success_msg,
            'coupon_code': coupon.code,
            'discount_percentage': coupon.discount_percentage,
            'discount_amount': float(discount),
            'cart_subtotal': float(subtotal),
            'cart_shipping': float(shipping),
            'cart_total': float(total)
        })

    messages.success(request, success_msg)
    return redirect('cart:cart_view')


@require_POST
def remove_coupon(request):
    request.session.pop('applied_coupon_code', None)
    cart = get_or_create_cart(request)
    subtotal = cart.subtotal
    shipping = Decimal('0.00') if (subtotal == 0 or subtotal >= cart.free_shipping_threshold) else Decimal(str(cart.default_shipping_fee))
    total = max(Decimal('0.00'), subtotal + shipping)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.POST.get('format') == 'json':
        return JsonResponse({
            'status': 'success',
            'message': 'Coupon removed.',
            'cart_subtotal': float(subtotal),
            'cart_discount': 0.00,
            'cart_shipping': float(shipping),
            'cart_total': float(total)
        })

    messages.info(request, 'Coupon removed.')
    return redirect('cart:cart_view')
