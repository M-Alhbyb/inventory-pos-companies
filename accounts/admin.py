from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import SubscriptionPlan, Company, CompanySubscription, User


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'max_users', 'max_products', 'has_inventory', 'has_pos', 'price_monthly', 'trial_days', 'is_active']
    list_filter = ['is_active', 'has_inventory', 'has_pos']
    search_fields = ['name']


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone', 'is_active', 'user_count', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name', 'email']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(CompanySubscription)
class CompanySubscriptionAdmin(admin.ModelAdmin):
    list_display = ['company', 'plan', 'status', 'start_date', 'end_date', 'trial_end_date', 'payment_verified']
    list_filter = ['status', 'payment_verified', 'plan']
    search_fields = ['company__name']
    actions = ['approve_subscriptions']
    
    @admin.action(description='Approve selected subscriptions')
    def approve_subscriptions(self, request, queryset):
        for sub in queryset.filter(status='pending'):
            sub.approve()


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'company', 'role', 'is_active']
    list_filter = ['role', 'company', 'is_active']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('معلومات إضافية', {
            'fields': ('company', 'role', 'phone', 'products_count')
        }),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('معلومات إضافية', {
            'fields': ('company', 'role', 'phone')
        }),
    )
