"""Forms for inventory app."""

from django import forms
from .models import Category, Product, Transaction, TransactionItem


class CategoryForm(forms.ModelForm):
    """Form for categories."""
    
    class Meta:
        model = Category
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'اسم الفئة'
            }),
            'description': forms.Textarea(attrs={
                'class': 'textarea textarea-bordered w-full',
                'placeholder': 'الوصف',
                'rows': 3
            }),
        }


class ProductForm(forms.ModelForm):
    """Form for products."""
    
    class Meta:
        model = Product
        fields = ['category', 'name', 'description', 'price', 'cost', 
                  'stock', 'low_stock_threshold', 'sku', 'barcode', 'image', 'is_active']
        widgets = {
            'category': forms.Select(attrs={
                'class': 'select select-bordered w-full'
            }),
            'name': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'اسم المنتج'
            }),
            'description': forms.Textarea(attrs={
                'class': 'textarea textarea-bordered w-full',
                'placeholder': 'الوصف',
                'rows': 3
            }),
            'price': forms.NumberInput(attrs={
                'class': 'input input-bordered w-full',
                'step': '0.01',
                'min': '0'
            }),
            'cost': forms.NumberInput(attrs={
                'class': 'input input-bordered w-full',
                'step': '0.01',
                'min': '0'
            }),
            'stock': forms.NumberInput(attrs={
                'class': 'input input-bordered w-full',
                'min': '0'
            }),
            'low_stock_threshold': forms.NumberInput(attrs={
                'class': 'input input-bordered w-full',
                'min': '0'
            }),
            'sku': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'رمز المنتج'
            }),
            'barcode': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'الباركود'
            }),
        }
    
    def __init__(self, *args, company=None, **kwargs):
        super().__init__(*args, **kwargs)
        if company:
            self.fields['category'].queryset = Category.objects.filter(company=company)


class TransactionForm(forms.ModelForm):
    """Form for transactions."""
    
    class Meta:
        model = Transaction
        fields = ['user', 'type', 'notes']
        widgets = {
            'user': forms.Select(attrs={
                'class': 'select select-bordered w-full'
            }),
            'type': forms.Select(attrs={
                'class': 'select select-bordered w-full'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'textarea textarea-bordered w-full',
                'placeholder': 'ملاحظات',
                'rows': 2
            }),
        }
    
    def __init__(self, *args, company=None, **kwargs):
        from accounts.models import User
        super().__init__(*args, **kwargs)
        if company:
            # Only show representatives
            self.fields['user'].queryset = User.objects.filter(
                company=company, 
                role=User.Role.REPRESENTATIVE
            )
