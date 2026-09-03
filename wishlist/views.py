from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from .models import Wishlist, WishlistItem
from products.models import Product
from cart.models import Cart, CartItem
from .context_processors import get_or_create_wishlist
from cart.context_processors import get_or_create_cart


def wishlist_view(request):
    wishlist = get_or_create_wishlist(request)
    items = wishlist.items.select_related('product', 'product__category').all()
    context = {
        'wishlist_items': items,
    }
    return render(request, 'wishlist/wishlist.html', context)


@require_POST
def toggle_wishlist(request):
    product_id = request.POST.get('product_id')
    product = get_object_or_404(Product, id=product_id, is_active=True)
    wishlist = get_or_create_wishlist(request)

    wishlist_item = wishlist.items.filter(product=product).first()
    if wishlist_item:
        wishlist_item.delete()
        is_in_wishlist = False
        message = f"Removed {product.name} from your wishlist."
    else:
        WishlistItem.objects.create(wishlist=wishlist, product=product)
        is_in_wishlist = True
        message = f"Added {product.name} to your wishlist."

    count = wishlist.items.count()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.POST.get('format') == 'json':
        return JsonResponse({
            'status': 'success',
            'is_in_wishlist': is_in_wishlist,
            'wishlist_count': count,
            'message': message,
        })

    messages.info(request, message)
    return redirect(request.META.get('HTTP_REFERER', 'wishlist:wishlist_view'))


@require_POST
def move_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    wishlist = get_or_create_wishlist(request)
    cart = get_or_create_cart(request)

    # Remove from wishlist
    wishlist.items.filter(product=product).delete()

    # Add to cart
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        cart_item.quantity += 1
        cart_item.save()

    messages.success(request, f"Moved {product.name} to your bag.")
    return redirect('cart:cart_view')
