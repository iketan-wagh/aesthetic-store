from django.contrib import admin
from .models import Category, Product, ProductImage


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 2
    fields = ('image', 'alt_text', 'is_primary', 'display_order')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'tagline', 'is_featured', 'display_order', 'created_at')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('is_featured', 'display_order')
    search_fields = ('name', 'description')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'discount_price', 'stock', 'badge', 'is_featured', 'is_bestseller', 'is_new_drop', 'is_active')
    list_filter = ('category', 'badge', 'is_featured', 'is_bestseller', 'is_new_drop', 'is_active')
    list_editable = ('price', 'discount_price', 'stock', 'badge', 'is_featured', 'is_bestseller', 'is_new_drop', 'is_active')
    search_fields = ('name', 'sku', 'description', 'tags', 'materials')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline]
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'sku', 'category', 'badge', 'tags')
        }),
        ('Pricing & Inventory', {
            'fields': ('price', 'discount_price', 'stock', 'is_active')
        }),
        ('Editorial & Descriptions', {
            'fields': ('short_description', 'description')
        }),
        ('Sustainability & Craft Specs', {
            'fields': ('materials', 'dimensions', 'care_instructions', 'sustainability_notes', 'packaging_notes', 'lifespan_notes')
        }),
        ('Flags & Merchandising', {
            'fields': ('is_featured', 'is_bestseller', 'is_new_drop')
        }),
    )


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('product', 'alt_text', 'is_primary', 'display_order')
    list_filter = ('is_primary',)
    search_fields = ('product__name', 'alt_text')
