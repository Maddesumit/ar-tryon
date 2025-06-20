"""
Django management command to populate the catalog with sample data.
This helps us test the catalog functionality with realistic data.
"""

from django.core.management.base import BaseCommand
from django.utils.text import slugify
from catalog.models import Category, Brand, Product
import random

class Command(BaseCommand):
    help = 'Populate the catalog with sample data for testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before populating',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing data...')
            Product.objects.all().delete()
            Brand.objects.all().delete()
            Category.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Data cleared.'))

        # Create Categories
        categories_data = [
            {
                'name': 'T-Shirts',
                'description': 'Comfortable and stylish t-shirts for everyday wear',
                'sort_order': 1
            },
            {
                'name': 'Shirts',
                'description': 'Formal and casual shirts for all occasions',
                'sort_order': 2
            },
            {
                'name': 'Jeans',
                'description': 'Denim jeans in various styles and fits',
                'sort_order': 3
            },
            {
                'name': 'Dresses',
                'description': 'Beautiful dresses for every occasion',
                'sort_order': 4
            },
            {
                'name': 'Jackets',
                'description': 'Stylish jackets and outerwear',
                'sort_order': 5
            },
            {
                'name': 'Sneakers',
                'description': 'Comfortable and trendy sneakers',
                'sort_order': 6
            },
        ]

        categories = {}
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={
                    'slug': slugify(cat_data['name']),
                    'description': cat_data['description'],
                    'sort_order': cat_data['sort_order'],
                    'is_active': True
                }
            )
            categories[cat_data['name']] = category
            if created:
                self.stdout.write(f'Created category: {category.name}')

        # Create Brands
        brands_data = [
            {
                'name': 'Nike',
                'description': 'Just Do It - Leading sportswear brand'
            },
            {
                'name': 'Adidas',
                'description': 'Impossible is Nothing - Global sportswear manufacturer'
            },
            {
                'name': 'Zara',
                'description': 'Fast fashion retailer with trendy designs'
            },
            {
                'name': 'H&M',
                'description': 'Affordable fashion for everyone'
            },
            {
                'name': 'Uniqlo',
                'description': 'Quality basics and innovative fabrics'
            },
            {
                'name': 'Levi\'s',
                'description': 'Original jeans company since 1853'
            },
        ]

        brands = {}
        for brand_data in brands_data:
            brand, created = Brand.objects.get_or_create(
                name=brand_data['name'],
                defaults={
                    'slug': slugify(brand_data['name']),
                    'description': brand_data['description'],
                    'is_active': True
                }
            )
            brands[brand_data['name']] = brand
            if created:
                self.stdout.write(f'Created brand: {brand.name}')

        # Create Products
        products_data = [
            # T-Shirts
            {
                'name': 'Classic Cotton T-Shirt',
                'category': 'T-Shirts',
                'brand': 'Uniqlo',
                'price': 19.99,
                'gender': 'U',
                'try_on_category': 'tops',
                'description': 'Soft, comfortable cotton t-shirt perfect for everyday wear.',
                'short_description': 'Comfortable cotton tee for daily wear',
                'available_sizes': 'XS,S,M,L,XL,XXL',
                'available_colors': 'White,Black,Navy,Gray,Red',
                'is_featured': True
            },
            {
                'name': 'Dri-FIT Running Tee',
                'category': 'T-Shirts',
                'brand': 'Nike',
                'price': 29.99,
                'sale_price': 24.99,
                'gender': 'U',
                'try_on_category': 'tops',
                'description': 'Moisture-wicking t-shirt designed for active lifestyle.',
                'short_description': 'Performance tee with moisture-wicking technology',
                'available_sizes': 'S,M,L,XL',
                'available_colors': 'Black,White,Blue,Green',
                'is_featured': True
            },
            
            # Shirts
            {
                'name': 'Oxford Button-Down Shirt',
                'category': 'Shirts',
                'brand': 'Uniqlo',
                'price': 39.99,
                'gender': 'M',
                'try_on_category': 'tops',
                'description': 'Classic oxford shirt perfect for business casual or smart casual looks.',
                'short_description': 'Classic oxford button-down shirt',
                'available_sizes': 'S,M,L,XL',
                'available_colors': 'White,Blue,Pink,Light Blue',
            },
            {
                'name': 'Linen Casual Shirt',
                'category': 'Shirts',
                'brand': 'Zara',
                'price': 49.99,
                'gender': 'M',
                'try_on_category': 'tops',
                'description': 'Lightweight linen shirt perfect for summer.',
                'short_description': 'Lightweight summer linen shirt',
                'available_sizes': 'S,M,L,XL',
                'available_colors': 'White,Beige,Navy,Light Green',
            },
            
            # Jeans
            {
                'name': '501 Original Fit Jeans',
                'category': 'Jeans',
                'brand': 'Levi\'s',
                'price': 89.99,
                'gender': 'U',
                'try_on_category': 'bottoms',
                'description': 'The original blue jean since 1873. Straight fit with iconic styling.',
                'short_description': 'Classic straight-fit jeans',
                'available_sizes': '28,30,32,34,36,38',
                'available_colors': 'Dark Blue,Light Blue,Black',
                'is_featured': True
            },
            {
                'name': 'Skinny Fit Jeans',
                'category': 'Jeans',
                'brand': 'H&M',
                'price': 34.99,
                'gender': 'F',
                'try_on_category': 'bottoms',
                'description': 'Modern skinny fit jeans with stretch for comfort.',
                'short_description': 'Comfortable skinny fit jeans',
                'available_sizes': '25,26,27,28,29,30',
                'available_colors': 'Dark Blue,Black,Gray',
            },
            
            # Dresses
            {
                'name': 'Floral Summer Dress',
                'category': 'Dresses',
                'brand': 'Zara',
                'price': 59.99,
                'sale_price': 39.99,
                'gender': 'F',
                'try_on_category': 'dresses',
                'description': 'Beautiful floral print dress perfect for summer occasions.',
                'short_description': 'Elegant floral summer dress',
                'available_sizes': 'XS,S,M,L,XL',
                'available_colors': 'Blue Floral,Pink Floral,White Floral',
                'is_featured': True
            },
            {
                'name': 'Little Black Dress',
                'category': 'Dresses',
                'brand': 'H&M',
                'price': 44.99,
                'gender': 'F',
                'try_on_category': 'dresses',
                'description': 'Classic little black dress suitable for any occasion.',
                'short_description': 'Versatile little black dress',
                'available_sizes': 'XS,S,M,L,XL',
                'available_colors': 'Black',
            },
            
            # Jackets
            {
                'name': 'Denim Jacket',
                'category': 'Jackets',
                'brand': 'Levi\'s',
                'price': 79.99,
                'gender': 'U',
                'try_on_category': 'outerwear',
                'description': 'Classic denim jacket that never goes out of style.',
                'short_description': 'Timeless denim jacket',
                'available_sizes': 'S,M,L,XL',
                'available_colors': 'Light Blue,Dark Blue,Black',
            },
            {
                'name': 'Windbreaker Jacket',
                'category': 'Jackets',
                'brand': 'Nike',
                'price': 69.99,
                'gender': 'U',
                'try_on_category': 'outerwear',
                'description': 'Lightweight windbreaker perfect for outdoor activities.',
                'short_description': 'Lightweight windbreaker jacket',
                'available_sizes': 'S,M,L,XL',
                'available_colors': 'Black,Navy,Gray,Red',
            },
            
            # Sneakers
            {
                'name': 'Air Max 90',
                'category': 'Sneakers',
                'brand': 'Nike',
                'price': 119.99,
                'gender': 'U',
                'try_on_category': 'accessories',
                'description': 'Iconic Nike Air Max 90 with visible air cushioning.',
                'short_description': 'Classic Air Max sneakers',
                'available_sizes': '7,8,9,10,11,12',
                'available_colors': 'White,Black,Red,Blue',
                'is_featured': True,
                'is_try_on_enabled': False  # Shoes are harder to try on virtually
            },
            {
                'name': 'Stan Smith Sneakers',
                'category': 'Sneakers',
                'brand': 'Adidas',
                'price': 89.99,
                'gender': 'U',
                'try_on_category': 'accessories',
                'description': 'Classic white leather sneakers with green accents.',
                'short_description': 'Iconic white leather sneakers',
                'available_sizes': '7,8,9,10,11,12',
                'available_colors': 'White/Green,White/Navy,All White',
                'is_try_on_enabled': False
            },
        ]

        for product_data in products_data:
            category = categories[product_data['category']]
            brand = brands[product_data['brand']]
            
            product, created = Product.objects.get_or_create(
                name=product_data['name'],
                brand=brand,
                defaults={
                    'slug': slugify(f"{brand.name}-{product_data['name']}"),
                    'category': category,
                    'price': product_data['price'],
                    'sale_price': product_data.get('sale_price'),
                    'gender': product_data['gender'],
                    'try_on_category': product_data['try_on_category'],
                    'description': product_data['description'],
                    'short_description': product_data['short_description'],
                    'available_sizes': product_data['available_sizes'],
                    'available_colors': product_data['available_colors'],
                    'stock_quantity': random.randint(10, 100),
                    'is_available': True,
                    'is_featured': product_data.get('is_featured', False),
                    'is_try_on_enabled': product_data.get('is_try_on_enabled', True),
                    'meta_title': f"{product_data['name']} - {brand.name}",
                    'meta_description': product_data['short_description']
                }
            )
            
            if created:
                self.stdout.write(f'Created product: {product.name}')

        # Show summary
        total_categories = Category.objects.count()
        total_brands = Brand.objects.count()
        total_products = Product.objects.count()

        self.stdout.write(
            self.style.SUCCESS(
                f'\nSample data populated successfully!\n'
                f'Categories: {total_categories}\n'
                f'Brands: {total_brands}\n'
                f'Products: {total_products}\n'
            )
        )
