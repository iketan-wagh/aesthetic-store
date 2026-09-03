/**
 * NOMA Main JavaScript & Utility Functions
 */

// CSRF Cookie Helper
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

const csrftoken = getCookie('csrftoken');

// Toast Notification Manager
const Toast = {
  show(message, type = 'info', duration = 3500) {
    let container = document.getElementById('toast-container');
    if (!container) {
      container = document.createElement('div');
      container.id = 'toast-container';
      container.className = 'toast-container';
      document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = 'toast-item';
    
    let icon = '✦';
    if (type === 'success') icon = '✓';
    if (type === 'error') icon = '✕';
    if (type === 'warning') icon = '⚠';

    toast.innerHTML = `
      <div class="flex items-center gap-3">
        <span class="text-[#C86D51] font-bold text-base">${icon}</span>
        <span class="text-white font-medium">${message}</span>
      </div>
      <button onclick="this.parentElement.remove()" class="text-gray-400 hover:text-white transition">
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
      </button>
    `;

    container.appendChild(toast);

    setTimeout(() => {
      if (toast.parentElement) {
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(10px)';
        toast.style.transition = 'all 0.3s ease';
        setTimeout(() => toast.remove(), 300);
      }
    }, duration);
  }
};

// Newsletter Form Handler
document.addEventListener('DOMContentLoaded', () => {
  const newsletterForms = document.querySelectorAll('.newsletter-form');
  newsletterForms.forEach(form => {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const input = form.querySelector('input[name="email"]');
      const email = input.value.trim();
      if (!email) return;

      const submitBtn = form.querySelector('button[type="submit"]');
      const originalText = submitBtn ? submitBtn.innerHTML : 'Join';
      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = 'Joining...';
      }

      try {
        const formData = new FormData();
        formData.append('email', email);
        const res = await fetch('/api/newsletter/', {
          method: 'POST',
          headers: {
            'X-CSRFToken': csrftoken,
          },
          body: formData
        });
        const data = await res.json();
        if (res.ok) {
          Toast.show(data.message, 'success');
          input.value = '';
        } else {
          Toast.show(data.message || 'Something went wrong.', 'error');
        }
      } catch (err) {
        Toast.show('Network error. Please try again.', 'error');
      } finally {
        if (submitBtn) {
          submitBtn.disabled = false;
          submitBtn.innerHTML = originalText;
        }
      }
    });
  });

  // Mobile Menu Toggle
  const mobileMenuBtn = document.getElementById('mobile-menu-btn');
  const mobileMenuDrawer = document.getElementById('mobile-menu-drawer');
  const mobileMenuClose = document.getElementById('mobile-menu-close');
  const mobileMenuOverlay = document.getElementById('mobile-menu-overlay');

  if (mobileMenuBtn && mobileMenuDrawer) {
    const openMenu = () => {
      mobileMenuDrawer.classList.remove('hidden');
      if (mobileMenuOverlay) mobileMenuOverlay.classList.remove('hidden');
      setTimeout(() => {
        mobileMenuDrawer.classList.remove('-translate-x-full');
      }, 10);
      document.body.style.overflow = 'hidden';
    };

    const closeMenu = () => {
      mobileMenuDrawer.classList.add('-translate-x-full');
      if (mobileMenuOverlay) mobileMenuOverlay.classList.add('hidden');
      document.body.style.overflow = '';
      setTimeout(() => {
        mobileMenuDrawer.classList.add('hidden');
      }, 300);
    };

    mobileMenuBtn.addEventListener('click', openMenu);
    if (mobileMenuClose) mobileMenuClose.addEventListener('click', closeMenu);
    if (mobileMenuOverlay) mobileMenuOverlay.addEventListener('click', closeMenu);
  }

  // Sticky Navbar Scroll Elevation
  const header = document.getElementById('site-header');
  if (header) {
    window.addEventListener('scroll', () => {
      if (window.scrollY > 20) {
        header.classList.add('shadow-sm', 'bg-white/95', 'backdrop-blur-md');
        header.classList.remove('bg-[#FAF8F5]');
      } else {
        header.classList.remove('shadow-sm', 'bg-white/95', 'backdrop-blur-md');
        header.classList.add('bg-[#FAF8F5]');
      }
    });
  }
});
