from django import forms
from .models import Category, Product, User, Transaction, TransactionItem

class CategoryForm(forms.ModelForm):
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
    class Meta:
        model = Product
        fields = ['name', 'category', 'price', 'stock']
        widgets = {
            'name': forms.TextInput(attrs={
            "id":"productName",
            "name":"name",
            "required": "required",
            "class":"w-full px-4 py-3 rounded-lg border border-slate-300 focus:border-primary-500 focus:ring-2 focus:ring-primary-200 outline-none transition-all text-right",
            "placeholder":"مثال: إلكترونيات"
            }),
           'category': forms.Select(attrs={
            "id":"ProductCategory",
            "name":"category",
            "required": "required",
            "class":"w-full px-4 py-3 rounded-lg border border-slate-300 focus:border-primary-500 focus:ring-2 focus:ring-primary-200 outline-none transition-all text-right",
            "placeholder":"مثال: إلكترونيات"
            }),
            'price': forms.NumberInput(attrs={
            "id":"ProductPrice",
            "name":"price",
            "required": "required",
            "class":"w-full px-4 py-3 rounded-lg border border-slate-300 focus:border-primary-500 focus:ring-2 focus:ring-primary-200 outline-none transition-all text-right",
            }),
            'stock': forms.NumberInput(attrs={
            "id":"ProductStock",
            "name":"stock",
            "required": "required",
            "class":"w-full px-4 py-3 rounded-lg border border-slate-300 focus:border-primary-500 focus:ring-2 focus:ring-primary-200 outline-none transition-all text-right",
            }),
        }
        labels = {
            'name': 'اسم المنتج',
            'category': 'الفئة',
            'price': 'السعر',
            'stock': 'الكمية',
        }

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['user_type','username', 'email', 'first_name', 'last_name', 'phone', 'address']
        widgets = {
            'user_type': forms.Select(attrs={'class': 'hidden'}),
            'username': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border border-slate-300 focus:border-primary-500 focus:ring-2 focus:ring-primary-200 outline-none transition-all text-right'}),
            'email': forms.EmailInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border border-slate-300 focus:border-primary-500 focus:ring-2 focus:ring-primary-200 outline-none transition-all text-right'}),
            'first_name': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border border-slate-300 focus:border-primary-500 focus:ring-2 focus:ring-primary-200 outline-none transition-all text-right'}),
            'last_name': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border border-slate-300 focus:border-primary-500 focus:ring-2 focus:ring-primary-200 outline-none transition-all text-right'}),
            'phone': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border border-slate-300 focus:border-primary-500 focus:ring-2 focus:ring-primary-200 outline-none transition-all text-right'}),
            'address': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border border-slate-300 focus:border-primary-500 focus:ring-2 focus:ring-primary-200 outline-none transition-all text-right'}),
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
    class Meta:
        model = Transaction
        fields = ['user', 'products', 'amount', 'type']
        widgets = {
            'user': forms.Select(attrs={'class': 'w-full px-4 py-3 rounded-lg border border-slate-300 focus:border-primary-500 focus:ring-2 focus:ring-primary-200 outline-none transition-all text-right'}),
            'products': forms.SelectMultiple(attrs={'class': 'w-full px-4 py-3 rounded-lg border border-slate-300 focus:border-primary-500 focus:ring-2 focus:ring-primary-200 outline-none transition-all text-right'}),
            'amount': forms.NumberInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border border-slate-300 focus:border-primary-500 focus:ring-2 focus:ring-primary-200 outline-none transition-all text-right', 'step': '0.01'}),
            'type': forms.Select(attrs={'class': 'w-full px-4 py-3 rounded-lg border border-slate-300 focus:border-primary-500 focus:ring-2 focus:ring-primary-200 outline-none transition-all text-right'}),
        }
        labels = {
            'user': 'المستخدم',
            'products': 'المنتجات',
            'amount': 'المبلغ',
            'type': 'النوع',
        }