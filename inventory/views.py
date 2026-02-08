"""Views for inventory app."""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Sum, Q, F
from django.core.paginator import Paginator
from functools import wraps
from decimal import Decimal

from accounts.models import User
from accounts.views import company_required
from .models import Category, Product, Transaction, TransactionItem
from .forms import CategoryForm, ProductForm, TransactionForm


# =============================================================================
# DECORATORS
# =============================================================================

def accountant_required(view_func):
    """Restrict access to accountants only."""
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if not request.user.is_accountant:
            messages.error(request, 'هذه الصفحة مخصصة للمحاسبين فقط.')
            return redirect('accounts:login')
        return view_func(request, *args, **kwargs)
    return wrapper


def representative_required(view_func):
    """Restrict access to representatives only."""
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if not request.user.is_representative:
            messages.error(request, 'هذه الصفحة مخصصة للمندوبين فقط.')
            return redirect('accounts:login')
        return view_func(request, *args, **kwargs)
    return wrapper


def inventory_feature_required(view_func):
    """Check if company has inventory feature enabled."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.company:
            subscription = getattr(request.user.company, 'subscription', None)
            if subscription and not subscription.plan.has_inventory:
                messages.error(request, 'خطة شركتك لا تتضمن ميزة المخزون.')
                return redirect('accounts:company_dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


# =============================================================================
# ACCOUNTANT DASHBOARD
# =============================================================================

@accountant_required
@company_required
@inventory_feature_required
def dashboard(request):
    """Accountant inventory dashboard."""
    company = request.user.company
    
    # Stats
    context = {
        'total_products': Product.objects.filter(company=company).count(),
        'total_categories': Category.objects.filter(company=company).count(),
        'total_representatives': User.objects.filter(
            company=company, role=User.Role.REPRESENTATIVE
        ).count(),
        'low_stock_products': Product.objects.filter(
            company=company, stock__lte=F('low_stock_threshold')
        ).count(),
    }
    
    # Recent transactions
    recent_transactions = Transaction.objects.filter(
        company=company
    ).select_related('user').order_by('-date')[:10]
    context['recent_transactions'] = recent_transactions
    
    # Pending transactions count
    context['pending_count'] = Transaction.objects.filter(
        company=company, status=Transaction.Status.PENDING
    ).count()
    
    return render(request, 'inventory/dashboard.html', context)


# =============================================================================
# CATEGORIES
# =============================================================================

@accountant_required
@company_required
@inventory_feature_required
def categories_view(request):
    """List and manage categories."""
    company = request.user.company
    categories = Category.objects.filter(company=company).order_by('name')
    
    return render(request, 'inventory/categories.html', {
        'categories': categories,
        'form': CategoryForm()
    })


@accountant_required
@company_required
def add_category(request):
    """Add a new category."""
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.company = request.user.company
            category.save()
            messages.success(request, 'تم إضافة الفئة بنجاح!')
        else:
            messages.error(request, 'حدث خطأ في البيانات.')
    return redirect('inventory:categories')


@accountant_required
@company_required
def edit_category(request, category_id):
    """Edit a category."""
    category = get_object_or_404(
        Category, id=category_id, company=request.user.company
    )
    
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تحديث الفئة بنجاح!')
    
    return redirect('inventory:categories')


@accountant_required
@company_required
def delete_category(request, category_id):
    """Delete a category."""
    if request.method == 'POST':
        category = get_object_or_404(
            Category, id=category_id, company=request.user.company
        )
        category.delete()
        messages.success(request, 'تم حذف الفئة بنجاح!')
    return redirect('inventory:categories')


# =============================================================================
# PRODUCTS
# =============================================================================

@accountant_required
@company_required
@inventory_feature_required
def products_view(request):
    """List and manage products."""
    company = request.user.company
    products = Product.objects.filter(company=company).select_related('category')
    
    # Search
    search = request.GET.get('search', '')
    if search:
        products = products.filter(
            Q(name__icontains=search) | 
            Q(sku__icontains=search) |
            Q(barcode__icontains=search)
        )
    
    # Filter by category
    category_id = request.GET.get('category')
    if category_id:
        products = products.filter(category_id=category_id)
    
    # Pagination
    paginator = Paginator(products.order_by('name'), 20)
    page = request.GET.get('page')
    products = paginator.get_page(page)
    
    categories = Category.objects.filter(company=company)
    form = ProductForm(company=company)
    
    return render(request, 'inventory/products.html', {
        'products': products,
        'categories': categories,
        'form': form,
        'search': search
    })


@accountant_required
@company_required
def add_product(request):
    """Add a new product."""
    company = request.user.company
    
    # Check product limit
    subscription = company.subscription
    if company.products.count() >= subscription.plan.max_products:
        messages.error(request, 'لقد وصلت إلى الحد الأقصى للمنتجات في خطتك.')
        return redirect('inventory:products')
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, company=company)
        if form.is_valid():
            product = form.save(commit=False)
            product.company = company
            product.save()
            messages.success(request, 'تم إضافة المنتج بنجاح!')
        else:
            messages.error(request, 'حدث خطأ في البيانات.')
    return redirect('inventory:products')


@accountant_required
@company_required
def edit_product(request, product_id):
    """Edit a product."""
    company = request.user.company
    product = get_object_or_404(Product, id=product_id, company=company)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product, company=company)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تحديث المنتج بنجاح!')
    
    return redirect('inventory:products')


@accountant_required
@company_required
def delete_product(request, product_id):
    """Delete a product."""
    if request.method == 'POST':
        product = get_object_or_404(
            Product, id=product_id, company=request.user.company
        )
        product.delete()
        messages.success(request, 'تم حذف المنتج بنجاح!')
    return redirect('inventory:products')


# =============================================================================
# TRANSACTIONS
# =============================================================================

@accountant_required
@company_required
@inventory_feature_required
def transactions_view(request):
    """List and manage transactions."""
    company = request.user.company
    transactions = Transaction.objects.filter(
        company=company
    ).select_related('user', 'approved_by').prefetch_related('items__product')
    
    # Filter by status
    status = request.GET.get('status', '')
    if status:
        transactions = transactions.filter(status=status)
    
    # Filter by type
    trans_type = request.GET.get('type', '')
    if trans_type:
        transactions = transactions.filter(type=trans_type)
    
    # Pagination
    paginator = Paginator(transactions.order_by('-date'), 20)
    page = request.GET.get('page')
    transactions = paginator.get_page(page)
    
    return render(request, 'inventory/transactions.html', {
        'transactions': transactions,
        'current_status': status,
        'current_type': trans_type
    })


@accountant_required
@company_required
def approve_transaction(request, transaction_id):
    """Approve a pending transaction."""
    if request.method == 'POST':
        transaction = get_object_or_404(
            Transaction, id=transaction_id, company=request.user.company
        )
        if transaction.approve(request.user):
            messages.success(request, 'تمت الموافقة على المعاملة بنجاح!')
        else:
            messages.error(request, 'لا يمكن الموافقة على هذه المعاملة.')
    return redirect('inventory:transactions')


@accountant_required
@company_required
def reject_transaction(request, transaction_id):
    """Reject a pending transaction."""
    if request.method == 'POST':
        transaction = get_object_or_404(
            Transaction, id=transaction_id, company=request.user.company
        )
        if transaction.reject(request.user):
            messages.success(request, 'تم رفض المعاملة.')
        else:
            messages.error(request, 'لا يمكن رفض هذه المعاملة.')
    return redirect('inventory:transactions')


# =============================================================================
# REPRESENTATIVES
# =============================================================================

@accountant_required
@company_required
@inventory_feature_required
def representatives_view(request):
    """List representatives and their product counts."""
    company = request.user.company
    representatives = User.objects.filter(
        company=company, role=User.Role.REPRESENTATIVE
    )
    
    return render(request, 'inventory/representatives.html', {
        'representatives': representatives
    })


@accountant_required
@company_required
def representative_detail(request, rep_id):
    """View representative details and transactions."""
    company = request.user.company
    rep = get_object_or_404(
        User, id=rep_id, company=company, role=User.Role.REPRESENTATIVE
    )
    
    transactions = Transaction.objects.filter(
        user=rep
    ).prefetch_related('items__product').order_by('-date')
    
    return render(request, 'inventory/representative_detail.html', {
        'representative': rep,
        'transactions': transactions
    })


# =============================================================================
# REPRESENTATIVE PORTAL
# =============================================================================

@representative_required
@company_required
@inventory_feature_required
def rep_dashboard(request):
    """Representative dashboard."""
    user = request.user
    
    # Transaction stats
    context = {
        'products_count': user.products_count,
        'pending_count': Transaction.objects.filter(
            user=user, status=Transaction.Status.PENDING
        ).count(),
        'take_total': Transaction.objects.filter(
            user=user, type=Transaction.Type.TAKE, status=Transaction.Status.APPROVED
        ).aggregate(total=Sum('amount'))['total'] or 0,
        'payment_total': Transaction.objects.filter(
            user=user, type=Transaction.Type.PAYMENT, status=Transaction.Status.APPROVED
        ).aggregate(total=Sum('amount'))['total'] or 0,
    }
    
    # Recent transactions
    context['recent_transactions'] = Transaction.objects.filter(
        user=user
    ).order_by('-date')[:5]
    
    return render(request, 'inventory/rep/dashboard.html', context)


@representative_required
@company_required
def rep_transactions(request):
    """Representative's transaction history."""
    transactions = Transaction.objects.filter(
        user=request.user
    ).prefetch_related('items__product').order_by('-date')
    
    # Filter by type
    trans_type = request.GET.get('type', '')
    if trans_type:
        transactions = transactions.filter(type=trans_type)
    
    return render(request, 'inventory/rep/transactions.html', {
        'transactions': transactions,
        'current_type': trans_type
    })


@representative_required
@company_required
def rep_request(request):
    """Representative request a new transaction."""
    company = request.user.company
    products = Product.objects.filter(company=company, is_active=True)
    
    if request.method == 'POST':
        trans_type = request.POST.get('transaction_type')
        
        if trans_type == 'payment':
            amount = request.POST.get('amount')
            if amount:
                Transaction.objects.create(
                    company=company,
                    user=request.user,
                    type=Transaction.Type.PAYMENT,
                    amount=Decimal(amount)
                )
                messages.success(request, 'تم إرسال طلب الدفع بنجاح!')
        
        elif trans_type in ['take', 'restore']:
            product_ids = request.POST.getlist('product')
            quantities = request.POST.getlist('quantity')
            
            if product_ids and quantities:
                transaction = Transaction.objects.create(
                    company=company,
                    user=request.user,
                    type=trans_type
                )
                
                for prod_id, qty in zip(product_ids, quantities):
                    if prod_id and qty and int(qty) > 0:
                        product = get_object_or_404(Product, id=prod_id, company=company)
                        TransactionItem.objects.create(
                            transaction=transaction,
                            product=product,
                            quantity=int(qty),
                            price=product.price
                        )
                
                messages.success(request, 'تم إرسال الطلب بنجاح!')
        
        return redirect('inventory:rep_dashboard')
    
    return render(request, 'inventory/rep/request.html', {
        'products': products
    })
