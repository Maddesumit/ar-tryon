"""
Django management command to add product images from online APIs.
This will fetch real product images and associate them with our products.
"""

import requests
import os
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.conf import settings
from catalog.models import Product, ProductImage
import time
import json

class Command(BaseCommand):
    help = 'Add product images from online APIs based on product categories'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear-images',
            action='store_true',
            help='Clear existing product images before adding new ones',
        )
        parser.add_argument(
            '--max-images',
            type=int,
            default=3,
            help='Maximum number of images per product (default: 3)',
        )

    def handle(self, *args, **options):
        if options['clear_images']:
            self.stdout.write('Clearing existing product images...')
            ProductImage.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Existing images cleared.'))

        max_images = options['max_images']
        
        # Category to search term mapping for better image results
        category_search_terms = {
            'T-Shirts': ['t-shirt', 'tshirt', 'polo', 'casual shirt'],
            'Shirts': ['dress shirt', 'formal shirt', 'button shirt', 'business shirt'],
            'Jeans': ['jeans', 'denim', 'denim pants', 'blue jeans'],
            'Dresses': ['dress', 'women dress', 'summer dress', 'fashion dress'],
            'Jackets': ['jacket', 'coat', 'blazer', 'outerwear'],
            'Sneakers': ['sneakers', 'shoes', 'running shoes', 'athletic shoes'],
            'Boots': ['boots', 'ankle boots', 'leather boots', 'fashion boots'],
            'Sandals': ['sandals', 'summer shoes', 'flip flops', 'casual sandals'],
            'Pants': ['pants', 'trousers', 'chinos', 'dress pants'],
            'Shorts': ['shorts', 'summer shorts', 'casual shorts', 'bermuda shorts'],
            'Skirts': ['skirt', 'mini skirt', 'midi skirt', 'maxi skirt'],
            'Sweaters': ['sweater', 'pullover', 'cardigan', 'knitwear'],
            'Hoodies': ['hoodie', 'sweatshirt', 'pullover hoodie', 'casual wear'],
        }

        products = Product.objects.all()
        total_products = products.count()
        
        self.stdout.write(f'Adding images to {total_products} products...')

        for index, product in enumerate(products, 1):
            self.stdout.write(f'Processing product {index}/{total_products}: {product.name}')
            
            # Get search terms for this product's category
            search_terms = category_search_terms.get(
                product.category.name, 
                [product.category.name.lower(), 'clothing']
            )
            
            # Add images for this product
            images_added = 0
            for i, search_term in enumerate(search_terms):
                if images_added >= max_images:
                    break
                
                # Try multiple image sources
                image_sources = [
                    self.get_fashion_focused_image,
                    self.get_picsum_image,
                    self.get_lorem_picsum_image,
                    self.get_placeholder_image,
                    self.get_fashion_focused_image
                ]
                
                for source_func in image_sources:
                    try:
                        image_data = source_func(search_term, product.id, i)
                        if image_data:
                            # Create filename
                            filename = f"{product.slug}-{i+1}.jpg"
                            
                            # Create ProductImage object
                            product_image = ProductImage.objects.create(
                                product=product,
                                alt_text=f"{product.name} - Image {i+1}",
                                is_primary=(images_added == 0),  # First image is primary
                                sort_order=i
                            )
                            
                            # Save the image file
                            product_image.image.save(
                                filename,
                                ContentFile(image_data),
                                save=True
                            )
                            
                            images_added += 1
                            self.stdout.write(f'  ✅ Added image {i+1} from {source_func.__name__}')
                            break  # Success, move to next image
                            
                    except Exception as e:
                        self.stdout.write(f'  ❌ Failed with {source_func.__name__}: {str(e)}')
                        continue
                
                # Small delay to be respectful to APIs
                time.sleep(0.3)
            
            self.stdout.write(f'  📸 Added {images_added} images for {product.name}')

        # Show summary
        total_images = ProductImage.objects.count()
        products_with_images = Product.objects.filter(images__isnull=False).distinct().count()

        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ Image addition completed!\n'
                f'📊 Statistics:\n'
                f'   • Total products: {total_products}\n'
                f'   • Products with images: {products_with_images}\n'
                f'   • Total images added: {total_images}\n'
                f'   • Average images per product: {total_images/total_products:.1f}\n'
            )
        )

    def get_picsum_image(self, search_term, product_id, image_index):
        """Get image from Lorem Picsum (reliable placeholder service)"""
        try:
            # Use product ID and image index for consistent but different images
            image_id = (product_id * 100 + image_index) % 1000
            url = f"https://picsum.photos/800/1000?random={image_id}"
            
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.content
        except Exception:
            return None

    def get_lorem_picsum_image(self, search_term, product_id, image_index):
        """Get image from Lorem Picsum with different parameters"""
        try:
            # Different approach for variety
            seed = product_id + image_index * 50
            url = f"https://picsum.photos/seed/{seed}/800/1000"
            
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.content
        except Exception:
            return None

    def get_placeholder_image(self, search_term, product_id, image_index):
        """Generate a simple colored placeholder image"""
        try:
            # Use different colors based on category
            colors = {
                't-shirt': '4CAF50',      # Green
                'dress shirt': '2196F3',   # Blue
                'jeans': '3F51B5',        # Indigo
                'dress': 'E91E63',        # Pink
                'jacket': '795548',       # Brown
                'sneakers': 'FF9800',     # Orange
            }
            
            # Find matching color or use default
            color = '9E9E9E'  # Default gray
            for term, hex_color in colors.items():
                if term in search_term.lower():
                    color = hex_color
                    break
            
            # Create a simple placeholder from placeholder.com
            url = f"https://via.placeholder.com/800x1000/{color}/FFFFFF?text={search_term.replace(' ', '+')}"
            
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.content
        except Exception:
            return None

    def get_fashion_focused_image(self, search_term, product_id, image_index):
        """Get fashion-focused images using multiple sources"""
        try:
            # Use different image dimensions for fashion items
            width, height = 600, 800  # Fashion-friendly aspect ratio
            
            # Create a seed based on product info for consistency
            seed = hash(f"{search_term}_{product_id}_{image_index}") % 10000
            
            # Try different fashion-focused image sources
            sources = [
                f"https://picsum.photos/seed/fashion{seed}/600/800",
                f"https://picsum.photos/seed/clothing{seed}/600/800", 
                f"https://picsum.photos/seed/style{seed}/600/800",
                f"https://source.unsplash.com/600x800/?{search_term.replace(' ', ',')},fashion",
                f"https://loremflickr.com/600/800/{search_term.replace(' ', ',')},fashion"
            ]
            
            for url in sources:
                try:
                    response = requests.get(url, timeout=10, allow_redirects=True)
                    if response.status_code == 200 and len(response.content) > 1000:
                        return response.content
                except:
                    continue
            
            return None
        except Exception:
            return None
