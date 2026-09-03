from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from products.models import Product
from .models import Review


@login_required
@require_POST
def add_review(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    
    rating = int(request.POST.get('rating', 5))
    if rating < 1 or rating > 5:
        rating = 5

    title = request.POST.get('title', '').strip()
    comment = request.POST.get('comment', '').strip()

    if not title or not comment:
        messages.error(request, "Please provide a headline and a review comment.")
        return redirect(product.get_absolute_url())

    review, created = Review.objects.update_or_create(
        product=product,
        user=request.user,
        defaults={
            'rating': rating,
            'title': title,
            'comment': comment,
            'is_verified_purchase': True,
            'is_approved': True
        }
    )

    if created:
        messages.success(request, "Thank you for reviewing! Your feedback helps our conscious community.")
    else:
        messages.success(request, "Your review has been updated.")

    return redirect(f"{product.get_absolute_url()}#reviews")
