from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from django.db.models import Avg


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    tagline = models.CharField(max_length=255, blank=True, default='')
    description = models.TextField(blank=True, default='')
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    is_featured = models.BooleanField(default=False)
    display_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['display_order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('products:category_detail', kwargs={'slug': self.slug})


class Product(models.Model):
    BADGE_CHOICES = (
        ('NONE', 'None'),
        ('NEW', 'NEW'),
        ('BESTSELLER', 'BESTSELLER'),
        ('LIMITED', 'LIMITED'),
        ('NOMA_PICK', 'NOMA PICK'),
    )

    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    sku = models.CharField(max_length=50, unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    stock = models.PositiveIntegerField(default=25)
    
    short_description = models.CharField(max_length=300)
    description = models.TextField()
    
    badge = models.CharField(max_length=20, choices=BADGE_CHOICES, default='NONE')
    tags = models.CharField(max_length=255, help_text="Comma-separated tags e.g. Sustainable, Bestseller, Everyday", default='Sustainable')
    
    # Sustainability & Specification details
    materials = models.TextField(blank=True, default='')
    dimensions = models.CharField(max_length=200, blank=True, default='')
    care_instructions = models.TextField(blank=True, default='')
    sustainability_notes = models.TextField(blank=True, default='')
    packaging_notes = models.CharField(max_length=300, blank=True, default='100% Recyclable, plastic-free kraft packaging.')
    lifespan_notes = models.CharField(max_length=200, blank=True, default='Built for enduring everyday use.')
    
    # Flags & Ordering
    is_featured = models.BooleanField(default=False)
    is_bestseller = models.BooleanField(default=False)
    is_new_drop = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    view_count = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_featured', '-created_at']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('products:product_detail', kwargs={'slug': self.slug})

    @property
    def current_price(self):
        return self.discount_price if self.discount_price and self.discount_price < self.price else self.price

    @property
    def has_discount(self):
        return bool(self.discount_price and self.discount_price < self.price)

    @property
    def discount_percent(self):
        if self.has_discount and self.price > 0:
            return int(((self.price - self.discount_price) / self.price) * 100)
        return 0

    @property
    def in_stock(self):
        return self.stock > 0

    @property
    def tag_list(self):
        if self.tags:
            return [t.strip() for t in self.tags.split(',') if t.strip()]
        return []

    @property
    def primary_image_obj(self):
        if hasattr(self, '_prefetched_objects_cache') and 'images' in self._prefetched_objects_cache:
            imgs = self.images.all()
            for img in imgs:
                if img.is_primary:
                    return img
            return imgs[0] if imgs else None
        img = self.images.filter(is_primary=True).first()
        if not img:
            img = self.images.first()
        return img

    @property
    def primary_image_url(self):
        img = self.primary_image_obj
        if img and img.image:
            return img.image.url
        return f"/static/images/products/{self.slug}.jpg"

    @property
    def secondary_image_url(self):
        if hasattr(self, '_prefetched_objects_cache') and 'images' in self._prefetched_objects_cache:
            imgs = list(self.images.all())
            if len(imgs) > 1:
                return imgs[1].image.url if imgs[1].image else f"/static/images/products/{self.slug}-2.jpg"
            return f"/static/images/products/{self.slug}-2.jpg"
        imgs = self.images.all()
        if len(imgs) > 1:
            return imgs[1].image.url if imgs[1].image else f"/static/images/products/{self.slug}-2.jpg"
        return f"/static/images/products/{self.slug}-2.jpg"

    @property
    def average_rating(self):
        if hasattr(self, '_prefetched_objects_cache') and 'reviews' in self._prefetched_objects_cache:
            approved_reviews = [r.rating for r in self.reviews.all() if r.is_approved]
            if approved_reviews:
                return round(sum(approved_reviews) / len(approved_reviews), 1)
            return 5.0
        avg = self.reviews.filter(is_approved=True).aggregate(Avg('rating'))['rating__avg']
        return round(avg, 1) if avg else 5.0

    @property
    def review_count(self):
        if hasattr(self, '_prefetched_objects_cache') and 'reviews' in self._prefetched_objects_cache:
            return sum(1 for r in self.reviews.all() if r.is_approved)
        return self.reviews.filter(is_approved=True).count()


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    alt_text = models.CharField(max_length=200, blank=True, default='')
    is_primary = models.BooleanField(default=False)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-is_primary', 'display_order']

    def __str__(self):
        return f"{self.product.name} Image ({'Primary' if self.is_primary else 'Gallery'})"
