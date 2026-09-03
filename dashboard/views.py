import json
import functools
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.db.models import Sum, Count, Q
from django.utils import timezone
from django.core.paginator import Paginator
from django.conf import settings

from orders.models import Order, OrderItem, PaymentTransaction
from products.models import Product, Category
from accounts.models import UserProfile
from coupons.models import Coupon, CouponUsage


def is_dashboard_authenticated(request):
    """Checks if the user is staff AND has completed the dashboard password challenge in this session."""
    if not request.user.is_authenticated or not request.user.is_staff:
        return False
    verified_until = request.session.get('dashboard_verified_until', 0)
    if timezone.now().timestamp() > verified_until:
        return False
    return True


def dashboard_protected(view_func):
    """Decorator requiring staff status AND password gate verification."""
    @functools.wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(f"/dashboard/auth/?next={request.path}")
        if not request.user.is_staff:
            messages.error(request, "Access restricted to authorized administrative staff.")
            return redirect('core:home')
        if not is_dashboard_authenticated(request):
            return redirect(f"/dashboard/auth/?next={request.path}")
        return view_func(request, *args, **kwargs)
    return wrapper


def dashboard_auth_view(request):
    """Password Gate Screen: Requires re-entering admin password before granting access."""
    next_url = request.GET.get('next') or request.POST.get('next') or '/dashboard/'

    # If already verified, go straight to dashboard
    if is_dashboard_authenticated(request):
        return redirect(next_url)

    if request.method == 'POST':
        password = request.POST.get('password', '').strip()
        
        # If user is already logged in as staff, verify their password
        if request.user.is_authenticated:
            if not request.user.is_staff:
                messages.error(request, "Access denied: Staff privileges required.")
                return redirect('core:home')
            
            # Check user password or master passcode
            custom_passcode = getattr(settings, 'DASHBOARD_PASSCODE', '')
            if request.user.check_password(password) or (custom_passcode and password == custom_passcode):
                # Grant access for 1 hour (3600s)
                request.session['dashboard_verified_until'] = timezone.now().timestamp() + 3600
                messages.success(request, f"Welcome back, {request.user.first_name or request.user.username}! Operations Hub unlocked.")
                return redirect(next_url)
            else:
                messages.error(request, "Incorrect admin password. Access denied.")
        else:
            # Unauthenticated user: require username & password
            username_or_email = request.POST.get('username', '').strip()
            user_obj = User.objects.filter(Q(username__iexact=username_or_email) | Q(email__iexact=username_or_email)).first()
            if user_obj:
                user = authenticate(request, username=user_obj.username, password=password)
                if user and user.is_staff:
                    login(request, user)
                    request.session['dashboard_verified_until'] = timezone.now().timestamp() + 3600
                    messages.success(request, f"Welcome back, {user.first_name or user.username}! Operations Hub unlocked.")
                    return redirect(next_url)

            messages.error(request, "Invalid administrator credentials.")

    context = {
        'next': next_url,
    }
    return render(request, 'dashboard/auth_gate.html', context)


def dashboard_lock_view(request):
    """Instantly locks the dashboard session and redirects to password gate."""
    request.session.pop('dashboard_verified_until', None)
    messages.info(request, "Operations Hub session locked securely.")
    return redirect('dashboard:auth')


@dashboard_protected
def dashboard_home(request):
    """Main Analytics & Quick Store Operations Hub."""
    now = timezone.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    # Key Metrics
    total_revenue = Order.objects.filter(payment_status='PAID').aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
    today_revenue = Order.objects.filter(payment_status='PAID', created_at__gte=today_start).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
    total_orders_count = Order.objects.count()
    unfulfilled_orders_count = Order.objects.filter(order_status__in=['CONFIRMED', 'PROCESSING']).count()
    total_customers_count = User.objects.filter(is_staff=False).count()
    low_stock_products_count = Product.objects.filter(stock__lte=5, is_active=True).count()

    # Recent 8 Orders
    recent_orders = Order.objects.prefetch_related('items', 'items__product').order_by('-created_at')[:8]

    # Low Stock Products list
    low_stock_products = Product.objects.filter(stock__lte=5, is_active=True).order_by('stock')[:5]

    context = {
        'total_revenue': total_revenue,
        'today_revenue': today_revenue,
        'total_orders_count': total_orders_count,
        'unfulfilled_orders_count': unfulfilled_orders_count,
        'total_customers_count': total_customers_count,
        'low_stock_products_count': low_stock_products_count,
        'recent_orders': recent_orders,
        'low_stock_products': low_stock_products,
        'active_nav': 'overview',
    }
    return render(request, 'dashboard/home.html', context)


@dashboard_protected
def dashboard_orders(request):
    """Full-featured interactive order search, address lookup & fulfillment manager."""
    orders_qs = Order.objects.prefetch_related('items', 'items__product').order_by('-created_at')

    # Status filter
    status_filter = request.GET.get('status', '').strip().upper()
    if status_filter and status_filter != 'ALL':
        orders_qs = orders_qs.filter(order_status=status_filter)

    # Payment filter
    payment_filter = request.GET.get('payment', '').strip().upper()
    if payment_filter and payment_filter != 'ALL':
        orders_qs = orders_qs.filter(payment_status=payment_filter)

    # Search Query across all fields: Order number, Name, Phone, Email, City, Pincode, Tracking ID
    query = request.GET.get('q', '').strip()
    if query:
        orders_qs = orders_qs.filter(
            Q(order_number__icontains=query) |
            Q(shipping_name__icontains=query) |
            Q(shipping_phone__icontains=query) |
            Q(shipping_email__icontains=query) |
            Q(shipping_city__icontains=query) |
            Q(shipping_pincode__icontains=query) |
            Q(shipping_address_line1__icontains=query) |
            Q(tracking_number__icontains=query) |
            Q(payment_id__icontains=query)
        ).distinct()

    # Pagination
    paginator = Paginator(orders_qs, 15)
    page_number = request.GET.get('page', 1)
    orders_page = paginator.get_page(page_number)

    status_counts = {
        'ALL': Order.objects.count(),
        'CONFIRMED': Order.objects.filter(order_status='CONFIRMED').count(),
        'PROCESSING': Order.objects.filter(order_status='PROCESSING').count(),
        'SHIPPED': Order.objects.filter(order_status='SHIPPED').count(),
        'DELIVERED': Order.objects.filter(order_status='DELIVERED').count(),
        'CANCELLED': Order.objects.filter(order_status='CANCELLED').count(),
    }

    context = {
        'orders': orders_page,
        'query': query,
        'status_filter': status_filter or 'ALL',
        'payment_filter': payment_filter or 'ALL',
        'status_counts': status_counts,
        'active_nav': 'orders',
    }
    return render(request, 'dashboard/orders.html', context)


@dashboard_protected
def dashboard_order_update_status(request, order_number):
    """AJAX/Form endpoint to update fulfillment status & tracking number."""
    order = get_object_or_404(Order, order_number=order_number)

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except Exception:
            data = request.POST

        new_status = data.get('order_status')
        new_tracking = data.get('tracking_number')

        if new_status and new_status in dict(Order.ORDER_STATUS_CHOICES).keys():
            order.order_status = new_status
        if new_tracking is not None:
            order.tracking_number = new_tracking.strip()

        order.save()

        if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.POST.get('format') == 'json':
            return JsonResponse({
                'status': 'success',
                'order_number': order.order_number,
                'order_status': order.order_status,
                'order_status_display': order.get_order_status_display(),
                'tracking_number': order.tracking_number,
                'message': f"Order #{order.order_number} status updated to {order.get_order_status_display()}."
            })

        messages.success(request, f"Order #{order.order_number} status updated.")
    return redirect('dashboard:orders')


@dashboard_protected
def dashboard_order_slip(request, order_number):
    """Clean, printable Packing Slip / Dispatch Label."""
    order = get_object_or_404(Order.objects.prefetch_related('items'), order_number=order_number)
    return render(request, 'dashboard/order_slip.html', {'order': order})


@dashboard_protected
def dashboard_inventory(request):
    """Real-time Product Catalog & Stock Controller."""
    products = Product.objects.select_related('category').order_by('category__name', 'name')
    categories = Category.objects.all()

    query = request.GET.get('q', '').strip()
    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(sku__icontains=query) |
            Q(category__name__icontains=query)
        )

    cat_filter = request.GET.get('category', '')
    if cat_filter:
        products = products.filter(category__slug=cat_filter)

    context = {
        'products': products,
        'categories': categories,
        'query': query,
        'cat_filter': cat_filter,
        'active_nav': 'inventory',
    }
    return render(request, 'dashboard/inventory.html', context)


@dashboard_protected
def dashboard_product_update_stock(request, pk):
    """Inline AJAX stock updater."""
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except Exception:
            data = request.POST

        stock_val = data.get('stock')
        is_active = data.get('is_active')

        if stock_val is not None:
            try:
                product.stock = max(0, int(stock_val))
            except ValueError:
                pass

        if is_active is not None:
            product.is_active = bool(is_active)

        product.save()

        return JsonResponse({
            'status': 'success',
            'product_id': product.id,
            'stock': product.stock,
            'is_active': product.is_active,
            'in_stock': product.in_stock,
            'message': f"Updated {product.name} (Stock: {product.stock})."
        })

    return JsonResponse({'status': 'error', 'message': 'Invalid method'}, status=405)


@dashboard_protected
def dashboard_customers(request):
    """Customer Directory & Analytics."""
    customers_qs = User.objects.filter(is_staff=False).annotate(
        order_count=Count('orders'),
        total_spend=Sum('orders__total_amount', filter=Q(orders__payment_status='PAID'))
    ).order_by('-date_joined')

    query = request.GET.get('q', '').strip()
    if query:
        customers_qs = customers_qs.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query) |
            Q(username__icontains=query)
        )

    paginator = Paginator(customers_qs, 20)
    page_number = request.GET.get('page', 1)
    customers_page = paginator.get_page(page_number)

    context = {
        'customers': customers_page,
        'query': query,
        'active_nav': 'customers',
    }
    return render(request, 'dashboard/customers.html', context)


@dashboard_protected
def dashboard_coupons(request):
    """Coupons & Promotions Controller."""
    coupons = Coupon.objects.all().order_by('-created_at')
    context = {
        'coupons': coupons,
        'active_nav': 'coupons',
    }
    return render(request, 'dashboard/coupons.html', context)
