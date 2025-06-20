"""
Models for catalog app.
This app handles product catalog functionality including categories, brands, and products.
"""

from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from PIL import Image
import os

class Category(models.Model):
    """
    Product categories (e.g., Shirts, Pants, Dresses, etc.)
    Categories help organize products and make browsing easier.
    """
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, help_text="URL-friendly version of name")
    description = models.TextField(blank=True, help_text="Brief description of the category")
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    
    # SEO and organization
    is_active = models.BooleanField(default=True, help_text="Whether this category is shown to users")
    sort_order = models.IntegerField(default=0, help_text="Lower numbers appear first")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Categories"  # Correct plural form
        ordering = ['sort_order', 'name']
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        """URL for this category"""
        return reverse('catalog:category_detail', kwargs={'slug': self.slug})

class Brand(models.Model):
    """
    Clothing brands (e.g., Nike, Adidas, Zara, etc.)
    """
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to='brands/', blank=True, null=True)
    website = models.URLField(blank=True, help_text="Brand's official website")
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('catalog:brand_detail', kwargs={'slug': self.slug})

class Product(models.Model):
    """
    Individual products/clothing items.
    This is the main model for items users can try on.
    """
    # Basic information
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(help_text="Detailed product description")
    short_description = models.CharField(max_length=255, help_text="Brief description for listings")
    
    # Relationships
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='products')
    
    # Pricing
    price = models.DecimalField(max_digits=10, decimal_places=2)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    # Product details
    GENDER_CHOICES = [
        ('M', 'Men'),
        ('F', 'Women'),
        ('U', 'Unisex'),
        ('K', 'Kids'),
    ]
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default='U')
    
    # Sizes available (we'll improve this in later phases)
    available_sizes = models.CharField(
        max_length=50, 
        default='S,M,L,XL',
        help_text="Comma-separated list of available sizes"
    )
    
    # Colors available
    available_colors = models.CharField(
        max_length=100,
        default='Black,White',
        help_text="Comma-separated list of available colors"
    )
    
    # Inventory
    stock_quantity = models.PositiveIntegerField(default=0)
    is_available = models.BooleanField(default=True)
    
    # Try-on specific fields
    is_try_on_enabled = models.BooleanField(
        default=True, 
        help_text="Whether this product supports virtual try-on"
    )
    try_on_category = models.CharField(
        max_length=50,
        choices=[
            ('tops', 'Tops (shirts, t-shirts, sweaters)'),
            ('bottoms', 'Bottoms (pants, shorts, skirts)'),
            ('dresses', 'Dresses'),
            ('outerwear', 'Outerwear (jackets, coats)'),
            ('accessories', 'Accessories'),
        ],
        default='tops',
        help_text="Category for try-on processing"
    )
    
    # SEO and metadata
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.CharField(max_length=300, blank=True)
    
    # Status and timestamps
    is_featured = models.BooleanField(default=False, help_text="Show in featured products")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['category', 'is_active']),
            models.Index(fields=['brand', 'is_active']),
            models.Index(fields=['is_featured', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.brand.name} - {self.name}"
    
    def get_absolute_url(self):
        return reverse('catalog:product_detail', kwargs={'slug': self.slug})
    
    @property
    def current_price(self):
        """Return sale price if available, otherwise regular price"""
        return self.sale_price if self.sale_price else self.price
    
    @property
    def is_on_sale(self):
        """Check if product is currently on sale"""
        return self.sale_price is not None and self.sale_price < self.price
    
    @property
    def discount_percentage(self):
        """Calculate discount percentage if on sale"""
        if self.is_on_sale:
            return int(((self.price - self.sale_price) / self.price) * 100)
        return 0
    
    def get_available_sizes_list(self):
        """Convert comma-separated sizes to list"""
        return [size.strip() for size in self.available_sizes.split(',') if size.strip()]
    
    def get_available_colors_list(self):
        """Convert comma-separated colors to list"""
        return [color.strip() for color in self.available_colors.split(',') if color.strip()]

class ProductImage(models.Model):
    """
    Product images. Each product can have multiple images.
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/')
    alt_text = models.CharField(max_length=200, help_text="Alternative text for accessibility")
    is_primary = models.BooleanField(default=False, help_text="Main product image")
    sort_order = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['sort_order', 'created_at']
    
    def __str__(self):
        return f"{self.product.name} - Image {self.id}"
    
    def save(self, *args, **kwargs):
        """
        Override save to handle primary image logic and resize images.
        """
        # If this is being set as primary, unset all other primary images for this product
        if self.is_primary:
            ProductImage.objects.filter(product=self.product, is_primary=True).update(is_primary=False)
        
        super().save(*args, **kwargs)
        
        # Resize image if it's too large
        if self.image:
            try:
                img = Image.open(self.image.path)
                if img.height > 800 or img.width > 800:
                    output_size = (800, 800)
                    img.thumbnail(output_size)
                    img.save(self.image.path)
            except Exception as e:
                # If image processing fails, continue
                pass

class ProductReview(models.Model):
    """
    Product reviews from users.
    This will help build trust and provide feedback.
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='product_reviews')
    
    rating = models.IntegerField(
        choices=[(i, f"{i} Star{'s' if i != 1 else ''}") for i in range(1, 6)],
        help_text="Rating from 1 to 5 stars"
    )
    title = models.CharField(max_length=200, help_text="Review title")
    content = models.TextField(help_text="Detailed review")
    
    # Additional review details
    size_purchased = models.CharField(max_length=10, blank=True)
    color_purchased = models.CharField(max_length=50, blank=True)
    
    # Moderation
    is_approved = models.BooleanField(default=True)
    is_verified_purchase = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['product', 'user']  # One review per user per product
    
    def __str__(self):
        return f"{self.user.username} - {self.product.name} ({self.rating}/5)"
