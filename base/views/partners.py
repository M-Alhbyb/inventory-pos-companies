from django.shortcuts import render, get_object_or_404, redirect
from base.models import User, USER_TYPES, Product, Transaction, TransactionItem
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.db import transaction as db_transaction
from decimal import Decimal

from base.forms import UserForm

def get_partner_type_display(partner_type):
    if partner_type == 'merchant':
        return 'تاجر'
    elif partner_type == 'representative':
        return 'مندوب'
    return ''

def partners_view(request, partner_type):
    partners = User.objects.filter(user_type=partner_type).all()
    
    # Handle search
    q = request.GET.get('q')
    if q:
        partners = partners.filter(
            Q(username__icontains=q) |
            Q(first_name__icontains=q) |
            Q(last_name__icontains=q) |
            Q(phone__icontains=q)
        )

    user_form = UserForm()
    edit_user_form = UserForm(prefix='edit')

    context = {
        'partners': partners,
        'user_form': user_form,
        'edit_user_form': edit_user_form,
        'partner_type': partner_type,
        'partner_type_display': get_partner_type_display(partner_type),
    }
    return render(request, 'partners/partners.html', context)

@require_http_methods(["POST"])
def add_partner(request, partner_type):
    try:
        user_form = UserForm(request.POST)
        
        if user_form.is_valid():
            with db_transaction.atomic():
                user = user_form.save(commit=False)
                user.user_type = partner_type
                user.set_password('password123') # Default password
                user.save()
                
            messages.success(request, f'تم إضافة {get_partner_type_display(partner_type)} بنجاح')
            return JsonResponse({'success': True})
        else:
            errors = {}
            errors.update(user_form.errors)
            return JsonResponse({'success': False, 'error': str(errors)})
            
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@require_http_methods(["POST", "GET"])
def edit_partner(request, partner_id):
    try:
        if request.method == "GET":
            partner = get_object_or_404(User, id=partner_id)
            
            user_form = UserForm(instance=partner)
            
            final_form = {}
            for field in user_form:
                val = field.value()
                final_form[field.name] = str(val) if val is not None else ""

            return JsonResponse({'success': True, 'fields': final_form})
        
        partner = get_object_or_404(User, id=partner_id)
        
        user_form = UserForm(request.POST, instance=partner, prefix='edit')
        
        if user_form.is_valid():
            user = user_form.save(commit=False)
            # Ensure user_type doesn't change implicitly, though form shouldn't have it
            user.save()
            
            messages.success(request, f'تم تحديث بيانات {get_partner_type_display(partner.user_type)} بنجاح')
            return JsonResponse({'success': True})
        else:
            errors = {}
            errors.update(user_form.errors)
            return JsonResponse({'success': False, 'error': str(errors)})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@require_http_methods(["POST"])
def delete_partner(request, partner_id):
    try:
        partner = get_object_or_404(User, id=partner_id)
        partner_type_display = get_partner_type_display(partner.user_type)
        partner.delete()
        
        messages.success(request, f'تم حذف {partner_type_display} بنجاح')
        return JsonResponse({'success': True})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

def partner_detail(request, partner_id):
    partner = get_object_or_404(User, id=partner_id)
    products = Product.objects.all()
    # Get all transactions for this partner
    transactions = Transaction.objects.filter(user=partner).prefetch_related('items__product')
    partner_products = TransactionItem.objects.filter(transaction__user=partner)
    products_list = list(products.values('id', 'name', 'stock'))
    products_list.insert(0, {'id': "skip", 'name': 'اختر منتج', 'stock': ''})

    if request.method == 'POST':
        transaction_type = request.POST.get('transaction_type')
        
        # Handle Payment (Merchant only)
        if transaction_type == 'payment' and partner.user_type == 'merchant':
            amount = request.POST.get('amount')
            if amount:
                if amount == "":
                    messages.error(request, 'يجب إدخال المبلغ')
                    return redirect('base:partner_detail', partner_id)
                else:
                    Transaction.objects.create(user=partner, type='payment', amount=Decimal(amount))
                    messages.success(request, 'تم سداد المبلغ بنجاح')
                    return redirect('base:partner_detail', partner_id)

        # Handle Product Transactions (Take/Restore)
        if transaction_type in ['take', 'restore']:
            name = request.POST.getlist('product') 
            quantity = request.POST.getlist('quantity')
            
            if len(name) == 1:
                if name[0] == "skip":
                    messages.error(request, 'يجب اختيار منتج')
                    return redirect('base:partner_detail', partner_id)
            
            # For merchants, 'take' is the only product transaction usually, but logic is same
            # If merchant tries 'restore', it might not be in UI, but backend can handle or restrict
            if partner.user_type == 'merchant' and transaction_type == 'restore':
                 # Merchants don't usually restore in this app version, but if they do, logic is generic
                 pass

            transaction = Transaction.objects.create(user=partner, type=transaction_type)
            for i in range(len(name)):
                if name[i] != "skip":
                    if quantity[i] == "":
                        continue
                    product = Product.objects.get(id=name[i])
                    
                    # Check stock for 'take'
                    if transaction_type == 'take':
                        if product.stock < Decimal(quantity[i]):
                            messages.error(request, f'الكمية المطلوبة من {product.name} غير متوفرة')
                            transaction.delete()
                            return redirect('base:partner_detail', partner_id)
                            
                    TransactionItem.objects.create(
                        transaction=transaction,
                        product=product,
                        quantity=Decimal(quantity[i]),
                    )
            messages.success(request, 'تم إضافة المعاملة بنجاح')
            return redirect('base:partner_detail', partner_id)

    context = {
        'partner': partner,
        'partner_transactions': transactions.order_by('-date'),
        'partner_products': partner_products,
        'products': products,
        'products_list': products_list,
        'partner_type': partner.user_type,
        'partner_type_display': get_partner_type_display(partner.user_type),
    }
    return render(request, 'partners/partner-detail.html', context)

def delete_transaction(request, partner_id, transaction_id):
    """Delete a transaction and reverse all stock/debt changes"""
    
    if request.method == 'POST':
        try:
            transaction = get_object_or_404(Transaction, id=transaction_id, user_id=partner_id)
            transaction.delete()  # Model's delete method handles stock/debt reversal
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})
