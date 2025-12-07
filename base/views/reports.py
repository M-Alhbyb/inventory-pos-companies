"""Report generation views."""

from datetime import datetime
from decimal import Decimal

from django.shortcuts import render, get_object_or_404
from django.db.models import Sum, Count, Q
from django.db.models.functions import TruncDate
from django.utils import timezone

from base.models import Transaction, TransactionItem, Product, User, Category
from base.constants import FirstDayOfMonth


def reports_view(request):
    """Display comprehensive reports with date filtering."""
    # Parse date range
    end_date = timezone.now()
    start_date = end_date.replace(day=FirstDayOfMonth.get())
    
    if request.GET.get('start_date'):
        start_date = datetime.strptime(request.GET.get('start_date'), '%Y-%m-%d')
        start_date = timezone.make_aware(start_date)
    if request.GET.get('end_date'):
        end_date = datetime.strptime(request.GET.get('end_date'), '%Y-%m-%d')
        end_date = timezone.make_aware(end_date)
    
    # Date filter for transactions
    date_filter = {'date__gte': start_date, 'date__lte': end_date}
    
    # Calculate totals
    def get_transaction_total(trans_type):
        return Transaction.objects.filter(
            type=trans_type, **date_filter
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    
    total_sales = get_transaction_total('take')
    total_payments = get_transaction_total('payment')
    total_fees = get_transaction_total('fees')
    total_restores = get_transaction_total('restore')
    
    # Net profit calculation (payments - fees)
    net_profit = total_payments - total_fees
    
    # Outstanding debt
    total_debt = User.objects.filter(
        user_type='merchant'
    ).aggregate(total=Sum('debt'))['total'] or Decimal('0.00')
    
    # Transaction counts
    transaction_counts = {
        trans_type: Transaction.objects.filter(type=trans_type, **date_filter).count()
        for trans_type in ['take', 'payment', 'restore', 'fees']
    }
    
    # Top merchants by sales
    top_merchants = User.objects.filter(
        user_type='merchant',
        transactions__type='take',
        transactions__date__gte=start_date,
        transactions__date__lte=end_date
    ).annotate(
        total_sales=Sum('transactions__amount')
    ).order_by('-total_sales')[:5]
    
    # Top products by quantity sold
    top_products = Product.objects.filter(
        transaction_items__transaction__type='take',
        transaction_items__transaction__date__gte=start_date,
        transaction_items__transaction__date__lte=end_date
    ).annotate(
        total_quantity=Sum('transaction_items__quantity'),
        total_revenue=Sum('transaction_items__total')
    ).order_by('-total_quantity')[:10]
    
    # Daily transaction trends
    daily_trends = Transaction.objects.filter(
        **date_filter
    ).annotate(
        day=TruncDate('date')
    ).values('day', 'type').annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('day')
    
    # Category performance
    category_performance = Category.objects.annotate(
        total_sales=Sum(
            'product__transaction_items__total',
            filter=Q(
                product__transaction_items__transaction__type='take',
                product__transaction_items__transaction__date__gte=start_date,
                product__transaction_items__transaction__date__lte=end_date
            )
        ),
        total_quantity=Sum(
            'product__transaction_items__quantity',
            filter=Q(
                product__transaction_items__transaction__type='take',
                product__transaction_items__transaction__date__gte=start_date,
                product__transaction_items__transaction__date__lte=end_date
            )
        )
    ).filter(total_sales__isnull=False).order_by('-total_sales')
    
    # Low stock products
    low_stock_products = Product.objects.filter(stock__lte=10).order_by('stock')[:10]
    
    # Representative performance
    top_representatives = User.objects.filter(
        user_type='representative',
        transactions__type='take',
        transactions__date__gte=start_date,
        transactions__date__lte=end_date
    ).annotate(
        total_products=Sum('transactions__items__quantity')
    ).order_by('-total_products')[:5]
    
    return render(request, 'reports.html', {
        'start_date': start_date,
        'end_date': end_date,
        'total_sales': total_sales,
        'total_payments': total_payments,
        'total_fees': total_fees,
        'total_restores': total_restores,
        'net_profit': net_profit,
        'total_debt': total_debt,
        'transaction_counts': transaction_counts,
        'top_merchants': top_merchants,
        'top_products': top_products,
        'daily_trends': daily_trends,
        'category_performance': category_performance,
        'low_stock_products': low_stock_products,
        'top_representatives': top_representatives,
    })


def merchant_report(request, merchant_id):
    """Detailed report for a specific merchant."""
    merchant = get_object_or_404(User, id=merchant_id, user_type='merchant')
    
    # Get all transactions for this merchant
    transactions = Transaction.objects.filter(user=merchant).order_by('-date')
    
    # Calculate totals
    total_taken = transactions.filter(type='take').aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    total_paid = transactions.filter(type='payment').aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    
    # Products taken by merchant
    products_taken = TransactionItem.objects.filter(
        transaction__user=merchant,
        transaction__type='take'
    ).values('product__name').annotate(
        total_quantity=Sum('quantity'),
        total_amount=Sum('total')
    ).order_by('-total_quantity')
    
    return render(request, 'merchant_report.html', {
        'merchant': merchant,
        'transactions': transactions,
        'total_taken': total_taken,
        'total_paid': total_paid,
        'current_debt': merchant.debt,
        'products_taken': products_taken,
    })


def product_report(request, product_id):
    """Detailed report for a specific product."""
    product = get_object_or_404(Product, id=product_id)
    
    # Transaction history for this product
    transaction_items = TransactionItem.objects.filter(
        product=product
    ).select_related('transaction', 'transaction__user').order_by('-transaction__date')
    
    # Calculate totals
    total_taken = transaction_items.filter(
        transaction__type='take'
    ).aggregate(total=Sum('quantity'))['total'] or 0
    
    total_restored = transaction_items.filter(
        transaction__type='restore'
    ).aggregate(total=Sum('quantity'))['total'] or 0
    
    total_revenue = transaction_items.filter(
        transaction__type='take'
    ).aggregate(total=Sum('total'))['total'] or Decimal('0.00')
    
    # Top customers for this product
    top_customers = User.objects.filter(
        transactions__items__product=product,
        transactions__type='take'
    ).annotate(
        total_quantity=Sum('transactions__items__quantity')
    ).order_by('-total_quantity')[:5]
    
    return render(request, 'product_report.html', {
        'product': product,
        'transaction_items': transaction_items,
        'total_taken': total_taken,
        'total_restored': total_restored,
        'total_revenue': total_revenue,
        'top_customers': top_customers,
    })
