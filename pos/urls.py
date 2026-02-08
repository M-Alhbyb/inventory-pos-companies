"""URL routing for POS app."""

from django.urls import path
from . import views

app_name = 'pos'

urlpatterns = [
    # Main POS interface
    path('', views.pos_interface, name='interface'),
    path('checkout/', views.process_checkout, name='checkout'),
    path('receipt/<int:sale_id>/', views.print_receipt, name='receipt'),
    
    # Sales history
    path('history/', views.sales_history, name='history'),
    path('daily-summary/', views.daily_summary, name='daily_summary'),
    
    # API endpoints
    path('api/search/', views.search_products, name='search_products'),
    path('api/barcode/', views.get_product_by_barcode, name='get_by_barcode'),
]
