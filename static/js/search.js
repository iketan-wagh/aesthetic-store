/**
 * NOMA Live Search Overlay
 */

const SearchModal = {
  overlay: null,
  input: null,
  resultsContainer: null,
  debounceTimer: null,

  init() {
    this.overlay = document.getElementById('search-overlay');
    this.input = document.getElementById('search-overlay-input');
    this.resultsContainer = document.getElementById('search-overlay-results');
    this.closeBtn = document.getElementById('search-overlay-close');
    this.defaultView = document.getElementById('search-default-view');
    this.liveView = document.getElementById('search-live-view');

    // Open triggers
    document.querySelectorAll('.search-trigger-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        this.open();
      });
    });

    if (this.closeBtn) this.closeBtn.addEventListener('click', () => this.close());
    
    // Close on Escape
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && this.isOpen()) {
        this.close();
      }
    });

    // Tag click triggers search
    document.querySelectorAll('.search-tag-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const query = btn.dataset.query;
        if (this.input) {
          this.input.value = query;
          this.performSearch(query);
        }
      });
    });

    // Search input live handler
    if (this.input) {
      this.input.addEventListener('input', (e) => {
        const query = e.target.value.trim();
        clearTimeout(this.debounceTimer);
        this.debounceTimer = setTimeout(() => {
          this.performSearch(query);
        }, 220);
      });
    }
  },

  isOpen() {
    return this.overlay && !this.overlay.classList.contains('hidden');
  },

  open() {
    if (!this.overlay) return;
    this.overlay.classList.remove('hidden');
    document.body.style.overflow = 'hidden';
    setTimeout(() => {
      if (this.input) this.input.focus();
    }, 100);
  },

  close() {
    if (!this.overlay) return;
    this.overlay.classList.add('hidden');
    document.body.style.overflow = '';
  },

  async performSearch(query) {
    if (!query) {
      if (this.defaultView) this.defaultView.classList.remove('hidden');
      if (this.liveView) this.liveView.classList.add('hidden');
      return;
    }

    if (this.defaultView) this.defaultView.classList.add('hidden');
    if (this.liveView) this.liveView.classList.remove('hidden');

    try {
      const res = await fetch(`/shop/api/search/?q=${encodeURIComponent(query)}`);
      const data = await res.json();
      this.renderResults(data, query);
    } catch (err) {
      console.error('Search query error', err);
    }
  },

  renderResults(data, query) {
    if (!this.resultsContainer) return;

    if (data.count === 0) {
      this.resultsContainer.innerHTML = `
        <div class="py-16 text-center">
          <p class="font-serif text-2xl text-neutral-800 mb-2">Nothing matched that vibe.</p>
          <p class="text-sm text-neutral-500 max-w-sm mx-auto mb-6">We couldn't find anything matching "${query}". Try searching for copper, drinkware, candle, or desk.</p>
          <a href="/shop/" onclick="SearchModal.close()" class="btn-secondary text-xs py-2 px-6">View All Pieces</a>
        </div>
      `;
      return;
    }

    let html = '';
    
    // Matching categories
    if (data.categories && data.categories.length > 0) {
      html += `
        <div class="mb-6">
          <p class="text-xs tracking-widest uppercase text-neutral-400 font-semibold mb-3">Categories</p>
          <div class="flex flex-wrap gap-2">
            ${data.categories.map(c => `
              <a href="${c.url}" onclick="SearchModal.close()" class="text-xs px-3 py-1.5 rounded-full bg-[#EFEAE1] hover:bg-terracotta hover:text-white transition font-medium text-neutral-800">
                ${c.name} →
              </a>
            `).join('')}
          </div>
        </div>
      `;
    }

    // Matching products grid
    html += `
      <div>
        <p class="text-xs tracking-widest uppercase text-neutral-400 font-semibold mb-4">Products (${data.count})</p>
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
          ${data.results.map(p => `
            <a href="${p.url}" onclick="SearchModal.close()" class="group block p-2 rounded-xl bg-white border border-[#ECE6DB] hover:border-terracotta transition">
              <div class="aspect-[4/5] rounded-lg overflow-hidden bg-[#F7F4EE] mb-2 relative">
                <img src="${p.image_url}" alt="${p.name}" class="w-full h-full object-cover group-hover:scale-105 transition duration-300">
                ${p.badge ? `<span class="absolute top-2 left-2 text-[9px] font-bold px-2 py-0.5 rounded-full bg-charcoal text-white">${p.badge}</span>` : ''}
              </div>
              <p class="text-[10px] uppercase tracking-wider text-neutral-400 font-semibold">${p.category}</p>
              <h4 class="font-medium text-xs text-neutral-900 truncate group-hover:text-terracotta transition">${p.name}</h4>
              <p class="font-semibold text-xs text-neutral-900 mt-1">₹${p.current_price.toFixed(2)}</p>
            </a>
          `).join('')}
        </div>
      </div>
    `;

    this.resultsContainer.innerHTML = html;
  }
};

document.addEventListener('DOMContentLoaded', () => {
  SearchModal.init();
});
