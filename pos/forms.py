"""Forms for POS app."""

from django import forms
from .models import Sale


class CheckoutForm(forms.Form):
    """Form for processing checkout."""
    
    customer_name = forms.CharField(
        required=False,
        max_length=255,
        label='اسم العميل',
        widget=forms.TextInput(attrs={
            'class': 'input input-bordered w-full',
            'placeholder': 'اسم العميل (اختياري)'
        })
    )
    customer_phone = forms.CharField(
        required=False,
        max_length=20,
        label='هاتف العميل',
        widget=forms.TextInput(attrs={
            'class': 'input input-bordered w-full',
            'placeholder': 'هاتف العميل (اختياري)'
        })
    )
    discount_percentage = forms.DecimalField(
        required=False,
        min_value=0,
        max_value=100,
        label='نسبة الخصم (%)',
        widget=forms.NumberInput(attrs={
            'class': 'input input-bordered w-full',
            'step': '0.01',
            'min': '0',
            'max': '100',
            'value': '0'
        })
    )
    payment_method = forms.ChoiceField(
        choices=Sale.PaymentMethod.choices,
        label='طريقة الدفع',
        widget=forms.RadioSelect(attrs={
            'class': 'radio radio-primary'
        })
    )
    amount_paid = forms.DecimalField(
        min_value=0,
        label='المبلغ المدفوع',
        widget=forms.NumberInput(attrs={
            'class': 'input input-bordered w-full text-2xl',
            'step': '0.01',
            'min': '0'
        })
    )
    notes = forms.CharField(
        required=False,
        label='ملاحظات',
        widget=forms.Textarea(attrs={
            'class': 'textarea textarea-bordered w-full',
            'placeholder': 'ملاحظات (اختياري)',
            'rows': 2
        })
    )
