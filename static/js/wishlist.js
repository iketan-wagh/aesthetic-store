/**
 * NOMA Wishlist Interactivity
 */

const WishlistManager = {
  init() {
    document.addEventListener('click', async (e) => {
      const btn = e.target.closest('.wishlist-toggle-btn');
      if (!btn) return;

      e.preventDefault();
      e.stopPropagation();

      const productId = btn.dataset.productId;
      if (!productId) return;

      const heartIcon = btn.querySelector('svg');
      btn.disabled = true;

      try {
        const formData = new FormData();
        formData.append('product_id', productId);

        const res = await fetch('/wishlist/toggle/', {
          method: 'POST',
          headers: {
            'X-CSRFToken': csrftoken,
            'X-Requested-With': 'XMLHttpRequest'
          },
          body: formData
        });

        const data = await res.json();
        if (res.ok) {
          Toast.show(data.message, data.is_in_wishlist ? 'success' : 'info');
          this.updateHeartAppearance(btn, data.is_in_wishlist);
          this.updateWishlistCount(data.wishlist_count);
        } else {
          Toast.show('Could not update wishlist.', 'error');
        }
      } catch (err) {
        Toast.show('Network error.', 'error');
      } finally {
        btn.disabled = false;
      }
    });
  },

  updateHeartAppearance(btn, isInWishlist) {
    const icon = btn.querySelector('svg');
    if (isInWishlist) {
      btn.classList.add('text-terracotta');
      btn.classList.remove('text-neutral-400');
      if (icon) {
        icon.setAttribute('fill', 'currentColor');
        icon.classList.add('scale-110');
        setTimeout(() => icon.classList.remove('scale-110'), 200);
      }
    } else {
      btn.classList.remove('text-terracotta');
      btn.classList.add('text-neutral-400');
      if (icon) icon.setAttribute('fill', 'none');
    }
  },

  updateWishlistCount(count) {
    document.querySelectorAll('.wishlist-badge-count').forEach(el => {
      el.innerText = count;
      if (count > 0) {
        el.classList.remove('hidden');
      } else {
        el.classList.add('hidden');
      }
    });
  }
};

document.addEventListener('DOMContentLoaded', () => {
  WishlistManager.init();
});
