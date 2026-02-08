from django.contrib import admin
from .models import User, Product, Category, Transaction, TransactionItem


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin configuration for Category model."""
    
    list_display = ('name', 'created_at', 'updated_at')
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Admin configuration for Product model."""
    
    list_display = ('name', 'category', 'price', 'stock', 'created_at')
    list_filter = ('category',)
    search_fields = ('name', 'description')
    ordering = ('name',)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Admin configuration for User model."""
    
    list_display = ('username', 'user_type', 'first_name', 'last_name', 'phone', 'products_count')
    list_filter = ('user_type',)
    search_fields = ('username', 'first_name', 'last_name', 'phone')
    ordering = ('username',)


class TransactionItemInline(admin.TabularInline):
    """Inline admin for TransactionItems within Transaction."""
    
    model = TransactionItem
    extra = 0
    readonly_fields = ('price', 'total')


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    """Admin configuration for Transaction model."""
    
    list_display = ('id', 'user', 'type', 'amount', 'date')
    list_filter = ('type', 'user__user_type', 'date')
    search_fields = ('user__username', 'user__first_name', 'user__last_name')
    ordering = ('-date',)
    inlines = [TransactionItemInline]


@admin.register(TransactionItem)
class TransactionItemAdmin(admin.ModelAdmin):
    """Admin configuration for TransactionItem model."""
    
    list_display = ('id', 'transaction', 'product', 'quantity', 'price', 'total')
    list_filter = ('transaction__type',)
    search_fields = ('product__name',)
    ordering = ('-transaction__date',)
