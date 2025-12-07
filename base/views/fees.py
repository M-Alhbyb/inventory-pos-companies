"""Fees/expenses management view."""

from decimal import Decimal

from django.shortcuts import redirect
from django.contrib import messages

from base.models import Transaction
from base.forms import FeesForm


def add_fees(request):
    """
    Handle fees transaction creation.
    Fees are expenses that don't involve products or users.
    """
    if request.method != 'POST':
        return redirect('base:dashboard')
    
    form = FeesForm(request.POST)
    if form.is_valid():
        amount = form.cleaned_data['amount']
        
        # Create the fees transaction
        Transaction.objects.create(
            user=None,  # Fees don't have a user
            amount=amount,
            type='fees'
        )
        
        messages.success(request, f'تم إضافة منصرف بقيمة {amount} ج.س بنجاح')
    else:
        messages.error(request, 'حدث خطأ في البيانات المدخلة')
    
    return redirect('base:dashboard')