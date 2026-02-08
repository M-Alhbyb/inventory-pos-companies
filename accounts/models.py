"""
Accounts models for multi-tenant SaaS platform.

This module contains models for:
- Subscription Plans
- Companies
- Company Subscriptions
- Users with roles
"""

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import timedelta


# =============================================================================
# SUBSCRIPTION PLAN
# =============================================================================

class SubscriptionPlan(models.Model):
    """Subscription plan defining features and limits."""
    
    name = models.CharField(max_length=100, verbose_name='اسم الخطة')
    description = models.TextField(blank=True, verbose_name='الوصف')
    
    # Limits
    max_users = models.IntegerField(default=5, verbose_name='الحد الأقصى للمستخدمين')
    max_products = models.IntegerField(default=100, verbose_name='الحد الأقصى للمنتجات')
    
    # Features
    has_inventory = models.BooleanField(default=True, verbose_name='يتضمن المخزون')
    has_pos = models.BooleanField(default=True, verbose_name='يتضمن نقطة البيع')
    
    # Pricing
    price_monthly = models.DecimalField(
        max_digits=10, decimal_places=2, default=0,
        verbose_name='السعر الشهري'
    )
    price_yearly = models.DecimalField(
        max_digits=10, decimal_places=2, default=0,
        verbose_name='السعر السنوي'
    )
    
    # Trial
    trial_days = models.IntegerField(default=14, verbose_name='أيام الفترة التجريبية')
    
    is_active = models.BooleanField(default=True, verbose_name='نشط')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'خطة الاشتراك'
        verbose_name_plural = 'خطط الاشتراك'
        ordering = ['price_monthly']
    
    def __str__(self):
        return self.name


# =============================================================================
# COMPANY
# =============================================================================

class Company(models.Model):
    """Company/tenant in the multi-tenant system."""
    
    name = models.CharField(max_length=255, verbose_name='اسم الشركة')
    email = models.EmailField(verbose_name='البريد الإلكتروني')
    phone = models.CharField(max_length=20, verbose_name='رقم الهاتف')
    address = models.TextField(blank=True, verbose_name='العنوان')
    logo = models.ImageField(
        upload_to='company_logos/', blank=True, null=True,
        verbose_name='الشعار'
    )
    
    # Tax settings
    tax_rate = models.DecimalField(
        max_digits=5, decimal_places=2, default=0,
        verbose_name='نسبة الضريبة (%)'
    )
    tax_name = models.CharField(
        max_length=50, default='VAT', blank=True,
        verbose_name='اسم الضريبة'
    )
    # PASHA : add company VAT number to print it in cashier receipt 
    
    is_active = models.BooleanField(default=True, verbose_name='نشط')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'شركة'
        verbose_name_plural = 'الشركات'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    @property
    def user_count(self):
        """Get current number of users in this company."""
        return self.users.count()
    
    @property
    def product_count(self):
        """Get current number of products in this company."""
        return self.products.count()


# =============================================================================
# COMPANY SUBSCRIPTION
# =============================================================================

class CompanySubscription(models.Model):
    """Links a company to a subscription plan with status tracking."""
    
    class Status(models.TextChoices):
        PENDING = 'pending', 'معلق'
        TRIAL = 'trial', 'تجريبي'
        ACTIVE = 'active', 'نشط'
        EXPIRED = 'expired', 'منتهي'
        CANCELLED = 'cancelled', 'ملغي'
    
    company = models.OneToOneField(
        Company, on_delete=models.CASCADE,
        related_name='subscription', verbose_name='الشركة'
    )
    plan = models.ForeignKey(
        SubscriptionPlan, on_delete=models.PROTECT,
        related_name='subscriptions', verbose_name='الخطة'
    )
    
    status = models.CharField(
        max_length=20, choices=Status.choices,
        default=Status.PENDING, verbose_name='الحالة'
    )
    
    start_date = models.DateField(null=True, blank=True, verbose_name='تاريخ البدء')
    end_date = models.DateField(null=True, blank=True, verbose_name='تاريخ الانتهاء')
    trial_end_date = models.DateField(null=True, blank=True, verbose_name='نهاية الفترة التجريبية')
    
    payment_verified = models.BooleanField(default=False, verbose_name='تم التحقق من الدفع')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'اشتراك الشركة'
        verbose_name_plural = 'اشتراكات الشركات'
    
    def __str__(self):
        return f"{self.company.name} - {self.plan.name}"
    
    def approve(self):
        """Approve pending subscription and start trial."""
        if self.status == self.Status.PENDING:
            self.status = self.Status.TRIAL
            self.start_date = timezone.now().date()
            self.trial_end_date = self.start_date + timedelta(days=self.plan.trial_days)
            self.save()
    
    def activate(self, months=1):
        """Activate subscription after payment."""
        self.status = self.Status.ACTIVE
        self.payment_verified = True
        if not self.start_date:
            self.start_date = timezone.now().date()
        self.end_date = self.start_date + timedelta(days=30 * months)
        self.save()
    
    @property
    def is_valid(self):
        """Check if subscription allows access."""
        if self.status == self.Status.TRIAL:
            return self.trial_end_date and self.trial_end_date >= timezone.now().date()
        elif self.status == self.Status.ACTIVE:
            return self.end_date and self.end_date >= timezone.now().date()
        return False


# =============================================================================
# USER
# =============================================================================

class User(AbstractUser):
    """Custom user with company association and role."""
    
    class Role(models.TextChoices):
        PLATFORM_MANAGER = 'platform_manager', 'مدير المنصة'
        COMPANY_MANAGER = 'company_manager', 'مدير الشركة'
        ACCOUNTANT = 'accountant', 'محاسب'
        REPRESENTATIVE = 'representative', 'مندوب'
        CASHIER = 'cashier', 'كاشير'
    
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE,
        related_name='users', null=True, blank=True,
        verbose_name='الشركة'
    )
    
    role = models.CharField(
        max_length=20, choices=Role.choices,
        default=Role.REPRESENTATIVE, verbose_name='الدور'
    )
    
    phone = models.CharField(max_length=20, blank=True, verbose_name='رقم الهاتف')
    
    # For representatives: products currently held
    products_count = models.IntegerField(default=0, verbose_name='عدد المنتجات')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'مستخدم'
        verbose_name_plural = 'المستخدمين'
    
    def __str__(self):
        return self.get_full_name() or self.username
    
    @property
    def is_platform_manager(self):
        return self.role == self.Role.PLATFORM_MANAGER
    
    @property
    def is_company_manager(self):
        return self.role == self.Role.COMPANY_MANAGER
    
    @property
    def is_accountant(self):
        return self.role == self.Role.ACCOUNTANT
    
    @property
    def is_representative(self):
        return self.role == self.Role.REPRESENTATIVE
    
    @property
    def is_cashier(self):
        return self.role == self.Role.CASHIER
