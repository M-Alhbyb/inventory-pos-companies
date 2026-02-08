"""Views for POS app."""

import json
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Sum, Q
from django.views.decorators.http import require_POST
from django.utils import timezone
from functools import wraps

from accounts.views import company_required
from inventory.models import Product
from .models import Sale, SaleItem
from .forms import CheckoutForm


# =============================================================================
# DECORATORS
# =============================================================================

def cashier_required(view_func):
    """Restrict access to cashiers only."""
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if not request.user.is_cashier:
            messages.error(request, 'هذه الصفحة مخصصة للكاشير فقط.')
            return redirect('accounts:login')
        return view_func(request, *args, **kwargs)
    return wrapper


def pos_feature_required(view_func):
    """Check if company has POS feature enabled."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.company:
            subscription = getattr(request.user.company, 'subscription', None)
            if subscription and not subscription.plan.has_pos:
                messages.error(request, 'خطة شركتك لا تتضمن ميزة نقطة البيع.')
                return redirect('accounts:company_dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


# =============================================================================
# POS INTERFACE
# =============================================================================

@cashier_required
@company_required
@pos_feature_required
def pos_interface(request):
    """Main POS interface."""
    company = request.user.company
    
    # Get all active products with stock
    products = Product.objects.filter(
        company=company, is_active=True
    ).select_related('category').order_by('category__name', 'name')
    
    # Get categories for filtering
    categories = products.values_list('category__id', 'category__name').distinct()
    
    # Convert products to JSON for JavaScript
    products_data = []
    for product in products:
        products_data.append({
            'id': product.id,
            'name': product.name,
            'price': str(product.price),
            'stock': product.stock,
            'category_id': product.category_id if product.category else None,
            'category_name': product.category.name if product.category else 'بدون فئة',
            'barcode': product.barcode or '',
            'image': product.image.url if product.image else ''
        })
    
    context = {
        'products': products,
        'products_json': json.dumps(products_data),
        'categories': list(categories),
        'company': company,
        'checkout_form': CheckoutForm()
    }
    
    return render(request, 'pos/interface.html', context)


@cashier_required
@company_required
@require_POST
def process_checkout(request):
    """Process the checkout and create a sale."""
    company = request.user.company
    
    try:
        # Parse cart data
        cart_data = json.loads(request.POST.get('cart', '[]'))
        if not cart_data:
            return JsonResponse({'success': False, 'error': 'السلة فارغة'})
        
        # Get form data
        customer_name = request.POST.get('customer_name', '')
        customer_phone = request.POST.get('customer_phone', '')
        discount_percentage = Decimal(request.POST.get('discount_percentage', '0') or '0')
        payment_method = request.POST.get('payment_method', Sale.PaymentMethod.CASH)
        amount_paid = Decimal(request.POST.get('amount_paid', '0'))
        notes = request.POST.get('notes', '')
        
        # Create sale
        sale = Sale.objects.create(
            company=company,
            cashier=request.user,
            customer_name=customer_name,
            customer_phone=customer_phone,
            discount_percentage=discount_percentage,
            payment_method=payment_method,
            amount_paid=amount_paid,
            notes=notes
        )
        
        # Add items
        for item in cart_data:
            product = get_object_or_404(Product, id=item['id'], company=company)
            
            # Check stock
            if product.stock < item['quantity']:
                sale.delete()
                return JsonResponse({
                    'success': False, 
                    'error': f'الكمية المطلوبة من {product.name} غير متوفرة'
                })
            
            SaleItem.objects.create(
                sale=sale,
                product=product,
                quantity=item['quantity'],
                price=product.price,
                cost=product.cost
            )
        
        # Calculate totals
        sale.calculate_totals()
        
        # Apply stock changes
        sale.apply_stock_changes()
        
        return JsonResponse({
            'success': True,
            'sale_id': sale.id,
            'receipt_number': sale.receipt_number,
            'total': str(sale.total),
            'change': str(sale.change)
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@cashier_required
@company_required
def print_receipt(request, sale_id):
    """Display printable receipt."""
    sale = get_object_or_404(
        Sale, id=sale_id, company=request.user.company
    )
    
    return render(request, 'pos/receipt.html', {
        'sale': sale,
        'company': request.user.company
    })


# =============================================================================
# SALES HISTORY
# =============================================================================

@cashier_required
@company_required
def sales_history(request):
    """View cashier's sales history."""
    sales = Sale.objects.filter(
        cashier=request.user
    ).order_by('-created_at')
    
    # Filter by date
    date_filter = request.GET.get('date')
    if date_filter:
        sales = sales.filter(created_at__date=date_filter)
    
    # Today's summary
    today = timezone.now().date()
    today_sales = Sale.objects.filter(
        cashier=request.user,
        created_at__date=today,
        status=Sale.Status.COMPLETED
    )
    
    context = {
        'sales': sales[:50],  # Limit to 50 most recent
        'today_count': today_sales.count(),
        'today_total': today_sales.aggregate(total=Sum('total'))['total'] or 0
    }
    
    return render(request, 'pos/sales_history.html', context)


@cashier_required
@company_required
def daily_summary(request):
    """Daily sales summary for cashier."""
    today = timezone.now().date()
    
    sales = Sale.objects.filter(
        cashier=request.user,
        created_at__date=today,
        status=Sale.Status.COMPLETED
    )
    
    # Group by payment method
    cash_sales = sales.filter(payment_method=Sale.PaymentMethod.CASH)
    card_sales = sales.filter(payment_method=Sale.PaymentMethod.CARD)
    transfer_sales = sales.filter(payment_method=Sale.PaymentMethod.TRANSFER)
    
    context = {
        'date': today,
        'total_sales': sales.count(),
        'total_amount': sales.aggregate(total=Sum('total'))['total'] or 0,
        'cash_amount': cash_sales.aggregate(total=Sum('total'))['total'] or 0,
        'card_amount': card_sales.aggregate(total=Sum('total'))['total'] or 0,
        'transfer_amount': transfer_sales.aggregate(total=Sum('total'))['total'] or 0,
        'sales': sales
    }
    
    return render(request, 'pos/daily_summary.html', context)


# =============================================================================
# API ENDPOINTS
# =============================================================================

@cashier_required
@company_required
def search_products(request):
    """Search products by name, SKU, or barcode."""
    query = request.GET.get('q', '')
    company = request.user.company
    
    products = Product.objects.filter(
        company=company,
        is_active=True
    ).filter(
        Q(name__icontains=query) |
        Q(sku__icontains=query) |
        Q(barcode__icontains=query)
    )[:20]
    
    data = [{
        'id': p.id,
        'name': p.name,
        'price': str(p.price),
        'stock': p.stock,
        'barcode': p.barcode or ''
    } for p in products]
    
    return JsonResponse({'products': data})


@cashier_required
@company_required
def get_product_by_barcode(request):
    """Get single product by barcode."""
    barcode = request.GET.get('barcode', '')
    company = request.user.company
    
    try:
        product = Product.objects.get(
            company=company,
            barcode=barcode,
            is_active=True
        )
        return JsonResponse({
            'found': True,
            'product': {
                'id': product.id,
                'name': product.name,
                'price': str(product.price),
                'stock': product.stock
            }
        })
    except Product.DoesNotExist:
        return JsonResponse({'found': False})
