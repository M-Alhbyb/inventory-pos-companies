from django.urls import path
from .views import general, categories, products, inventory, partners, transactions, fees, reports, ai

app_name = 'base'

urlpatterns = [
    # Dashboard
    path('', general.dashboard, name='dashboard'),
    
    # Categories
    path('categories/', categories.categories_view, name='categories'),
    path('categories/add/', categories.add_category, name='add_category'),
    path('categories/edit/<int:category_id>/', categories.edit_category, name='edit_category'),
    path('categories/delete/<int:category_id>/', categories.delete_category, name='delete_category'),

    # Products
    path('products/', products.products_view, name='products'),
    path('products/add/', products.add_product, name='add_product'),
    path('products/edit/<int:product_id>/', products.edit_product, name='edit_product'),
    path('products/delete/<int:product_id>/', products.delete_product, name='delete_product'),

    # Inventory
    path('inventory/', inventory.inventory_view, name='inventory'),

    # Transactions
    path('transactions/', transactions.transactions_view, name='transactions'),
    
    # Fees
    path('fees/add/', fees.add_fees, name='add_fees'),
    
    # Reports
    path('reports/', reports.reports_view, name='reports'),
    path('reports/merchant/<int:merchant_id>/', reports.merchant_report, name='merchant_report'),
    path('reports/product/<int:product_id>/', reports.product_report, name='product_report'),

    # Partners (generic routes)
    path('partners/<str:partner_type>/', partners.partners_view, name='partners'),
    path('partners/add/<str:partner_type>/', partners.add_partner, name='add_partner'),
    path('partners/<int:partner_id>/edit/', partners.edit_partner, name='edit_partner'),
    path('partners/<int:partner_id>/delete/', partners.delete_partner, name='delete_partner'),
    path('partners/<int:partner_id>/', partners.partner_detail, name='partner_detail'),
    path('partners/<int:partner_id>/transaction/<int:transaction_id>/delete/', partners.delete_transaction, name='partner_delete_transaction'),

    # Merchants (aliases using partner views)
    path('merchants/', partners.partners_view, {'partner_type': 'merchant'}, name='merchants'),
    path('merchants/add/', partners.add_partner, {'partner_type': 'merchant'}, name='add_merchant'),
    path('merchants/<int:partner_id>/', partners.partner_detail, name='merchant_detail'),

    # Representatives (aliases using partner views)
    path('representatives/', partners.partners_view, {'partner_type': 'representative'}, name='representatives'),
    path('representatives/add/', partners.add_partner, {'partner_type': 'representative'}, name='add_representative'),
    path('representatives/<int:partner_id>/', partners.partner_detail, name='representative_detail'),

    # AI
    path('ai/', ai.ai_view, name='ai'),
    path('ai/refresh/', ai.ai_refresh, name='ai_refresh'),
    path('status/<str:task_id>/', ai.get_process_status, name='get_process_status'),
]
