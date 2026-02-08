"""
Root URL Configuration for inventory-pos project.

This file serves as BOTH the project root URL config AND the inventory app URLs.
The inventory app patterns are defined here since the app shares the project config directory.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

# Import inventory views for direct use
from . import views as inventory_views


def home_redirect(request):
    """Redirect home to login or appropriate dashboard."""
    if request.user.is_authenticated:
        from accounts.views import redirect_by_role
        return redirect_by_role(request.user)
    return redirect('accounts:login')


# Inventory app URL patterns (for namespacing)
inventory_patterns = [
    # Accountant Dashboard
    path('', inventory_views.dashboard, name='dashboard'),
    
    # Categories
    path('categories/', inventory_views.categories_view, name='categories'),
    path('categories/add/', inventory_views.add_category, name='add_category'),
    path('categories/<int:category_id>/edit/', inventory_views.edit_category, name='edit_category'),
    path('categories/<int:category_id>/delete/', inventory_views.delete_category, name='delete_category'),
    
    # Products
    path('products/', inventory_views.products_view, name='products'),
    path('products/add/', inventory_views.add_product, name='add_product'),
    path('products/<int:product_id>/edit/', inventory_views.edit_product, name='edit_product'),
    path('products/<int:product_id>/delete/', inventory_views.delete_product, name='delete_product'),
    
    # Transactions
    path('transactions/', inventory_views.transactions_view, name='transactions'),
    path('transactions/<int:transaction_id>/approve/', inventory_views.approve_transaction, name='approve_transaction'),
    path('transactions/<int:transaction_id>/reject/', inventory_views.reject_transaction, name='reject_transaction'),
    
    # Representatives (viewed by accountant)
    path('representatives/', inventory_views.representatives_view, name='representatives'),
    path('representatives/<int:rep_id>/', inventory_views.representative_detail, name='representative_detail'),
    
    # Representative Portal
    path('rep/', inventory_views.rep_dashboard, name='rep_dashboard'),
    path('rep/transactions/', inventory_views.rep_transactions, name='rep_transactions'),
    path('rep/request/', inventory_views.rep_request, name='rep_request'),
]


urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Home redirect
    path('', home_redirect, name='home'),
    
    # App URLs
    path('accounts/', include('accounts.urls')),
    path('inventory/', include((inventory_patterns, 'inventory'), namespace='inventory')),
    path('pos/', include('pos.urls')),
    # path('reports/', include('reports.urls')),  # TODO: Add reports
    
    # Legacy base app (to be removed after migration)
    path('legacy/', include('base.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
