from django.urls import path
from .views import general, categories, products, inventory, partners, transactions, reports, representative

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
    path('transactions/<int:transaction_id>/approve/', transactions.approve_transaction, name='approve_transaction'),
    path('transactions/<int:transaction_id>/reject/', transactions.reject_transaction, name='reject_transaction'),
    
    # Reports
    path('reports/', reports.reports_view, name='reports'),
    path('reports/representative/<int:representative_id>/', reports.representative_report, name='representative_report'),
    path('reports/product/<int:product_id>/', reports.product_report, name='product_report'),

    # Representatives (Accountant view)
    path('representatives/', partners.partners_view, {'partner_type': 'representative'}, name='representatives'),
    path('representatives/<int:partner_id>/', partners.partner_detail, name='representative_detail'),
    path('representatives/<int:partner_id>/transaction/<int:transaction_id>/delete/', partners.delete_transaction, name='representative_delete_transaction'),

    # Representative Portal
    path('rep/', representative.rep_dashboard, name='rep_dashboard'),
    path('rep/transactions/', representative.rep_transactions, name='rep_transactions'),
    path('rep/request/', representative.rep_request_transaction, name='rep_request'),
]
