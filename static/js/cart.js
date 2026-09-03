/**
 * NOMA Cart & Cart Drawer Interactivity
 */

const CartDrawer = {
  isOpen: false,

  init() {
    this.drawer = document.getElementById('cart-drawer');
    this.overlay = document.getElementById('cart-drawer-overlay');
    this.panel = document.getElementById('cart-drawer-panel');
    this.closeBtn = document.getElementById('cart-drawer-close');
    this.itemsContainer = document.getElementById('cart-drawer-items');
    this.subtotalEl = document.getElementById('cart-drawer-subtotal');
    this.progressFill = document.getElementById('cart-drawer-progress-fill');
    this.progressText = document.getElementById('cart-drawer-progress-text');
    this.badgeEls = document.querySelectorAll('.cart-badge-count');

    // Trigger buttons
    document.querySelectorAll('.cart-trigger-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        this.open();
      });
    });

    if (this.closeBtn) this.closeBtn.addEventListener('click', () => this.close());
    if (this.overlay) this.overlay.addEventListener('click', () => this.close());

    // Close on Escape
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && this.isOpen) {
        this.close();
      }
    });

    // Delegate quantity & remove actions within drawer
    if (this.itemsContainer) {
      this.itemsContainer.addEventListener('click', (e) => {
        const target = e.target.closest('button');
        if (!target) return;

        const action = target.dataset.action;
        const itemId = target.dataset.itemId;

        if (action === 'increase' || action === 'decrease') {
          this.updateQuantity(itemId, action);
        } else if (action === 'remove') {
          this.removeItem(itemId);
        }
      });
    }

    // Intercept Quick Add buttons
    document.addEventListener('submit', (e) => {
      if (e.target.classList.contains('ajax-add-to-cart-form')) {
        e.preventDefault();
        this.handleAddToCartForm(e.target);
      }
    });
  },

  async open() {
    if (!this.drawer) return;
    this.drawer.classList.remove('hidden');
    // Allow browser to render display before transitioning
    setTimeout(() => {
      if (this.overlay) {
        this.overlay.classList.remove('opacity-0');
        this.overlay.classList.add('opacity-100');
      }
      if (this.panel) {
        this.panel.classList.remove('translate-x-full');
      }
    }, 10);
    
    document.body.style.overflow = 'hidden';
    this.isOpen = true;
    await this.refreshDrawer();
  },

  close() {
    if (!this.drawer) return;
    if (this.overlay) {
      this.overlay.classList.add('opacity-0');
      this.overlay.classList.remove('opacity-100');
    }
    if (this.panel) {
      this.panel.classList.add('translate-x-full');
    }
    document.body.style.overflow = '';
    this.isOpen = false;
    setTimeout(() => {
      if (!this.isOpen && this.drawer) {
        this.drawer.classList.add('hidden');
      }
    }, 300);
  },

  async handleAddToCartForm(form) {
    const submitBtn = form.querySelector('button[type="submit"]');
    const originalText = submitBtn ? submitBtn.innerHTML : '';
    if (submitBtn) {
      submitBtn.disabled = true;
      submitBtn.innerHTML = '<span class="animate-pulse">Adding...</span>';
    }

    try {
      const formData = new FormData(form);
      formData.append('format', 'json');
      const res = await fetch('/cart/add/', {
        method: 'POST',
        headers: {
          'X-CSRFToken': csrftoken,
          'X-Requested-With': 'XMLHttpRequest'
        },
        body: formData
      });
      const data = await res.json();
      if (res.ok) {
        Toast.show(data.message || 'Added to your bag', 'success');
        this.updateBadgeCounts(data.total_items);
        this.open();
      } else {
        Toast.show(data.message || 'Could not add item.', 'error');
      }
    } catch (err) {
      Toast.show('Error updating bag.', 'error');
    } finally {
      if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalText;
      }
    }
  },

  async refreshDrawer() {
    try {
      const res = await fetch('/cart/drawer-data/');
      const data = await res.json();
      this.renderDrawerContent(data);
      this.updateBadgeCounts(data.total_items);
    } catch (err) {
      console.error('Error fetching cart drawer data', err);
    }
  },

  renderDrawerContent(data) {
    if (!this.itemsContainer) return;

    if (!data.items || data.items.length === 0) {
      this.itemsContainer.innerHTML = `
        <div class="py-12 px-4 text-center">
          <div class="w-16 h-16 mx-auto mb-4 rounded-full bg-[#FAF6F0] flex items-center justify-center text-2xl">🛍️</div>
          <p class="font-serif text-xl text-neutral-800 mb-2">Your cart is feeling a little empty.</p>
          <p class="text-xs text-neutral-500 mb-6 max-w-xs mx-auto">Explore thoughtful essentials crafted for a more conscious everyday.</p>
          <a href="/shop/" onclick="CartDrawer.close()" class="btn-primary text-xs py-3 px-6">Explore Catalog</a>
        </div>
      `;
      if (this.subtotalEl) this.subtotalEl.innerText = '₹0.00';
      if (this.progressFill) this.progressFill.style.width = '0%';
      if (this.progressText) this.progressText.innerText = '₹999 away from FREE SHIPPING';
      const checkoutBtn = document.getElementById('cart-drawer-checkout-btn');
      if (checkoutBtn) checkoutBtn.classList.add('opacity-50', 'pointer-events-none');
      return;
    }

    const checkoutBtn = document.getElementById('cart-drawer-checkout-btn');
    if (checkoutBtn) checkoutBtn.classList.remove('opacity-50', 'pointer-events-none');

    // Render line items
    let html = '';
    data.items.forEach(item => {
      html += `
        <div class="flex gap-4 py-4 border-b border-[#EAE4D9] items-center">
          <a href="${item.url}" class="w-20 h-24 bg-[#F5F2EB] rounded-lg overflow-hidden flex-shrink-0 border border-[#E8E2D5]">
            <img src="${item.image_url}" alt="${item.name}" class="w-full h-full object-cover">
          </a>
          <div class="flex-1 min-w-0">
            <div class="flex justify-between items-start">
              <div>
                <p class="text-[10px] tracking-widest uppercase text-neutral-400 font-semibold">${item.category}</p>
                <a href="${item.url}" class="font-medium text-sm text-neutral-900 truncate block hover:text-terracotta transition">${item.name}</a>
              </div>
              <button data-action="remove" data-item-id="${item.id}" class="text-neutral-400 hover:text-red-500 transition p-1" title="Remove item">
                <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
              </button>
            </div>
            
            <div class="flex justify-between items-center mt-3">
              <div class="flex items-center border border-[#DCD5C7] rounded-full bg-white px-2 py-0.5">
                <button data-action="decrease" data-item-id="${item.id}" class="w-5 h-5 flex items-center justify-center text-neutral-600 hover:text-black font-bold text-xs">-</button>
                <span class="px-2 text-xs font-semibold text-neutral-900">${item.quantity}</span>
                <button data-action="increase" data-item-id="${item.id}" class="w-5 h-5 flex items-center justify-center text-neutral-600 hover:text-black font-bold text-xs">+</button>
              </div>
              <span class="font-semibold text-sm text-neutral-900">₹${item.subtotal.toFixed(2)}</span>
            </div>
          </div>
        </div>
      `;
    });

    this.itemsContainer.innerHTML = html;
    if (this.subtotalEl) this.subtotalEl.innerText = `₹${data.subtotal.toFixed(2)}`;

    // Update Progress
    if (this.progressFill) this.progressFill.style.width = `${data.shipping_progress}%`;
    if (this.progressText) {
      if (data.free_shipping_unlocked) {
        this.progressText.innerHTML = '<span class="text-emerald-700 font-semibold">✦ You have unlocked FREE SHIPPING!</span>';
      } else {
        this.progressText.innerText = `₹${data.amount_to_free_shipping.toFixed(2)} away from FREE SHIPPING`;
      }
    }
  },

  async updateQuantity(itemId, action) {
    try {
      const formData = new FormData();
      formData.append('item_id', itemId);
      formData.append('action', action);
      const res = await fetch('/cart/update/', {
        method: 'POST',
        headers: {
          'X-CSRFToken': csrftoken,
          'X-Requested-With': 'XMLHttpRequest'
        },
        body: formData
      });
      const data = await res.json();
      if (res.ok) {
        this.refreshDrawer();
      } else {
        Toast.show(data.message || 'Cannot update quantity.', 'warning');
      }
    } catch (err) {
      Toast.show('Network error updating item.', 'error');
    }
  },

  async removeItem(itemId) {
    try {
      const formData = new FormData();
      formData.append('item_id', itemId);
      const res = await fetch('/cart/remove/', {
        method: 'POST',
        headers: {
          'X-CSRFToken': csrftoken,
          'X-Requested-With': 'XMLHttpRequest'
        },
        body: formData
      });
      const data = await res.json();
      if (res.ok) {
        Toast.show(data.message || 'Item removed.', 'info');
        this.refreshDrawer();
      }
    } catch (err) {
      Toast.show('Network error removing item.', 'error');
    }
  },

  updateBadgeCounts(count) {
    document.querySelectorAll('.cart-badge-count').forEach(el => {
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
  CartDrawer.init();
});
