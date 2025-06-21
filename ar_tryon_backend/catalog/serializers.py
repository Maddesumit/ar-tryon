"""
Serializers for catalog app API
"""
from rest_framework import serializers
from .models import Product, Category, Brand, ProductImage


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category model"""
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'image']


class BrandSerializer(serializers.ModelSerializer):
    """Serializer for Brand model"""
    
    class Meta:
        model = Brand
        fields = ['id', 'name', 'slug', 'description', 'logo', 'website']


class ProductImageSerializer(serializers.ModelSerializer):
    """Serializer for ProductImage model"""
    
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'alt_text', 'is_primary', 'sort_order']


class ProductSerializer(serializers.ModelSerializer):
    """Serializer for Product model"""
    category = CategorySerializer(read_only=True)
    brand = BrandSerializer(read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    
    # Computed fields
    average_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'description', 'short_description', 'price', 'sale_price',
            'category', 'brand', 'gender', 'available_sizes', 'available_colors', 
            'stock_quantity', 'is_available', 'is_try_on_enabled', 'try_on_category',
            'is_featured', 'is_active', 'created_at', 'updated_at', 'images', 
            'average_rating', 'review_count'
        ]
    
    def get_average_rating(self, obj):
        """Calculate average rating for the product"""
        # For now, return a placeholder value
        # In a real app, this would calculate from actual reviews
        return 4.2
    
    def get_review_count(self, obj):
        """Get review count for the product"""
        # For now, return a placeholder value
        # In a real app, this would count actual reviews
        return 156
