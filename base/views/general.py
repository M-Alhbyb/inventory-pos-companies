
from django.shortcuts import render, redirect
from base.models import Category, Product, User,  Transaction, TransactionItem
from base.forms import CategoryForm, ProductForm
import json

def dashboard(request):
    # Get counts for stats
    total_products = Product.objects.count()
    total_categories = Category.objects.count()
    total_merchants = User.objects.filter(user_type='merchant').count()
    total_representatives = User.objects.filter(user_type='representative').count()
    
    # Get recent items
    recent_products = Product.objects.select_related('category').order_by('-id')[:5]
    recent_categories = Category.objects.order_by('-id')[:5]
    merchants = User.objects.filter(user_type='merchant').all()
    representatives = User.objects.filter(user_type='representative').all()
    
    # Get recent transactions
    recent_transactions = Transaction.objects.order_by('-id')[:5]
    
    # Get products for transaction modals
    products = Product.objects.all()
    products_list = list(products.values('id', 'name', 'stock'))
    products_list.insert(0, {'id': "skip", 'name': 'اختر منتج', 'stock': ''})
    
    # Initialize forms
    category_form = CategoryForm()
    product_form = ProductForm()
    
    context = {
        'total_products': total_products,
        'total_categories': total_categories,
        'total_merchants': total_merchants,
        'total_representatives': total_representatives,
        'recent_transactions': recent_transactions,
        'merchants': merchants,
        'representatives': representatives,
        'category_form': category_form,
        'product_form': product_form,
        'products_list': json.dumps(products_list),
    }
    return render(request, 'dashboard.html', context)
