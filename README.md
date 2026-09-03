# NOMA — Premium Gen-Z Sustainable Lifestyle Store

> **“Good things. Better vibes.”**
> *Beautiful things shouldn't cost the planet.*

![NOMA Hero Preview](/static/images/lifestyle/hero-composition.svg)

---

## ✦ Brand Concept & Aesthetic

**NOMA** is an editorial, modern, and eco-conscious lifestyle e-commerce platform crafted for Gen Z and young millennials. It represents **aesthetic sustainable living** — combining Pinterest & Instagram visual identity with high-utility, reusable, and giftable objects.

* **Palette**: Warm ivory (`#FAF8F5`), charcoal (`#1C1B19`), terracotta (`#C86D51`), soft beige (`#F3EFE6`), muted sage (`#7B8C78`), and warm copper (`#C57D56`).
* **Typography**: *Italiana* & *Playfair Display* editorial serifs paired with clean *Plus Jakarta Sans* body type.
* **Core Philosophy**: Things you actually want to own — thoughtfully designed, made to last, and easier on the planet.

---

## ✦ Features

### 🛍️ E-Commerce & Product Discovery
- **Homepage Editorial Experience**: Asymmetric hero layout, "The New Drop" carousel, Category Explorer ("Find Your Vibe"), Sustainability impact breakdown, "The Everyday Edit", customer reviews, and `@noma.everyday` community gallery.
- **Dynamic Shop Grid**: Real-time category selector, price range filters, availability toggles, and multi-mode sorting (*Featured, Newest, Price Low → High, Price High → Low, Best Selling*).
- **Product Detail Page (PDP)**: Multi-angle gallery with zoom, sustainability breakdown accordion, stock availability indicator, one-click buy-now, and customer review system.
- **Live Search Overlay**: Full-screen modal with trending query tags, matching categories, and live product search results.

### 🛒 Bag, Wishlist & Checkout
- **Interactive Slide-Over Cart Drawer**: Desktop slide-over & mobile bottom sheet with live free shipping progress tracker (*"₹350 away from FREE SHIPPING"*), line item quantity adjustments, and recommendations.
- **Coupon System**: Discount coupon engine with test code `NOMA10` (10% discount) and live cart calculation.
- **Wishlist**: Real-time heart toggle with instant navbar badge updates and "Move to Bag" workflow.
- **2-Column Minimal Checkout**: Saved address picker for logged-in members, new address form, and Cash on Delivery (COD) / simulated Razorpay test payment gateway.
- **Order Management**: Order tracking timeline (*Confirmed → Packed → Shipped → Out for Delivery → Delivered*), printable receipts, and customer dashboard.

### 👤 Customer Accounts & Admin
- **Member Authentication**: Secure registration, login, logout, profile editor, and saved address book management.
- **Customized Django Admin**: Searchable product catalog, order status workflow, coupon usage tracking, and review moderation.

---

## ✦ Quick Start & Development Setup

### 1. Prerequisites
- Python 3.9+ installed
- Git

### 2. Setup Virtual Environment

#### Windows (PowerShell / Command Prompt):
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
# Or for Command Prompt:
# venv\Scripts\activate.bat
```

#### macOS / Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Apply Database Migrations
```bash
python manage.py migrate
```

### 5. Seed Initial Catalog, Categories & Reviews
```bash
python manage.py seed_data
```

### 6. Run the Development Server
```bash
python manage.py runserver
```

Open your browser at **`http://127.0.0.1:8000/`**.

---

## ✦ Demo Accounts & Credentials

| Role | Username / Email | Password | Access |
| :--- | :--- | :--- | :--- |
| **Store Admin** | `admin` / `hello@nomalifestyle.com` | `admin123` | Django Admin (`/admin/`) & Full Storefront |
| **Customer** | `ananya_m` / `ananya@example.com` | `password123` | Storefront & Customer Dashboard (`/account/`) |

### Test Coupon Code:
* Code: **`NOMA10`**
* Benefit: **10% OFF** on orders above ₹499.

---

## ✦ Initial Product Catalog

| # | Product Name | Category | Price | Badge | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | **Aura Copper Bottle** | Drinkware | ₹1,499 (₹1,299) | `BESTSELLER` | Minimalist Ayurvedic copper bottle for everyday hydration. |
| 2 | **Copper Water Recharge Balls** | Wellness | ₹799 | `NEW` | Reusable solid 99.8% copper spheres for intentional water rituals. |
| 3 | **Cloud Reusable Tumbler** | Drinkware | ₹999 (₹899) | `NOMA PICK` | 480ml double-wall vacuum insulated matte tumbler with slider lid. |
| 4 | **Bamboo Desk Edit** | Workspace | ₹699 | `LIMITED` | Sustainable Moso bamboo organizer for a calmer, decluttered desk. |
| 5 | **Slow Sunday Soy Candle** | Home & Living | ₹599 | `NEW` | Hand-poured soy wax in a reusable ceramic vessel with hinoki & amber notes. |

---

## ✦ Running Automated Tests

Run the complete test suite:
```bash
python manage.py test
```

---

## ✦ Project Structure

```
ECOM/
├── manage.py
├── requirements.txt
├── .env.example
├── README.md
├── config/             # Project settings & URL routing
├── accounts/           # User authentication, profiles, address book
├── products/           # Categories, products, image gallery, search API
├── cart/               # Cart, CartItem, AJAX endpoints, drawer data
├── wishlist/           # Wishlist, WishlistItem, AJAX toggle
├── orders/             # Order creation, checkout, payments, tracking
├── coupons/            # Coupon model, discount engine, validation
├── reviews/            # Verified customer reviews & rating breakdown
├── core/               # Static pages, seed_data management command
├── templates/          # Semantic HTML5 templates & modular components
├── static/             # Custom CSS design tokens, JS modules, SVG assets
└── media/              # User-uploaded product media
```

---

*Crafted with intention for modern, aesthetic, conscious living.* ✦
