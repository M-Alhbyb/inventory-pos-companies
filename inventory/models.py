"""
Inventory models for multi-tenant SaaS platform.

This module contains models for:
- Categories
- Products
- Transactions (take/restore/payment)
- Transaction Items
"""

from django.db import models
from django.db.models import Sum
from decimal import Decimal


# =============================================================================
# CATEGORY
# =============================================================================

class Category(models.Model):
    """Product category, scoped to a company."""
    
    company = models.ForeignKey(
        'accounts.Company', on_delete=models.CASCADE,
        related_name='categories', verbose_name='الشركة'
    )
    name = models.CharField(max_length=255, verbose_name='اسم الفئة')
    description = models.TextField(blank=True, verbose_name='الوصف')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'فئة'
        verbose_name_plural = 'الفئات'
        ordering = ['name']
        unique_together = ['company', 'name']
    
    def __str__(self):
        return self.name


# =============================================================================
# PRODUCT
# =============================================================================

class Product(models.Model):
    """Product with stock tracking, scoped to a company."""
    
    company = models.ForeignKey(
        'accounts.Company', on_delete=models.CASCADE,
        related_name='products', verbose_name='الشركة'
    )
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='products',
        verbose_name='الفئة'
    )
    
    name = models.CharField(max_length=255, verbose_name='اسم المنتج')
    description = models.TextField(blank=True, verbose_name='الوصف')
    
    # Pricing
    price = models.DecimalField(
        max_digits=10, decimal_places=2, default=0,
        verbose_name='سعر البيع'
    )
    cost = models.DecimalField(
        max_digits=10, decimal_places=2, default=0,
        verbose_name='سعر التكلفة'
    )
    
    # Stock
    stock = models.IntegerField(default=0, verbose_name='المخزون')
    low_stock_threshold = models.IntegerField(
        default=10, verbose_name='حد المخزون المنخفض'
    )
    
    # Identification
    sku = models.CharField(
        max_length=100, blank=True,
        verbose_name='رمز المنتج (SKU)'
    )
    barcode = models.CharField(
        max_length=100, blank=True,
        verbose_name='الباركود'
    )
    
    image = models.ImageField(
        upload_to='products/', blank=True, null=True,
        verbose_name='صورة المنتج'
    )
    
    is_active = models.BooleanField(default=True, verbose_name='نشط')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'منتج'
        verbose_name_plural = 'المنتجات'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    @property
    def is_low_stock(self):
        """Check if product is below low stock threshold."""
        return self.stock <= self.low_stock_threshold
    
    @property
    def profit_margin(self):
        """Calculate profit margin percentage."""
        if self.cost and self.cost > 0:
            return ((self.price - self.cost) / self.cost) * 100
        return Decimal('0')


# =============================================================================
# TRANSACTION
# =============================================================================

class Transaction(models.Model):
    """Transaction for tracking product movements and payments."""
    
    class Type(models.TextChoices):
        TAKE = 'take', 'أخذ'
        RESTORE = 'restore', 'إرجاع'
        PAYMENT = 'payment', 'دفع'
    
    class Status(models.TextChoices):
        PENDING = 'pending', 'معلق'
        APPROVED = 'approved', 'موافق عليه'
        REJECTED = 'rejected', 'مرفوض'
    
    company = models.ForeignKey(
        'accounts.Company', on_delete=models.CASCADE,
        related_name='transactions', verbose_name='الشركة'
    )
    user = models.ForeignKey(
        'accounts.User', on_delete=models.SET_NULL,
        null=True, related_name='transactions',
        verbose_name='المندوب'
    )
    
    type = models.CharField(
        max_length=20, choices=Type.choices,
        verbose_name='نوع المعاملة'
    )
    status = models.CharField(
        max_length=20, choices=Status.choices,
        default=Status.PENDING, verbose_name='الحالة'
    )
    
    amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0,
        verbose_name='المبلغ'
    )
    notes = models.TextField(blank=True, verbose_name='ملاحظات')
    
    # Approval tracking
    approved_by = models.ForeignKey(
        'accounts.User', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='approved_transactions',
        verbose_name='تمت الموافقة بواسطة'
    )
    approved_at = models.DateTimeField(null=True, blank=True, verbose_name='تاريخ الموافقة')
    
    date = models.DateTimeField(auto_now_add=True, verbose_name='التاريخ')
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'معاملة'
        verbose_name_plural = 'المعاملات'
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.get_type_display()} - {self.user} - {self.amount}"
    
    def update_totals(self):
        """Update transaction amount from items."""
        total = self.items.aggregate(total=Sum('total'))['total'] or Decimal('0')
        self.amount = total
        self.save(update_fields=['amount'])
    
    def approve(self, approved_by):
        """Approve the transaction and apply stock changes."""
        from django.utils import timezone
        
        if self.status != self.Status.PENDING:
            return False
        
        self.status = self.Status.APPROVED
        self.approved_by = approved_by
        self.approved_at = timezone.now()
        self.save()
        
        # Apply stock changes
        for item in self.items.all():
            if self.type == self.Type.TAKE:
                item.product.stock -= item.quantity
            elif self.type == self.Type.RESTORE:
                item.product.stock += item.quantity
            item.product.save()
        
        # Update user's products count
        self._update_user_products_count()
        return True
    
    def reject(self, rejected_by):
        """Reject the transaction."""
        if self.status != self.Status.PENDING:
            return False
        
        self.status = self.Status.REJECTED
        self.approved_by = rejected_by
        self.save()
        return True
    
    def _update_user_products_count(self):
        """Recalculate user's product count from approved transactions."""
        if not self.user:
            return
        
        taken = Transaction.objects.filter(
            user=self.user, 
            type=self.Type.TAKE, 
            status=self.Status.APPROVED
        ).aggregate(total=Sum('items__quantity'))['total'] or 0
        
        restored = Transaction.objects.filter(
            user=self.user, 
            type=self.Type.RESTORE, 
            status=self.Status.APPROVED
        ).aggregate(total=Sum('items__quantity'))['total'] or 0
        
        self.user.products_count = taken - restored
        self.user.save(update_fields=['products_count'])


# =============================================================================
# TRANSACTION ITEM
# =============================================================================

class TransactionItem(models.Model):
    """Individual item within a transaction."""
    
    transaction = models.ForeignKey(
        Transaction, on_delete=models.CASCADE,
        related_name='items', verbose_name='المعاملة'
    )
    product = models.ForeignKey(
        Product, on_delete=models.PROTECT,
        related_name='transaction_items', verbose_name='المنتج'
    )
    
    quantity = models.IntegerField(default=1, verbose_name='الكمية')
    price = models.DecimalField(
        max_digits=10, decimal_places=2,
        verbose_name='السعر'
    )
    total = models.DecimalField(
        max_digits=10, decimal_places=2,
        verbose_name='الإجمالي'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'عنصر معاملة'
        verbose_name_plural = 'عناصر المعاملات'
    
    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
    
    def save(self, *args, **kwargs):
        # Auto-calculate total
        if not self.price:
            self.price = self.product.price
        self.total = self.price * self.quantity
        super().save(*args, **kwargs)
        
        # Update transaction total
        self.transaction.update_totals()
