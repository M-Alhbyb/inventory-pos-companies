"""Dashboard view for the inventory system."""

import json

from django.shortcuts import render
from django.core.paginator import Paginator

from base.models import Category, Product, User, Transaction
from base.forms import CategoryForm, ProductForm, FeesForm


def dashboard(request):
    """Display the main dashboard with statistics and recent data."""
    # Get counts for stats
    context = {
        'total_products': Product.objects.count(),
        'total_categories': Category.objects.count(),
        'total_merchants': User.objects.filter(user_type='merchant').count(),
        'total_representatives': User.objects.filter(user_type='representative').count(),
    }
    
    # Get recent items
    context['recent_products'] = Product.objects.select_related('category').order_by('-created_at')[:5]
    context['recent_categories'] = Category.objects.order_by('-created_at')[:5]
    context['merchants'] = User.objects.filter(user_type='merchant')
    context['representatives'] = User.objects.filter(user_type='representative')
    
    # Get recent transactions with pagination
    recent_transactions = Transaction.objects.order_by('-date')
    paginator = Paginator(recent_transactions, 5)
    page_number = request.GET.get('page')
    context['page_obj'] = paginator.get_page(page_number)
    context['recent_transactions'] = recent_transactions
    
    # Get products for transaction modals
    products = Product.objects.all()
    products_list = list(products.values('id', 'name', 'stock'))
    products_list.insert(0, {'id': 'skip', 'name': 'اختر منتج', 'stock': ''})
    context['products_list'] = json.dumps(products_list)
    
    # Initialize forms
    context['category_form'] = CategoryForm()
    context['product_form'] = ProductForm()
    context['fees_form'] = FeesForm()
    
    return render(request, 'dashboard.html', context)
