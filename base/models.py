from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import Sum
from decimal import Decimal


class Category(models.Model):
    """Product category model."""
    
    name = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "الفئة"
        verbose_name_plural = "الفئات"


class Product(models.Model):
    """Product model with stock tracking."""
    
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    estimated_stock_out = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name

    @property
    def days_until_stock_out(self):
        """Calculate days until estimated stock out."""
        if self.estimated_stock_out:
            from django.utils import timezone
            delta = self.estimated_stock_out - timezone.now()
            return max(delta.days, 0)
        return None

    class Meta:
        verbose_name = "المنتج"
        verbose_name_plural = "المنتجات"


USER_TYPES = (
    ('admin', 'مشرف'),
    ('merchant', 'تاجر'),
    ('representative', 'مندوب')
)


class User(AbstractUser):
    """Custom user model with extended fields for merchants and representatives."""
    
    phone = models.CharField(max_length=255)
    address = models.TextField()
    user_type = models.CharField(
        max_length=20,
        choices=USER_TYPES,
        default=USER_TYPES[0][0],
        blank=False
    )
    debt = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    products_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.username} - {self.user_type}"

    class Meta:
        verbose_name = "المستخدم"
        verbose_name_plural = "المستخدمين"


TRANSACTION_TYPES = (
    ('take', 'أخذ'),
    ('payment', 'دفع'),
    ('restore', 'إرجاع'),
    ('fees', 'منصرف')
)


class Transaction(models.Model):
    """Transaction model for tracking product movements and payments."""
    
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='transactions'
    )
    products = models.ManyToManyField(
        Product,
        related_name='transactions',
        blank=True
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.amount:
            return f"{self.get_type_display()} - {self.amount}"
        return f"{self.get_type_display()} - {self.user.username if self.user else 'Unknown'}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.update_totals()

    def update_totals(self):
        """Update transaction amount and user debt/product counts."""
        # Update amount by calculating total from TransactionItems for 'take' and 'restore'
        if self.type in ['take', 'restore']:
            total = self.items.aggregate(total=Sum('total'))['total']
            self.amount = total if total else Decimal('0.00')
            product_ids = self.items.values_list('product_id', flat=True)
            self.products.set(product_ids)
            Transaction.objects.filter(pk=self.pk).update(amount=self.amount)

        # Update user debt for merchants
        if self.user and self.user.user_type == 'merchant':
            if self.type == 'take':
                self.user.debt += self.amount if self.amount else Decimal('0.00')
            elif self.type == 'payment':
                self.user.debt -= self.amount if self.amount else Decimal('0.00')
            self.user.save()

        # Update products_count for all users based on current transaction items
        if self.user:
            self._update_user_products_count()

    def _update_user_products_count(self, exclude_self=False):
        """Helper method to recalculate user's product count."""
        base_query = TransactionItem.objects.filter(transaction__user=self.user)
        
        if exclude_self:
            base_query = base_query.exclude(transaction=self)
        
        total_products = base_query.filter(
            transaction__type='take'
        ).aggregate(total=Sum('quantity'))['total'] or 0
        
        restored_products = base_query.filter(
            transaction__type='restore'
        ).aggregate(total=Sum('quantity'))['total'] or 0
        
        self.user.products_count = total_products - restored_products
        self.user.save()

    def delete(self, *args, **kwargs):
        """Reverse stock and debt changes when deleting a transaction."""
        # Reverse stock changes for all items in this transaction
        for item in self.items.all():
            if item.product:
                if self.type == 'take':
                    item.product.stock += item.quantity
                elif self.type == 'restore':
                    item.product.stock -= item.quantity
                item.product.save()

        # Reverse debt changes for merchants
        if self.user and self.user.user_type == 'merchant':
            if self.type == 'take':
                self.user.debt -= self.amount if self.amount else Decimal('0.00')
            elif self.type == 'payment':
                self.user.debt += self.amount if self.amount else Decimal('0.00')
            self.user.save()

        # Update products_count after deletion
        if self.user:
            self._update_user_products_count(exclude_self=True)

        super().delete(*args, **kwargs)

    class Meta:
        verbose_name = "معاملة"
        verbose_name_plural = "معاملات"


class TransactionItem(models.Model):
    """Individual item within a transaction."""
    
    transaction = models.ForeignKey(
        Transaction,
        on_delete=models.CASCADE,
        related_name='items'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        related_name='transaction_items'
    )
    quantity = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        old_quantity = 0

        if not is_new:
            try:
                old_item = TransactionItem.objects.get(pk=self.pk)
                old_quantity = old_item.quantity
            except TransactionItem.DoesNotExist:
                is_new = True

        # Auto-calculate price and total
        if self.product:
            self.price = self.product.price
            self.total = Decimal(self.price) * Decimal(self.quantity)

            # Only adjust stock if quantity changed
            quantity_diff = self.quantity - old_quantity
            if quantity_diff != 0:
                if self.transaction.type == 'take':
                    self.product.stock -= quantity_diff
                elif self.transaction.type == 'restore':
                    self.product.stock += quantity_diff
                self.product.save()

        super().save(*args, **kwargs)

        # Update parent transaction totals
        if self.transaction:
            self.transaction.update_totals()

    def delete(self, *args, **kwargs):
        """Reverse stock changes when deleting an item."""
        if self.product:
            if self.transaction.type == 'take':
                self.product.stock += self.quantity
            elif self.transaction.type == 'restore':
                self.product.stock -= self.quantity
            self.product.save()

        transaction = self.transaction
        super().delete(*args, **kwargs)

        # Update parent transaction totals after deletion
        if transaction:
            transaction.update_totals()

    def __str__(self):
        return self.product.name if self.product else "Unknown Product"

    class Meta:
        verbose_name = "عنصر معاملة"
        verbose_name_plural = "عناصر معاملات"