"""
POS models for multi-tenant SaaS platform.

This module contains models for:
- Sales
- Sale Items
"""

from django.db import models
from django.db.models import Sum
from decimal import Decimal
import uuid


def generate_receipt_number():
    """Generate a unique receipt number."""
    return f"RCP-{uuid.uuid4().hex[:8].upper()}"


# =============================================================================
# SALE
# =============================================================================

class Sale(models.Model):
    """Point of sale transaction."""
    
    class PaymentMethod(models.TextChoices):
        CASH = 'cash', 'نقدي'
        CARD = 'card', 'بطاقة'
        TRANSFER = 'transfer', 'تحويل'
    
    class Status(models.TextChoices):
        COMPLETED = 'completed', 'مكتمل'
        REFUNDED = 'refunded', 'مسترد'
        CANCELLED = 'cancelled', 'ملغي'
    
    company = models.ForeignKey(
        'accounts.Company', on_delete=models.CASCADE,
        related_name='sales', verbose_name='الشركة'
    )
    cashier = models.ForeignKey(
        'accounts.User', on_delete=models.SET_NULL,
        null=True, related_name='sales', verbose_name='الكاشير'
    )
    
    # Receipt
    receipt_number = models.CharField(
        max_length=50, unique=True, default=generate_receipt_number,
        verbose_name='رقم الفاتورة'
    )
    
    # Customer (optional)
    customer_name = models.CharField(
        max_length=255, blank=True,
        verbose_name='اسم العميل'
    )
    customer_phone = models.CharField(
        max_length=20, blank=True,
        verbose_name='هاتف العميل'
    )
    
    # Amounts
    subtotal = models.DecimalField(
        max_digits=10, decimal_places=2, default=0,
        verbose_name='المجموع الفرعي'
    )
    discount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0,
        verbose_name='الخصم'
    )
    discount_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, default=0,
        verbose_name='نسبة الخصم (%)'
    )
    tax_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0,
        verbose_name='الضريبة'
    )
    total = models.DecimalField(
        max_digits=10, decimal_places=2, default=0,
        verbose_name='الإجمالي'
    )
    
    # Payment
    payment_method = models.CharField(
        max_length=20, choices=PaymentMethod.choices,
        default=PaymentMethod.CASH, verbose_name='طريقة الدفع'
    )
    amount_paid = models.DecimalField(
        max_digits=10, decimal_places=2, default=0,
        verbose_name='المبلغ المدفوع'
    )
    change = models.DecimalField(
        max_digits=10, decimal_places=2, default=0,
        verbose_name='الباقي'
    )
    
    status = models.CharField(
        max_length=20, choices=Status.choices,
        default=Status.COMPLETED, verbose_name='الحالة'
    )
    
    notes = models.TextField(blank=True, verbose_name='ملاحظات')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ البيع')
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'عملية بيع'
        verbose_name_plural = 'عمليات البيع'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.receipt_number} - {self.total}"
    
    def calculate_totals(self):
        """Calculate subtotal, tax, and total from items."""
        # Calculate subtotal from items
        self.subtotal = self.items.aggregate(
            total=Sum('total')
        )['total'] or Decimal('0')
        
        # Apply discount
        if self.discount_percentage > 0:
            self.discount = self.subtotal * (self.discount_percentage / 100)
        
        after_discount = self.subtotal - self.discount
        
        # Apply tax from company settings
        if self.company.tax_rate > 0:
            self.tax_amount = after_discount * (self.company.tax_rate / 100)
        
        # Calculate total
        self.total = after_discount + self.tax_amount
        
        # Calculate change
        self.change = max(Decimal('0'), self.amount_paid - self.total)
        
        self.save()
    
    def apply_stock_changes(self):
        """Reduce product stock after sale."""
        for item in self.items.all():
            item.product.stock -= item.quantity
            item.product.save()
    
    def reverse_stock_changes(self):
        """Restore product stock (for refunds/cancellations)."""
        for item in self.items.all():
            item.product.stock += item.quantity
            item.product.save()
    
    def refund(self):
        """Process refund for this sale."""
        if self.status == self.Status.COMPLETED:
            self.status = self.Status.REFUNDED
            self.reverse_stock_changes()
            self.save()
            return True
        return False


# =============================================================================
# SALE ITEM
# =============================================================================

class SaleItem(models.Model):
    """Individual item in a sale."""
    
    sale = models.ForeignKey(
        Sale, on_delete=models.CASCADE,
        related_name='items', verbose_name='عملية البيع'
    )
    product = models.ForeignKey(
        'inventory.Product', on_delete=models.PROTECT,
        related_name='sale_items', verbose_name='المنتج'
    )
    
    quantity = models.IntegerField(default=1, verbose_name='الكمية')
    price = models.DecimalField(
        max_digits=10, decimal_places=2,
        verbose_name='السعر'
    )
    cost = models.DecimalField(
        max_digits=10, decimal_places=2,
        verbose_name='التكلفة'
    )
    total = models.DecimalField(
        max_digits=10, decimal_places=2,
        verbose_name='الإجمالي'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'عنصر بيع'
        verbose_name_plural = 'عناصر البيع'
    
    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
    
    def save(self, *args, **kwargs):
        # Auto-set price and cost from product if not set
        if not self.price:
            self.price = self.product.price
        if not self.cost:
            self.cost = self.product.cost
        # Calculate total
        self.total = self.price * self.quantity
        super().save(*args, **kwargs)
    
    @property
    def profit(self):
        """Calculate profit for this item."""
        return (self.price - self.cost) * self.quantity
