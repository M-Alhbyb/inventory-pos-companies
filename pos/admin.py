from django.contrib import admin
from .models import Sale, SaleItem


class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 0
    readonly_fields = ['total', 'profit']


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ['receipt_number', 'company', 'cashier', 'total', 'payment_method', 'status', 'created_at']
    list_filter = ['company', 'payment_method', 'status', 'created_at']
    search_fields = ['receipt_number', 'customer_name', 'customer_phone']
    readonly_fields = ['receipt_number', 'created_at', 'updated_at']
    inlines = [SaleItemInline]
    actions = ['refund_sales']
    
    @admin.action(description='Refund selected sales')
    def refund_sales(self, request, queryset):
        for sale in queryset.filter(status='completed'):
            sale.refund()
