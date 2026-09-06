# House of Aesthetics — Conscious Lifestyle & Wellness Store

> **“Good things. Better vibes.”**  
> *Everyday essentials crafted with intention and built to last.*

---

## ✦ Brand Concept & Overview

**House of Aesthetics** is a modern, eco-conscious direct-to-consumer (D2C) e-commerce platform. It combines an editorial visual identity with high-utility, sustainable, and giftable lifestyle objects — from pure Ayurvedic copperware and natural gemstone decor to minimalist desk and home accessories.

* **Palette**: Warm ivory (`#FAF8F5`), charcoal (`#1C1B19`), terracotta (`#C86D51`), soft beige (`#F3EFE6`), and warm copper (`#C57D56`).
* **Core Philosophy**: Beautiful. Useful. Conscious. Objects you'll actually want to keep.

---

## ✦ Key Features

### 🛍️ E-Commerce & Product Discovery
- **Editorial Storefront**: Hero banner, category explorer, conscious living manifesto, and customer review showcases.
- **Dynamic Catalog Grid**: Real-time category filtering, price range sorting, and stock status indicators.
- **Product Detail Pages (PDP)**: Multi-angle image galleries with interactive thumbnail switchers, sustainability notes, and customer reviews.
- **Live Search Overlay**: Full-screen modal with instant real-time search suggestions.

### 🛒 Bag, Wishlist & Checkout
- **Interactive Slide-Over Bag**: Live subtotal calculations, free shipping threshold progress bar, and quantity adjustments.
- **Coupon System**: Promo code engine supporting percentage discounts, minimum order thresholds, and usage limits.
- **Customer Wishlist**: Real-time heart toggles with navbar badge counters and one-click "Move to Bag".
- **Secure Multi-Channel Checkout**: Saved customer address book, Cash on Delivery (COD), and Razorpay payment gateway integration.
- **Order Tracking & Receipts**: Real-time order tracking timeline, printable invoices, and customer order history.

### 🔐 Authentication & Security
- **Customer Accounts**: Secure registration, login, logout, password reset flow, and profile management.
- **Zero-Secret Architecture**: All credentials, database URLs, and API keys are strictly loaded through `.env` and environment variables.
- **Cloud Email Dispatcher**: Multi-strategy fallback dispatcher supporting HTTPS REST APIs (Brevo & Resend on Port 443) and standard SMTP.

---

## ✦ Quick Start & Local Development Setup

### 1. Prerequisites
- Python 3.9+
- Git

### 2. Clone the Repository
```bash
git clone https://github.com/iketan-wagh/aesthetic-store.git
cd aesthetic-store
```

### 3. Setup Virtual Environment

#### Windows (PowerShell):
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

#### macOS / Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables
Copy `.env.example` to create your private `.env` file:
```bash
cp .env.example .env
```
Update `.env` with your custom `SECRET_KEY`, database configuration, and API keys.

### 6. Run Database Migrations
```bash
python manage.py migrate
```

### 7. Seed Initial Catalog & Create Admin
```bash
python manage.py seed_data
```
*Or create a custom admin user:*
```bash
python manage.py createsuperuser
```

### 8. Run Development Server
```bash
python manage.py runserver
```
Visit **`http://127.0.0.1:8000/`** in your browser.

---

## ✦ Running Automated Tests

Run the full Django unit test suite:
```bash
python manage.py test --noinput
```

---

## ✦ Project Architecture

```text
ECOM/
├── .env.example               # Environment variables template
├── .gitignore                 # Secrets and temporary file exclusions
├── manage.py                  # Django CLI runner
├── requirements.txt           # Python dependencies
├── Procfile                   # Web worker definition for cloud deployment
│
├── config/                    # Root configuration & URL routing
├── accounts/                  # Authentication, profile & password reset
├── cart/                      # Cart sessions, items & slide-over drawer
├── core/                      # CMS pages, context processors & email dispatcher
├── coupons/                   # Coupon discounts & validation engine
├── dashboard/                 # Staff admin operations & inventory management
├── orders/                    # Checkout processing, tracking & receipts
├── products/                  # Product catalog, categories & galleries
├── reviews/                   # Customer star ratings & feedback
├── wishlist/                  # Wishlist context & storage
│
├── static/                    # CSS stylesheets, JS scripts & fallback assets
└── templates/                 # Reusable Django templates & email HTML/TXT
```

---

## ✦ License

This project is proprietary and confidential. All rights reserved.
