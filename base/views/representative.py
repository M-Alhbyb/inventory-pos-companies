"""Representative-facing views for dashboard, transactions, and requests."""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from functools import wraps

from base.models import User, Transaction, TransactionItem, Product


def representative_required(view_func):
    """Decorator to restrict access to representatives only."""
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.user_type != 'representative':
            messages.error(request, 'هذه الصفحة مخصصة للمندوبين فقط.')
            return redirect('base:dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


@representative_required
def rep_dashboard(request):
    """Representative dashboard with summary and quick actions."""
    user = request.user
    
    # Get recent transactions (last 5)
    recent_transactions = Transaction.objects.filter(
        user=user
    ).order_by('-date')[:5]
    
    # Get transaction counts by type
    take_count = Transaction.objects.filter(user=user, type='take').count()
    restore_count = Transaction.objects.filter(user=user, type='restore').count()
    payment_count = Transaction.objects.filter(user=user, type='payment').count()
    
    # Calculate total amounts
    total_taken = Transaction.objects.filter(
        user=user, type='take'
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    total_payments = Transaction.objects.filter(
        user=user, type='payment'
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    context = {
        'recent_transactions': recent_transactions,
        'products_count': user.products_count,
        'take_count': take_count,
        'restore_count': restore_count,
        'payment_count': payment_count,
        'total_taken': total_taken,
        'total_payments': total_payments,
    }
    
    return render(request, 'rep/rep_dashboard.html', context)


@representative_required
def rep_transactions(request):
    """List all transactions for the logged-in representative."""
    user = request.user
    
    # Get all transactions
    transactions = Transaction.objects.filter(
        user=user
    ).prefetch_related('items__product').order_by('-date')
    
    # Filter by type if specified
    transaction_type = request.GET.get('type')
    if transaction_type and transaction_type != 'all':
        transactions = transactions.filter(type=transaction_type)
    
    context = {
        'transactions': transactions,
        'current_type': transaction_type or 'all',
    }
    
    return render(request, 'rep/rep_transactions.html', context)


@representative_required
def rep_request_transaction(request):
    """Handle transaction request form."""
    if request.method == 'POST':
        transaction_type = request.POST.get('transaction_type')
        
        if transaction_type == 'payment':
            # Payment request
            amount = request.POST.get('amount')
            if amount:
                Transaction.objects.create(
                    user=request.user,
                    type='payment',
                    amount=amount
                )
                messages.success(request, 'تم طلب الدفع بنجاح!')
            else:
                messages.error(request, 'يرجى إدخال المبلغ.')
        
        elif transaction_type in ['take', 'restore']:
            # Product transaction
            products = request.POST.getlist('product')
            quantities = request.POST.getlist('quantity')
            
            if products and quantities:
                # Create transaction
                transaction = Transaction.objects.create(
                    user=request.user,
                    type=transaction_type
                )
                
                # Add items
                for product_id, quantity in zip(products, quantities):
                    if product_id and product_id != 'skip' and quantity:
                        product = get_object_or_404(Product, id=product_id)
                        TransactionItem.objects.create(
                            transaction=transaction,
                            product=product,
                            quantity=int(quantity)
                        )
                
                type_display = 'أخذ' if transaction_type == 'take' else 'إرجاع'
                messages.success(request, f'تم طلب {type_display} المنتجات بنجاح!')
            else:
                messages.error(request, 'يرجى اختيار منتج وإدخال الكمية.')
        
        return redirect('base:rep_dashboard')
    
    # GET request - show form
    products = Product.objects.all().order_by('name')
    products_list = list(products.values('id', 'name', 'stock'))
    
    context = {
        'products': products,
        'products_list': products_list,
    }
    
    return render(request, 'rep/rep_request.html', context)
