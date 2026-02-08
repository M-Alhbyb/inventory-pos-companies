from django.contrib import admin
from .models import Category, Product, Transaction, TransactionItem


class TransactionItemInline(admin.TabularInline):
    model = TransactionItem
    extra = 0
    readonly_fields = ['total']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'company', 'created_at']
    list_filter = ['company']
    search_fields = ['name']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'company', 'price', 'cost', 'stock', 'is_low_stock', 'is_active']
    list_filter = ['company', 'category', 'is_active']
    search_fields = ['name', 'sku', 'barcode']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['id', 'company', 'user', 'type', 'status', 'amount', 'date', 'approved_by']
    list_filter = ['company', 'type', 'status']
    search_fields = ['user__username', 'user__first_name']
    readonly_fields = ['date', 'updated_at', 'approved_at']
    inlines = [TransactionItemInline]
    actions = ['approve_transactions', 'reject_transactions']
    
    @admin.action(description='Approve selected transactions')
    def approve_transactions(self, request, queryset):
        for transaction in queryset.filter(status='pending'):
            transaction.approve(request.user)
    
    @admin.action(description='Reject selected transactions')
    def reject_transactions(self, request, queryset):
        for transaction in queryset.filter(status='pending'):
            transaction.reject(request.user)
