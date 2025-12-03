from django.shortcuts import render, get_object_or_404, redirect
from base.models import User, USER_TYPES, Product, Transaction, TransactionItem
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.db import transaction as db_transaction
from decimal import Decimal

from base.forms import UserForm, CategoryForm

def merchants_view(request):
    merchants = User.objects.filter(user_type=USER_TYPES[1][0]).all()
    
    # Handle search
    q = request.GET.get('q')
    if q:
        merchants = merchants.filter(
            Q(user__username__icontains=q) |
            Q(user__first_name__icontains=q) |
            Q(user__last_name__icontains=q) |
            Q(user__phone__icontains=q)
        )

    user_form = UserForm()
     
    edit_user_form = UserForm(prefix='edit')

    context = {
        'merchants': merchants,
        'user_form': user_form,
        'edit_user_form': edit_user_form,
    }
    return render(request, 'merchants.html', context)

@require_http_methods(["POST"])
def add_merchant(request):
    try:
        user_form = UserForm(request.POST)
        
        if user_form.is_valid():
            with db_transaction.atomic():
                user = user_form.save(commit=False)
                user.user_type = USER_TYPES[1][0]
                user.set_password('password123') # Default password
                user.save()
                
            messages.success(request, 'تم إضافة التاجر بنجاح')
            return JsonResponse({'success': True})
        else:
            errors = {}
            errors.update(user_form.errors)
            return JsonResponse({'success': False, 'error': str(errors)})
            
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@require_http_methods(["POST", "GET"])
def edit_merchant(request, merchant_id):
    try:
        if request.method == "GET":
            merchant = get_object_or_404(User, id=merchant_id)
            user = merchant
            
            user_form = UserForm(instance=user)
            
            context = {
                'user_form': user_form,
            }
            final_form = {}
            for field in user_form:
                val = field.value()
                final_form[field.name] = str(val) if val is not None else ""

            return JsonResponse({'success': True, 'fields': final_form})
        
        user = get_object_or_404(User, id=merchant_id)
        
        user_form = UserForm(request.POST, instance=user, prefix='edit')
        
        if user_form.is_valid():
            user = user_form.save(commit=False)
            user.user_type = USER_TYPES[1][0]
            user.save()
            
            messages.success(request, 'تم تحديث بيانات التاجر بنجاح')
            return JsonResponse({'success': True})
        else:
            errors = {}
            errors.update(user_form.errors)
            return JsonResponse({'success': False, 'error': str(errors)})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@require_http_methods(["POST"])
def delete_merchant(request, merchant_id):
    try:
        merchant = get_object_or_404(User, id=merchant_id)
        merchant.delete()
        
        messages.success(request, 'تم حذف التاجر بنجاح')
        return JsonResponse({'success': True})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

def merchant_detail(request, merchant_id):
    merchant = get_object_or_404(User, id=merchant_id)
    products = Product.objects.all()
    # Get all transactions for this merchant
    transactions = Transaction.objects.filter(user=merchant).prefetch_related('items__product')
    merchant_products = TransactionItem.objects.filter(transaction__user=merchant)
    products_list = list(products.values('id', 'name', 'stock'))
    products_list.insert(0, {'id': "skip", 'name': 'اختر منتج', 'stock': ''})

    if request.method == 'POST':
        amount = request.POST.get('amount')
        if amount:
            if amount == "":
                messages.error(request, 'يجب إدخال المبلغ')
                return redirect('base:merchant_detail', merchant_id)
            else:
                Transaction.objects.create(user=merchant, type='payment', amount=Decimal(amount))
                messages.success(request, 'تم سداد المبلغ بنجاح')
                return redirect('base:merchant_detail', merchant_id)

        name = request.POST.getlist('product') 
        quantity = request.POST.getlist('quantity')
        if len(name) == 1:
            if name[0] == "skip":
                messages.error(request, 'يجب اختيار منتج')
                return redirect('base:merchant_detail', merchant_id)
        transaction=Transaction.objects.create(user=merchant, type='take')
        for i in range(len(name)):
            if name[i] != "skip":
                if quantity[i] == "":
                    continue
                product = Product.objects.get(id=name[i])
                if product.stock < Decimal(quantity[i]):
                    messages.error(request, f'الكمية المطلوبة من {product.name} غير متوفرة')
                    transaction.delete()
                    return redirect('base:merchant_detail', merchant_id)
                TransactionItem.objects.create(
                    transaction=transaction,
                    product=product,
                    quantity=Decimal(quantity[i]),
                )
        messages.success(request, 'تم إعطاء المنتجات بنجاح')
        return redirect('base:merchant_detail', merchant_id)

    context = {
        'merchant': merchant,
        'merchant_transactions': transactions.order_by('-date'),
        'merchant_products': merchant_products,
        'products': products,
        'products_list': products_list,
    }
    return render(request, 'merchants/merchant-detail.html', context)

def delete_transaction(request, merchant_id, transaction_id):
    """Delete a transaction and reverse all stock/debt changes"""
    
    if request.method == 'POST':
        try:
            transaction = get_object_or_404(Transaction, id=transaction_id, user_id=merchant_id)
            transaction.delete()  # Model's delete method handles stock/debt reversal
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


