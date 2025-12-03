from django.urls import path
from .views import general, categories, products, inventory, partners, transactions
from .models import Category
app_name = 'base'

urlpatterns = [
    path('', general.dashboard, name='dashboard'),
    # categories
    path('categories/', categories.categories_view, name='categories'),
    path('categories/add/', categories.add_category, name='add_category'),
    path('categories/edit/<int:category_id>/', categories.edit_category, name='edit_category'),
    path('categories/delete/<int:category_id>/', categories.delete_category, name='delete_category'),

    # products
    path('products/', products.products_view, name='products'),
    path('products/add/', products.add_product, name='add_product'),
    path('products/edit/<int:product_id>/', products.edit_product, name='edit_product'),
    path('products/delete/<int:product_id>/', products.delete_product, name='delete_product'),

    # inventory
    path('inventory/', inventory.inventory_view, name='inventory'),

    # transactions
    path('transactions/', transactions.transactions_view, name='transactions'),

    # partners
    path('partners/<str:partner_type>', partners.partners_view, name='partners'),
    path('partners/add/<str:partner_type>', partners.add_partner, name='add_partner'),
    path('partners/edit/<int:partner_id>/', partners.edit_partner, name='edit_partner'),
    path('partners/delete/<int:partner_id>/', partners.delete_partner, name='delete_partner'),
    path('partners/<int:partner_id>/', partners.partner_detail, name='partner_detail'),
    path('partners/<int:partner_id>/transaction/<int:transaction_id>/delete/', partners.delete_transaction, name='partner_delete_transaction'),

    # merchants
    path('merchants/', partners.partners_view, {'partner_type': 'merchant'}, name='merchants'),
    path('merchants/add/', partners.add_partner, {'partner_type': 'merchant'}, name='add_merchant'),
    path('merchants/edit/<int:partner_id>/', partners.edit_partner, name='edit_merchant'),
    path('merchants/delete/<int:partner_id>/', partners.delete_partner, name='delete_merchant'),
    path('merchants/<int:partner_id>/', partners.partner_detail, name='merchant_detail'),
    path('merchants/<int:partner_id>/transaction/<int:transaction_id>/delete/', partners.delete_transaction, name='merchant_delete_transaction'),

    # representatives
    path('representatives/', partners.partners_view, {'partner_type': 'representative'}, name='representatives'),
    path('representatives/add/', partners.add_partner, {'partner_type': 'representative'}, name='add_representative'),
    path('representatives/edit/<int:partner_id>/', partners.edit_partner, name='edit_representative'),
    path('representatives/delete/<int:partner_id>/', partners.delete_partner, name='delete_representative'),
    path('representatives/<int:partner_id>/', partners.partner_detail, name='representative_detail'),
    path('representatives/<int:partner_id>/transaction/<int:transaction_id>/delete/', partners.delete_transaction, name='representative_delete_transaction'),
]
