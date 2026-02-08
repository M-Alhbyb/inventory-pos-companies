"""Dashboard view for the inventory system."""

import json

from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout

from base.models import Category, Product, User, Transaction
from base.forms import CategoryForm, ProductForm

@login_required
def dashboard(request):
    """Display the main dashboard with statistics and recent data."""
    # Get counts for stats
    context = {
        'total_products': Product.objects.count(),
        'total_categories': Category.objects.count(),
        'total_representatives': User.objects.filter(user_type='representative').count(),
    }
    
    # Get recent items
    context['recent_products'] = Product.objects.select_related('category').order_by('-created_at')[:5]
    context['recent_categories'] = Category.objects.order_by('-created_at')[:5]
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
    
    return render(request, 'dashboard.html', context)


def custom_logout(request):
    """Handle logout with visual confirmation for GET requests."""
    if request.method == 'POST':
        logout(request)
        return redirect('login')
    return render(request, 'registration/logout.html')


def custom_login(request):
    """Handle login with user_type based redirect."""
    from django.contrib.auth import authenticate, login
    from django.contrib.auth.forms import AuthenticationForm
    
    if request.user.is_authenticated:
        # Already logged in, redirect based on user_type
        if request.user.user_type == 'representative':
            return redirect('base:rep_dashboard')
        return redirect('base:dashboard')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            # Redirect based on user_type
            if user.user_type == 'representative':
                return redirect('base:rep_dashboard')
            return redirect('base:dashboard')
    else:
        form = AuthenticationForm()
    
    return render(request, 'registration/login.html', {'form': form})
