from django import forms
from .models import Category, Product, User, Transaction, TransactionItem

# Common CSS classes for form widgets
FORM_INPUT_CLASSES = (
    'w-full px-4 py-3 rounded-lg border border-slate-300 '
    'focus:border-primary-500 focus:ring-2 focus:ring-primary-200 '
    'outline-none transition-all text-right'
)

FORM_INPUT_CLASSES_GREEN = (
    'w-full px-4 py-3 rounded-lg border border-slate-300 '
    'focus:border-green-500 focus:ring-2 focus:ring-green-200 '
    'outline-none transition-all text-right'
)


class CategoryForm(forms.ModelForm):
    """Form for creating and editing categories."""
    
    class Meta:
        model = Category
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'name': 'اسم الفئة',
        }


class ProductForm(forms.ModelForm):
    """Form for creating and editing products."""
    
    class Meta:
        model = Product
        fields = ['name', 'category', 'price', 'stock']
        widgets = {
            'name': forms.TextInput(attrs={
                'id': 'productName',
                'name': 'name',
                'required': 'required',
                'class': FORM_INPUT_CLASSES,
                'placeholder': 'مثال: إلكترونيات'
            }),
            'category': forms.Select(attrs={
                'id': 'ProductCategory',
                'name': 'category',
                'required': 'required',
                'class': FORM_INPUT_CLASSES,
            }),
            'price': forms.NumberInput(attrs={
                'id': 'ProductPrice',
                'name': 'price',
                'required': 'required',
                'class': FORM_INPUT_CLASSES,
            }),
            'stock': forms.NumberInput(attrs={
                'id': 'ProductStock',
                'name': 'stock',
                'required': 'required',
                'class': FORM_INPUT_CLASSES,
            }),
        }
        labels = {
            'name': 'اسم المنتج',
            'category': 'الفئة',
            'price': 'السعر',
            'stock': 'الكمية',
        }


class UserForm(forms.ModelForm):
    """Form for creating and editing users (merchants/representatives)."""
    
    class Meta:
        model = User
        fields = ['user_type', 'username', 'email', 'first_name', 'last_name', 'phone', 'address']
        widgets = {
            'user_type': forms.Select(attrs={'class': 'hidden'}),
            'username': forms.TextInput(attrs={'class': FORM_INPUT_CLASSES}),
            'email': forms.EmailInput(attrs={'class': FORM_INPUT_CLASSES}),
            'first_name': forms.TextInput(attrs={'class': FORM_INPUT_CLASSES}),
            'last_name': forms.TextInput(attrs={'class': FORM_INPUT_CLASSES}),
            'phone': forms.TextInput(attrs={'class': FORM_INPUT_CLASSES}),
            'address': forms.TextInput(attrs={'class': FORM_INPUT_CLASSES}),
        }
        labels = {
            'username': 'اسم المستخدم',
            'email': 'البريد الإلكتروني',
            'first_name': 'الاسم الأول',
            'last_name': 'الاسم الأخير',
            'phone': 'رقم الهاتف',
            'address': 'العنوان',
        }


class TransactionForm(forms.ModelForm):
    """Form for creating and editing transactions."""
    
    class Meta:
        model = Transaction
        fields = ['user', 'products', 'amount', 'type']
        widgets = {
            'user': forms.Select(attrs={'class': FORM_INPUT_CLASSES}),
            'products': forms.SelectMultiple(attrs={'class': FORM_INPUT_CLASSES}),
            'amount': forms.NumberInput(attrs={
                'class': FORM_INPUT_CLASSES,
                'step': '0.01'
            }),
            'type': forms.Select(attrs={'class': FORM_INPUT_CLASSES}),
        }
        labels = {
            'user': 'المستخدم',
            'products': 'المنتجات',
            'amount': 'المبلغ',
            'type': 'النوع',
        }


class FeesForm(forms.Form):
    """Form for adding fees/expenses."""
    
    amount = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': FORM_INPUT_CLASSES_GREEN,
            'step': '0.01',
            'placeholder': '0.00'
        }),
        label='المبلغ'
    )
    description = forms.CharField(
        max_length=500,
        required=False,
        widget=forms.Textarea(attrs={
            'class': FORM_INPUT_CLASSES_GREEN,
            'rows': 3,
            'placeholder': 'وصف المنصرف (اختياري)'
        }),
        label='الوصف'
    )
