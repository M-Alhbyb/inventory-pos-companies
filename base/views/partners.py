"""Partner (merchant/representative) management views."""

from decimal import Decimal

from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.db import transaction as db_transaction
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required

from base.models import User, Product, Transaction, TransactionItem
from base.forms import UserForm

ITEMS_PER_PAGE = 10

# Partner type display names
PARTNER_TYPE_DISPLAY = {
    'merchant': 'تاجر',
    'representative': 'مندوب',
}


def get_partner_type_display(partner_type):
    """Get the Arabic display name for a partner type."""
    return PARTNER_TYPE_DISPLAY.get(partner_type, '')

@login_required
def partners_view(request, partner_type):
    """Display all partners of a given type with search and pagination."""
    partners = User.objects.filter(user_type=partner_type)
    
    # Handle search
    q = request.GET.get('q')
    if q:
        partners = partners.filter(
            Q(username__icontains=q) |
            Q(first_name__icontains=q) |
            Q(last_name__icontains=q) |
            Q(phone__icontains=q)
        )
    
    # Pagination
    paginator = Paginator(partners, ITEMS_PER_PAGE)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # Handle AJAX requests for infinite scroll
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return get_partners_json(page_obj, partner_type)
    
    return render(request, 'partners/partners.html', {
        'page_obj': page_obj,
        'user_form': UserForm(),
        'edit_user_form': UserForm(prefix='edit'),
        'partner_type': partner_type,
        'partner_type_display': get_partner_type_display(partner_type),
    })


def get_partners_json(page_obj, partner_type):
    """Return paginated partners as JSON for infinite scroll."""
    data = []
    for partner in page_obj:
        data.append({
            'id': partner.id,
            'username': partner.username,
            'full_name': partner.get_full_name() or partner.username,
            'first_name': partner.first_name or '',
            'last_name': partner.last_name or '',
            'phone': partner.phone or '',
            'address': partner.address or '',
            'debt': str(partner.debt) if partner.debt else '0',
            'products_count': partner.products_count or 0,
            'user_type': partner.user_type,
        })
    
    return JsonResponse({
        'success': True,
        'data': data,
        'partner_type': partner_type,
        'has_next': page_obj.has_next(),
        'next_page_number': page_obj.next_page_number() if page_obj.has_next() else None,
    })

@login_required
@require_http_methods(["POST"])
def add_partner(request, partner_type):
    """Handle adding a new partner."""
    try:
        user_form = UserForm(request.POST)
        
        if user_form.is_valid():
            with db_transaction.atomic():
                user = user_form.save(commit=False)
                user.user_type = partner_type
                user.set_password('password123')  # Default password
                user.save()
                
            messages.success(request, f'تم إضافة {get_partner_type_display(partner_type)} بنجاح')
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'error': str(user_form.errors)})
            
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
@require_http_methods(["POST", "GET"])
def edit_partner(request, partner_id):
    """Handle editing an existing partner."""
    try:
        partner = get_object_or_404(User, id=partner_id)
        
        if request.method == "GET":
            user_form = UserForm(instance=partner)
            final_form = {}
            for field in user_form:
                val = field.value()
                final_form[field.name] = str(val) if val is not None else ""
            return JsonResponse({'success': True, 'fields': final_form})
        
        user_form = UserForm(request.POST, instance=partner, prefix='edit')
        
        if user_form.is_valid():
            user_form.save()
            messages.success(request, f'تم تحديث بيانات {get_partner_type_display(partner.user_type)} بنجاح')
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'error': str(user_form.errors)})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
@require_http_methods(["POST"])
def delete_partner(request, partner_id):
    """Handle deleting a partner."""
    try:
        partner = get_object_or_404(User, id=partner_id)
        partner_type_display = get_partner_type_display(partner.user_type)
        partner.delete()
        
        messages.success(request, f'تم حذف {partner_type_display} بنجاح')
        return JsonResponse({'success': True})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
def partner_detail(request, partner_id):
    """Display partner details and handle transactions."""
    partner = get_object_or_404(User, id=partner_id)
    products = Product.objects.all()
    transactions = Transaction.objects.filter(user=partner).prefetch_related('items__product')
    partner_products = TransactionItem.objects.filter(transaction__user=partner)
    
    # Prepare products list for dropdowns
    products_list = list(products.values('id', 'name', 'stock'))
    products_list.insert(0, {'id': 'skip', 'name': 'اختر منتج', 'stock': ''})

    if request.method == 'POST':
        return _handle_partner_transaction(request, partner, partner_id)

    return render(request, 'partners/partner-detail.html', {
        'partner': partner,
        'partner_transactions': transactions.order_by('-date'),
        'partner_products': partner_products,
        'products': products,
        'products_list': products_list,
        'partner_type': partner.user_type,
        'partner_type_display': get_partner_type_display(partner.user_type),
    })


def _handle_partner_transaction(request, partner, partner_id):
    """Process partner transaction from POST request."""
    transaction_type = request.POST.get('transaction_type')
    
    # Handle Payment (Merchant only)
    if transaction_type == 'payment' and partner.user_type == 'merchant':
        amount = request.POST.get('amount')
        if amount and amount != "":
            Transaction.objects.create(user=partner, type='payment', amount=Decimal(amount))
            messages.success(request, 'تم سداد المبلغ بنجاح')
        else:
            messages.error(request, 'يجب إدخال المبلغ')
        return redirect('base:representative_detail', partner_id)

    # Handle Product Transactions (Take/Restore)
    if transaction_type in ['take', 'restore']:
        product_ids = request.POST.getlist('product')
        quantities = request.POST.getlist('quantity')
        
        # Validate at least one product selected
        if len(product_ids) == 1 and product_ids[0] == "skip":
            messages.error(request, 'يجب اختيار منتج')
            return redirect('base:representative_detail', partner_id)
        
        transaction = Transaction.objects.create(user=partner, type=transaction_type)
        
        for i, product_id in enumerate(product_ids):
            if product_id == "skip" or not quantities[i]:
                continue
                
            product = Product.objects.get(id=product_id)
            quantity = Decimal(quantities[i])
            
            # Check stock for 'take'
            if transaction_type == 'take' and product.stock < quantity:
                messages.error(request, f'الكمية المطلوبة من {product.name} غير متوفرة')
                transaction.delete()
                return redirect('base:representative_detail', partner_id)
            
            TransactionItem.objects.create(
                transaction=transaction,
                product=product,
                quantity=quantity,
            )
        
        messages.success(request, 'تم إضافة المعاملة بنجاح')
        return redirect('base:representative_detail', partner_id)
    
    return redirect('base:representative_detail', partner_id)

@login_required
@require_http_methods(["POST"])
def delete_transaction(request, partner_id, transaction_id):
    """Delete a transaction and reverse all stock/debt changes."""
    try:
        transaction = get_object_or_404(Transaction, id=transaction_id, user_id=partner_id)
        transaction.delete()  # Model's delete method handles stock/debt reversal
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
