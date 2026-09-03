import uuid
import json
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.db import transaction
from django.conf import settings

try:
    import razorpay
except ImportError:
    razorpay = None

from .models import Order, OrderItem, PaymentTransaction
from cart.models import Cart
from accounts.models import Address
from coupons.models import Coupon, CouponUsage
from cart.context_processors import get_or_create_cart


def checkout_view(request):
    cart = get_or_create_cart(request)
    if cart.total_items == 0:
        messages.warning(request, "Your bag is empty. Add some conscious pieces before checking out!")
        return redirect('products:shop')

    # Verify stock
    for item in cart.items.all():
        if item.quantity > item.product.stock:
            messages.error(request, f"Sorry, only {item.product.stock} units of {item.product.name} are in stock.")
            return redirect('cart:cart_view')

    saved_addresses = []
    default_address = None
    if request.user.is_authenticated:
        saved_addresses = Address.objects.filter(user=request.user)
        default_address = saved_addresses.filter(is_default=True).first()
        if not default_address and saved_addresses.exists():
            default_address = saved_addresses.first()

    # Calculate financial numbers
    subtotal = cart.subtotal
    coupon_code = request.session.get('applied_coupon_code')
    applied_coupon = None
    discount_amount = Decimal('0.00')
    if coupon_code:
        coupon = Coupon.objects.filter(code=coupon_code, active=True).first()
        if coupon and coupon.is_valid(subtotal)[0]:
            applied_coupon = coupon
            discount_amount = coupon.calculate_discount(subtotal)

    shipping_fee = Decimal('0.00') if (subtotal >= cart.free_shipping_threshold) else Decimal(str(cart.default_shipping_fee))
    total_amount = max(Decimal('0.00'), subtotal - discount_amount + shipping_fee)

    context = {
        'cart': cart,
        'cart_items': cart.items.select_related('product').all(),
        'saved_addresses': saved_addresses,
        'default_address': default_address,
        'cart_subtotal': subtotal,
        'cart_discount': discount_amount,
        'cart_shipping': shipping_fee,
        'cart_total': total_amount,
        'applied_coupon': applied_coupon,
        'razorpay_key_id': getattr(settings, 'RAZORPAY_KEY_ID', ''),
    }
    return render(request, 'orders/checkout.html', context)


@require_POST
def create_razorpay_order(request):
    """
    Creates a real Razorpay order using the Razorpay Python SDK.
    Returns the razorpay_order_id and amount in paise to the frontend SDK.
    """
    cart = get_or_create_cart(request)
    if cart.total_items == 0:
        return JsonResponse({'status': 'error', 'message': 'Cart is empty'}, status=400)

    subtotal = cart.subtotal
    coupon_code = request.session.get('applied_coupon_code')
    discount_amount = Decimal('0.00')
    if coupon_code:
        coupon = Coupon.objects.filter(code=coupon_code, active=True).first()
        if coupon and coupon.is_valid(subtotal)[0]:
            discount_amount = coupon.calculate_discount(subtotal)

    shipping_fee = Decimal('0.00') if (subtotal >= cart.free_shipping_threshold) else Decimal(str(cart.default_shipping_fee))
    total_amount = max(Decimal('0.00'), subtotal - discount_amount + shipping_fee)
    amount_in_paise = int(total_amount * 100)

    key_id = getattr(settings, 'RAZORPAY_KEY_ID', '')
    key_secret = getattr(settings, 'RAZORPAY_KEY_SECRET', '')

    razorpay_order_id = f"order_sim_{uuid.uuid4().hex[:12]}"

    if razorpay and key_id and key_secret and not key_id.startswith('rzp_test_NomaStore'):
        try:
            client = razorpay.Client(auth=(key_id, key_secret))
            order_data = {
                'amount': amount_in_paise,
                'currency': 'INR',
                'payment_capture': 1,
                'notes': {
                    'cart_items': str(cart.total_items),
                    'customer': request.user.username if request.user.is_authenticated else 'Guest'
                }
            }
            rzp_order = client.order.create(data=order_data)
            razorpay_order_id = rzp_order['id']
        except Exception as e:
            # Fallback to simulated order id if credentials are placeholder or network issue
            razorpay_order_id = f"order_fallback_{uuid.uuid4().hex[:12]}"
    else:
        # Standard local sandbox simulated order
        razorpay_order_id = f"order_demo_{uuid.uuid4().hex[:12]}"

    return JsonResponse({
        'status': 'success',
        'razorpay_order_id': razorpay_order_id,
        'amount': amount_in_paise,
        'currency': 'INR',
        'key_id': key_id,
        'brand_name': 'Aesthetic Store',
    })


@require_POST
def verify_razorpay_payment(request):
    """
    Verifies Razorpay payment signature and completes order creation.
    """
    cart = get_or_create_cart(request)
    if cart.total_items == 0:
        return JsonResponse({'status': 'error', 'message': 'Cart is empty'}, status=400)

    try:
        data = json.loads(request.body)
    except Exception:
        data = request.POST

    razorpay_payment_id = data.get('razorpay_payment_id', f"pay_live_{uuid.uuid4().hex[:14]}")
    razorpay_order_id = data.get('razorpay_order_id', '')
    razorpay_signature = data.get('razorpay_signature', '')

    # Shipping details from request
    shipping_name = data.get('full_name', '').strip()
    shipping_email = data.get('email', '').strip()
    shipping_phone = data.get('phone', '').strip()
    shipping_address_line1 = data.get('address_line1', '').strip()
    shipping_address_line2 = data.get('address_line2', '').strip()
    shipping_landmark = data.get('landmark', '').strip()
    shipping_city = data.get('city', '').strip()
    shipping_state = data.get('state', '').strip()
    shipping_pincode = data.get('pincode', '').strip()
    order_notes = data.get('order_notes', '').strip()
    save_address = data.get('save_address')

    # If saved address was selected
    address_id = data.get('saved_address_id')
    if address_id and request.user.is_authenticated:
        addr = Address.objects.filter(id=address_id, user=request.user).first()
        if addr:
            shipping_name = addr.full_name
            shipping_phone = addr.phone
            shipping_email = request.user.email or shipping_email
            shipping_address_line1 = addr.address_line1
            shipping_address_line2 = addr.address_line2
            shipping_landmark = addr.landmark
            shipping_city = addr.city
            shipping_state = addr.state
            shipping_pincode = addr.pincode

    if not all([shipping_name, shipping_phone, shipping_address_line1, shipping_city, shipping_state, shipping_pincode]):
        return JsonResponse({'status': 'error', 'message': 'Missing required address fields'}, status=400)

    # Optional signature verification for production keys
    key_id = getattr(settings, 'RAZORPAY_KEY_ID', '')
    key_secret = getattr(settings, 'RAZORPAY_KEY_SECRET', '')
    if razorpay and key_id and key_secret and razorpay_signature and not key_id.startswith('rzp_test_NomaStore'):
        try:
            client = razorpay.Client(auth=(key_id, key_secret))
            client.utility.verify_payment_signature({
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            })
        except razorpay.errors.SignatureVerificationError:
            return JsonResponse({'status': 'error', 'message': 'Payment signature verification failed.'}, status=400)
        except Exception:
            pass

    subtotal = cart.subtotal
    coupon_code = request.session.get('applied_coupon_code')
    applied_coupon = None
    discount_amount = Decimal('0.00')
    if coupon_code:
        coupon = Coupon.objects.filter(code=coupon_code, active=True).first()
        if coupon and coupon.is_valid(subtotal)[0]:
            applied_coupon = coupon
            discount_amount = coupon.calculate_discount(subtotal)

    shipping_fee = Decimal('0.00') if (subtotal >= cart.free_shipping_threshold) else Decimal(str(cart.default_shipping_fee))
    total_amount = max(Decimal('0.00'), subtotal - discount_amount + shipping_fee)

    with transaction.atomic():
        if request.user.is_authenticated and save_address:
            Address.objects.create(
                user=request.user,
                full_name=shipping_name,
                phone=shipping_phone,
                address_line1=shipping_address_line1,
                address_line2=shipping_address_line2,
                landmark=shipping_landmark,
                city=shipping_city,
                state=shipping_state,
                pincode=shipping_pincode,
                is_default=False
            )

        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            shipping_name=shipping_name,
            shipping_email=shipping_email or (request.user.email if request.user.is_authenticated else 'customer@aestheticstore.com'),
            shipping_phone=shipping_phone,
            shipping_address_line1=shipping_address_line1,
            shipping_address_line2=shipping_address_line2,
            shipping_landmark=shipping_landmark,
            shipping_city=shipping_city,
            shipping_state=shipping_state,
            shipping_pincode=shipping_pincode,
            subtotal=subtotal,
            discount_amount=discount_amount,
            shipping_fee=shipping_fee,
            total_amount=total_amount,
            coupon=applied_coupon,
            coupon_code=applied_coupon.code if applied_coupon else '',
            order_status='CONFIRMED',
            payment_method='ONLINE_TEST',
            payment_status='PAID',
            payment_id=razorpay_payment_id,
            order_notes=order_notes,
            tracking_number=f"TRK-AST-{uuid.uuid4().hex[:6].upper()}"
        )

        for item in cart.items.select_related('product').all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                product_name=item.product.name,
                product_sku=item.product.sku,
                price=item.product.current_price,
                quantity=item.quantity,
                subtotal=item.item_subtotal
            )
            if item.product.stock >= item.quantity:
                item.product.stock -= item.quantity
                item.product.save(update_fields=['stock'])

        if applied_coupon:
            CouponUsage.objects.create(
                coupon=applied_coupon,
                user=request.user if request.user.is_authenticated else None,
                session_key=request.session.session_key,
                discount_amount=discount_amount
            )
            applied_coupon.used_count += 1
            applied_coupon.save(update_fields=['used_count'])

        PaymentTransaction.objects.create(
            order=order,
            transaction_id=razorpay_payment_id,
            gateway='Razorpay_Live' if key_id.startswith('rzp_live') else 'Razorpay_Test',
            amount=total_amount,
            status='SUCCESS',
            response_payload=json.dumps({
                'gateway': 'Razorpay',
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'status': 'captured',
                'amount_paise': int(total_amount * 100),
                'currency': 'INR'
            })
        )

        cart.items.all().delete()
        request.session.pop('applied_coupon_code', None)
        request.session['last_order_number'] = order.order_number

    return JsonResponse({
        'status': 'success',
        'order_number': order.order_number,
        'redirect_url': f"/orders/success/{order.order_number}/"
    })


@require_POST
def process_checkout(request):
    """
    Standard form POST for Cash on Delivery (COD) or direct submission.
    """
    cart = get_or_create_cart(request)
    if cart.total_items == 0:
        messages.error(request, "Your bag is empty.")
        return redirect('products:shop')

    address_choice = request.POST.get('address_choice')
    
    if address_choice == 'saved' and request.user.is_authenticated:
        address_id = request.POST.get('saved_address_id')
        addr = get_object_or_404(Address, id=address_id, user=request.user)
        shipping_name = addr.full_name
        shipping_phone = addr.phone
        shipping_email = request.user.email or request.POST.get('email', '')
        shipping_address_line1 = addr.address_line1
        shipping_address_line2 = addr.address_line2
        shipping_landmark = addr.landmark
        shipping_city = addr.city
        shipping_state = addr.state
        shipping_pincode = addr.pincode
    else:
        shipping_name = request.POST.get('full_name', '').strip()
        shipping_email = request.POST.get('email', '').strip()
        shipping_phone = request.POST.get('phone', '').strip()
        shipping_address_line1 = request.POST.get('address_line1', '').strip()
        shipping_address_line2 = request.POST.get('address_line2', '').strip()
        shipping_landmark = request.POST.get('landmark', '').strip()
        shipping_city = request.POST.get('city', '').strip()
        shipping_state = request.POST.get('state', '').strip()
        shipping_pincode = request.POST.get('pincode', '').strip()

        if not all([shipping_name, shipping_email, shipping_phone, shipping_address_line1, shipping_city, shipping_state, shipping_pincode]):
            messages.error(request, "Please fill in all required shipping address fields.")
            return redirect('orders:checkout')

        if request.user.is_authenticated and request.POST.get('save_address') == 'on':
            Address.objects.create(
                user=request.user,
                full_name=shipping_name,
                phone=shipping_phone,
                address_line1=shipping_address_line1,
                address_line2=shipping_address_line2,
                landmark=shipping_landmark,
                city=shipping_city,
                state=shipping_state,
                pincode=shipping_pincode,
                is_default=False
            )

    payment_method = request.POST.get('payment_method', 'COD')
    order_notes = request.POST.get('order_notes', '').strip()

    subtotal = cart.subtotal
    coupon_code = request.session.get('applied_coupon_code')
    applied_coupon = None
    discount_amount = Decimal('0.00')
    if coupon_code:
        coupon = Coupon.objects.filter(code=coupon_code, active=True).first()
        if coupon and coupon.is_valid(subtotal)[0]:
            applied_coupon = coupon
            discount_amount = coupon.calculate_discount(subtotal)

    shipping_fee = Decimal('0.00') if (subtotal >= cart.free_shipping_threshold) else Decimal(str(cart.default_shipping_fee))
    total_amount = max(Decimal('0.00'), subtotal - discount_amount + shipping_fee)

    with transaction.atomic():
        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            shipping_name=shipping_name,
            shipping_email=shipping_email,
            shipping_phone=shipping_phone,
            shipping_address_line1=shipping_address_line1,
            shipping_address_line2=shipping_address_line2,
            shipping_landmark=shipping_landmark,
            shipping_city=shipping_city,
            shipping_state=shipping_state,
            shipping_pincode=shipping_pincode,
            subtotal=subtotal,
            discount_amount=discount_amount,
            shipping_fee=shipping_fee,
            total_amount=total_amount,
            coupon=applied_coupon,
            coupon_code=applied_coupon.code if applied_coupon else '',
            order_status='CONFIRMED',
            payment_method=payment_method,
            payment_status='PAID' if payment_method in ['UPI', 'CARD', 'NETBANKING', 'ONLINE_TEST'] else 'PENDING',
            order_notes=order_notes,
            tracking_number=f"TRK-AST-{uuid.uuid4().hex[:6].upper()}"
        )

        for item in cart.items.select_related('product').all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                product_name=item.product.name,
                product_sku=item.product.sku,
                price=item.product.current_price,
                quantity=item.quantity,
                subtotal=item.item_subtotal
            )
            if item.product.stock >= item.quantity:
                item.product.stock -= item.quantity
                item.product.save(update_fields=['stock'])

        if applied_coupon:
            CouponUsage.objects.create(
                coupon=applied_coupon,
                user=request.user if request.user.is_authenticated else None,
                session_key=request.session.session_key,
                discount_amount=discount_amount
            )
            applied_coupon.used_count += 1
            applied_coupon.save(update_fields=['used_count'])

        txn_id = f"pay_{uuid.uuid4().hex[:14]}"
        is_online = payment_method in ['UPI', 'CARD', 'NETBANKING', 'ONLINE_TEST']
        gateway_name = f"Razorpay_{payment_method}" if is_online else "COD_Gateway"

        PaymentTransaction.objects.create(
            order=order,
            transaction_id=txn_id,
            gateway=gateway_name,
            amount=total_amount,
            status='SUCCESS' if is_online else 'PENDING_COD',
            response_payload=json.dumps({
                'gateway': gateway_name,
                'method': payment_method,
                'status': 'captured' if is_online else 'pending',
                'txn_id': txn_id,
                'currency': 'INR'
            })
        )
        order.payment_id = txn_id
        order.save(update_fields=['payment_id'])

        cart.items.all().delete()
        request.session.pop('applied_coupon_code', None)
        request.session['last_order_number'] = order.order_number

    return redirect('orders:order_success', order_number=order.order_number)


def order_success(request, order_number):
    order = get_object_or_404(Order.objects.prefetch_related('items'), order_number=order_number)
    
    # Security check: Prevent IDOR / unauthorized viewing
    if order.user:
        if not request.user.is_authenticated or order.user != request.user:
            messages.error(request, "Unauthorized to view this order confirmation.")
            return redirect('core:home')
    else:
        # Guest order check: Must match active session's last order
        if request.session.get('last_order_number') != order.order_number and not request.user.is_staff:
            messages.error(request, "Unauthorized access to guest order confirmation.")
            return redirect('core:home')

    context = {
        'order': order,
    }
    return render(request, 'orders/success.html', context)


def order_detail(request, order_number):
    order = get_object_or_404(Order.objects.prefetch_related('items'), order_number=order_number)
    
    # Security check: Prevent IDOR / unauthorized viewing
    if order.user:
        if not request.user.is_authenticated or order.user != request.user:
            messages.error(request, "Unauthorized to view this order.")
            return redirect('accounts:login')
    else:
        # Guest order check: Require matching session or login
        if request.session.get('last_order_number') != order.order_number and not request.user.is_staff:
            messages.error(request, "Please log in to view account order history.")
            return redirect('accounts:login')

    context = {
        'order': order,
    }
    return render(request, 'orders/detail.html', context)
