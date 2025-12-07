"""Custom context processors for template rendering."""

from base.models import Product, Category, User


def sidebar_stats(request):
    """
    Context processor to provide sidebar statistics across all templates.
    
    Provides counts for products, categories, merchants, and representatives.
    """
    return {
        'products_count': Product.objects.count(),
        'categories_count': Category.objects.count(),
        'merchants_count': User.objects.filter(user_type='merchant').count(),
        'representatives_count': User.objects.filter(user_type='representative').count(),
    }
