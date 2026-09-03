from wishlist.models import Wishlist


def get_or_create_wishlist(request):
    if request.user.is_authenticated:
        wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
        # Merge anonymous session wishlist if exists
        if request.session.session_key:
            session_wishlist = Wishlist.objects.filter(session_key=request.session.session_key, user__isnull=True).first()
            if session_wishlist and session_wishlist != wishlist:
                for item in session_wishlist.items.all():
                    if not wishlist.items.filter(product=item.product).exists():
                        item.wishlist = wishlist
                        item.save()
                    else:
                        item.delete()
                session_wishlist.delete()
        return wishlist
    else:
        if not request.session.session_key:
            request.session.create()
        wishlist, _ = Wishlist.objects.get_or_create(session_key=request.session.session_key, user__isnull=True)
        return wishlist


def wishlist_context(request):
    wishlist = get_or_create_wishlist(request)
    product_ids = list(wishlist.items.values_list('product_id', flat=True))
    return {
        'wishlist': wishlist,
        'wishlist_count': len(product_ids),
        'wishlist_product_ids': product_ids,
    }
