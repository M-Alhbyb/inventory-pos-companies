from django.shortcuts import render, redirect, get_object_or_404
from base.models import Product, Transaction, TransactionItem, User
from base.forms import UserForm
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db import transaction as db_transaction
from decimal import Decimal

# Create your views here.

def representatives_view(request):
    representatives = User.objects.filter(user_type='representative').all()
    
    # Handle search
    q = request.GET.get('q')
    if q:
        representatives = representatives.filter(
            Q(user__username__icontains=q) |
            Q(user__first_name__icontains=q) |
            Q(user__last_name__icontains=q) |
            Q(user__phone__icontains=q)
        )

    user_form = UserForm()
    
    edit_user_form = UserForm(prefix='edit')

    context = {
        'representatives': representatives,
        'user_form': user_form,
        'edit_user_form': edit_user_form,
    }
    return render(request, 'representatives/representatives.html', context)

@require_http_methods(["POST"])
def add_representative(request):
    try:
        user_form = UserForm(request.POST)
        
        if user_form.is_valid():
            with db_transaction.atomic():
                user = user_form.save(commit=False)
                user.set_password('password123') # Default password
                user.save()
                
            messages.success(request, 'تم إضافة المندوب بنجاح')
            return JsonResponse({'success': True})
        else:
            errors = {}
            errors.update(user_form.errors)
            return JsonResponse({'success': False, 'error': str(errors)})
            
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@require_http_methods(["POST", "GET"])
def edit_representative(request, representative_id):
    try:
        if request.method == "GET":
            representative = get_object_or_404(User, id=representative_id)
            user = representative
            
            user_form = UserForm(instance=user)
            
            context = {
                'user_form': user_form,
            }
            final_form = {}
            for field in user_form:
                val = field.value()
                final_form[field.name] = str(val) if val is not None else ""

            return JsonResponse({'success': True, 'fields': final_form})
        
        representative = get_object_or_404(User, id=representative_id)
        user = representative
        
        user_form = UserForm(request.POST, instance=user, prefix='edit')
        
        if user_form.is_valid():
            user_form.save()
            
            messages.success(request, 'تم تحديث بيانات المندوب بنجاح')
            return JsonResponse({'success': True})
        else:
            errors = {}
            errors.update(user_form.errors)
            return JsonResponse({'success': False, 'error': str(errors)})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@require_http_methods(["POST"])
def delete_representative(request, representative_id):
    try:
        representative = get_object_or_404(User, id=representative_id)
        representative.delete()
        
        messages.success(request, 'تم حذف المندوب بنجاح')
        return JsonResponse({'success': True})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

def representative_detail(request, representative_id):
    representative = get_object_or_404(User, id=representative_id)
    products = Product.objects.all()
    # Get all transactions for this representative
    transactions = Transaction.objects.filter(user=representative).prefetch_related('items__product')
    representative_products = TransactionItem.objects.filter(transaction__user=representative)
    products_list = list(products.values('id', 'name', 'stock'))
    products_list.insert(0, {'id': "skip", 'name': 'اختر منتج', 'stock': ''})

    if request.method == 'POST':
        transaction_type = request.POST.get('type')
        
        if transaction_type in ['take', 'restore']:
            name = request.POST.getlist('product') 
            quantity = request.POST.getlist('quantity')
            
            if len(name) == 1:
                if name[0] == "skip":
                    messages.error(request, 'يجب اختيار منتج')
                    return redirect('base:representative_detail', representative_id)
            
            transaction = Transaction.objects.create(user=representative, type=transaction_type)
            for i in range(len(name)):
                product = Product.objects.get(id=name[i])
                if name[i] != "skip":
                    if quantity[i] == "":
                        continue
                    if product.stock < Decimal(quantity[i]):
                        messages.error(request, f'الكمية المطلوبة من {product.name} غير متوفرة')
                        transaction.delete()
                        return redirect('base:representative_detail', representative_id)
                    TransactionItem.objects.create(
                        transaction=transaction,
                        product=product,
                        quantity=Decimal(quantity[i]),
                    )
            messages.success(request, 'تم إضافة المعاملة بنجاح')
            return redirect('base:representative_detail', representative_id)

    context = {
        'representative': representative,
        'representative_transactions': transactions.order_by('-date'),
        'representative_products': representative_products,
        'products': products,
        'products_list': products_list,
    }
    return render(request, 'representatives/representative-detail.html', context)

def delete_transaction(request, representative_id, transaction_id):
    """Delete a transaction and reverse all stock/debt changes"""
    
    if request.method == 'POST':
        try:
            transaction = get_object_or_404(Transaction, id=transaction_id, user_id=representative_id)
            transaction.delete()  # Model's delete method handles stock/debt reversal
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})
