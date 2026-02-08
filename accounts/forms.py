"""Forms for accounts app."""

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, Company, SubscriptionPlan


class CompanyRegistrationForm(forms.ModelForm):
    """Form for company registration."""
    
    # Company manager credentials
    username = forms.CharField(
        max_length=150,
        label='اسم المستخدم',
        widget=forms.TextInput(attrs={
            'class': 'input input-bordered w-full',
            'placeholder': 'اسم المستخدم'
        })
    )
    password1 = forms.CharField(
        label='كلمة المرور',
        widget=forms.PasswordInput(attrs={
            'class': 'input input-bordered w-full',
            'placeholder': 'كلمة المرور'
        })
    )
    password2 = forms.CharField(
        label='تأكيد كلمة المرور',
        widget=forms.PasswordInput(attrs={
            'class': 'input input-bordered w-full',
            'placeholder': 'تأكيد كلمة المرور'
        })
    )
    
    plan = forms.ModelChoiceField(
        queryset=SubscriptionPlan.objects.filter(is_active=True),
        label='خطة الاشتراك',
        widget=forms.RadioSelect(attrs={'class': 'radio radio-primary'})
    )
    
    class Meta:
        model = Company
        fields = ['name', 'email', 'phone', 'address']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'اسم الشركة'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'البريد الإلكتروني'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'رقم الهاتف'
            }),
            'address': forms.Textarea(attrs={
                'class': 'textarea textarea-bordered w-full',
                'placeholder': 'العنوان',
                'rows': 3
            }),
        }
    
    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('كلمات المرور غير متطابقة')
        return password2
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('اسم المستخدم موجود بالفعل')
        return username


class CustomAuthenticationForm(AuthenticationForm):
    """Custom login form with styled widgets."""
    
    username = forms.CharField(
        label='اسم المستخدم',
        widget=forms.TextInput(attrs={
            'class': 'input input-bordered w-full',
            'placeholder': 'اسم المستخدم',
            'autofocus': True
        })
    )
    password = forms.CharField(
        label='كلمة المرور',
        widget=forms.PasswordInput(attrs={
            'class': 'input input-bordered w-full',
            'placeholder': 'كلمة المرور'
        })
    )


class UserForm(forms.ModelForm):
    """Form for adding/editing company users."""
    
    password = forms.CharField(
        required=False,
        label='كلمة المرور',
        widget=forms.PasswordInput(attrs={
            'class': 'input input-bordered w-full',
            'placeholder': 'اتركه فارغاً للاحتفاظ بكلمة المرور الحالية'
        })
    )
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'phone', 'role']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'اسم المستخدم'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'الاسم الأول'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'الاسم الأخير'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'البريد الإلكتروني'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'رقم الهاتف'
            }),
            'role': forms.Select(attrs={
                'class': 'select select-bordered w-full'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Exclude platform_manager from role choices for company users
        self.fields['role'].choices = [
            choice for choice in User.Role.choices 
            if choice[0] != User.Role.PLATFORM_MANAGER
        ]


class CompanySettingsForm(forms.ModelForm):
    """Form for company settings including tax."""
    
    class Meta:
        model = Company
        fields = ['name', 'email', 'phone', 'address', 'logo', 'tax_rate', 'tax_name']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'input input-bordered w-full'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'input input-bordered w-full'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'input input-bordered w-full'
            }),
            'address': forms.Textarea(attrs={
                'class': 'textarea textarea-bordered w-full',
                'rows': 3
            }),
            'tax_rate': forms.NumberInput(attrs={
                'class': 'input input-bordered w-full',
                'step': '0.01',
                'min': '0',
                'max': '100'
            }),
            'tax_name': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'مثال: VAT, ضريبة القيمة المضافة'
            }),
        }
