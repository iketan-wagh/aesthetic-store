from decimal import Decimal
from django.conf import settings
from cart.models import Cart
from coupons.models import Coupon


def get_or_create_cart(request):
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        # If there was an anonymous session cart, merge items into user cart
        if request.session.session_key:
            session_cart = Cart.objects.filter(session_key=request.session.session_key, user__isnull=True).first()
            if session_cart and session_cart != cart:
                for item in session_cart.items.all():
                    existing_item = cart.items.filter(product=item.product).first()
                    if existing_item:
                        existing_item.quantity += item.quantity
                        existing_item.save()
                    else:
                        item.cart = cart
                        item.save()
                session_cart.delete()
        return cart
    else:
        if not request.session.session_key:
            request.session.create()
        cart, _ = Cart.objects.get_or_create(session_key=request.session.session_key, user__isnull=True)
        return cart


def cart_context(request):
    cart = get_or_create_cart(request)
    cart_items = list(cart.items.select_related('product', 'product__category').all())
    
    total_items = sum(item.quantity for item in cart_items)
    subtotal = sum(item.item_subtotal for item in cart_items)
    
    threshold = Decimal(str(getattr(settings, 'FREE_SHIPPING_THRESHOLD', 999)))
    default_fee = Decimal(str(getattr(settings, 'DEFAULT_SHIPPING_FEE', 99)))
    
    # Check session for coupon
    coupon_code = request.session.get('applied_coupon_code')
    applied_coupon = None
    discount_amount = Decimal('0.00')
    
    if coupon_code:
        coupon = Coupon.objects.filter(code=coupon_code, active=True).first()
        if coupon:
            is_valid, _ = coupon.is_valid(subtotal)
            if is_valid:
                applied_coupon = coupon
                discount_amount = coupon.calculate_discount(subtotal)
            else:
                request.session.pop('applied_coupon_code', None)
        else:
            request.session.pop('applied_coupon_code', None)

    shipping_fee = Decimal('0.00')
    if subtotal > 0 and subtotal < threshold:
        shipping_fee = default_fee

    final_total = max(Decimal('0.00'), subtotal - discount_amount + shipping_fee)
    free_shipping_unlocked = subtotal >= threshold
    amount_to_free_shipping = max(Decimal('0.00'), threshold - subtotal)
    free_shipping_progress = min(100, max(0, int((subtotal / threshold) * 100))) if threshold > 0 else 100

    return {
        'cart': cart,
        'cart_items': cart_items,
        'cart_total_items': total_items,
        'cart_subtotal': subtotal,
        'cart_discount': discount_amount,
        'cart_shipping': shipping_fee,
        'cart_total': final_total,
        'applied_coupon': applied_coupon,
        'free_shipping_progress': free_shipping_progress,
        'amount_to_free_shipping': amount_to_free_shipping,
        'free_shipping_unlocked': free_shipping_unlocked,
    }
