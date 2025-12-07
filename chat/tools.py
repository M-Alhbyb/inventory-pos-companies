"""Tools for Gemini AI to interact with the inventory system."""

import json
from datetime import datetime, timedelta
from decimal import Decimal
from django.db.models import Sum, Count, Avg, F, Q
from django.db.models.functions import TruncDate, TruncMonth
from django.utils import timezone

from base.models import Category, Product, User, Transaction, TransactionItem, TRANSACTION_TYPES


# ==================== Basic Data Getters ====================

def get_categories():
    """الحصول على قائمة جميع الفئات مع عدد المنتجات في كل فئة."""
    categories = Category.objects.annotate(
        products_count=Count('product')
    ).all()
    return json.dumps([{
        'id': c.id, 
        'name': c.name,
        'description': c.description,
        'products_count': c.products_count,
        'created_at': c.created_at.isoformat() if c.created_at else None
    } for c in categories], ensure_ascii=False)


def get_products():
    """الحصول على قائمة جميع المنتجات مع تفاصيلها الكاملة."""
    products = Product.objects.select_related('category').all()
    return json.dumps([{
        'id': p.id, 
        'name': p.name,
        'description': p.description,
        'category': p.category.name if p.category else None,
        'category_id': p.category.id if p.category else None,
        'price': str(p.price),
        'stock': p.stock,
        'estimated_stock_out': p.estimated_stock_out.strftime('%Y-%m-%d') if p.estimated_stock_out else None,
        'days_until_stock_out': p.days_until_stock_out,
        'is_low_stock': p.stock <= 10,
        'is_out_of_stock': p.stock == 0,
        'created_at': p.created_at.isoformat() if p.created_at else None
    } for p in products], ensure_ascii=False)


def get_users():
    """الحصول على قائمة جميع المستخدمين (التجار والمندوبين) مع بياناتهم الكاملة."""
    users = User.objects.exclude(user_type='admin').annotate(
        transactions_count=Count('transactions')
    )
    return json.dumps([{
        'id': u.id, 
        'username': u.username,
        'full_name': f"{u.first_name} {u.last_name}".strip() or u.username,
        'first_name': u.first_name,
        'last_name': u.last_name,
        'phone': u.phone,
        'address': u.address,
        'user_type': u.user_type,
        'user_type_display': 'تاجر' if u.user_type == 'merchant' else 'مندوب',
        'debt': str(u.debt),
        'products_count': u.products_count,
        'transactions_count': u.transactions_count,
        'has_debt': u.debt > 0,
        'created_at': u.created_at.isoformat() if u.created_at else None
    } for u in users], ensure_ascii=False)


def get_merchants():
    """الحصول على قائمة التجار فقط مع ديونهم ومعاملاتهم."""
    merchants = User.objects.filter(user_type='merchant').annotate(
        transactions_count=Count('transactions'),
        total_takes=Count('transactions', filter=Q(transactions__type='take')),
        total_payments=Count('transactions', filter=Q(transactions__type='payment'))
    )
    return json.dumps([{
        'id': m.id,
        'username': m.username,
        'full_name': f"{m.first_name} {m.last_name}".strip() or m.username,
        'phone': m.phone,
        'address': m.address,
        'debt': str(m.debt),
        'products_count': m.products_count,
        'transactions_count': m.transactions_count,
        'total_takes': m.total_takes,
        'total_payments': m.total_payments,
        'has_debt': m.debt > 0
    } for m in merchants], ensure_ascii=False)


def get_representatives():
    """الحصول على قائمة المندوبين فقط مع إحصائياتهم."""
    reps = User.objects.filter(user_type='representative').annotate(
        transactions_count=Count('transactions'),
        total_takes=Count('transactions', filter=Q(transactions__type='take')),
        total_restores=Count('transactions', filter=Q(transactions__type='restore'))
    )
    return json.dumps([{
        'id': r.id,
        'username': r.username,
        'full_name': f"{r.first_name} {r.last_name}".strip() or r.username,
        'phone': r.phone,
        'address': r.address,
        'products_count': r.products_count,
        'transactions_count': r.transactions_count,
        'total_takes': r.total_takes,
        'total_restores': r.total_restores
    } for r in reps], ensure_ascii=False)


def get_transactions():
    """الحصول على المعاملات الأخيرة (آخر 100 معاملة)."""
    transactions = Transaction.objects.select_related('user').prefetch_related('items__product').order_by('-date')[:100]
    return json.dumps([{
        'id': t.id, 
        'type': t.type,
        'type_display': t.get_type_display(),
        'user_id': t.user.id if t.user else None,
        'user': t.user.username if t.user else None,
        'user_type': t.user.user_type if t.user else None,
        'amount': str(t.amount) if t.amount else '0',
        'items_count': t.items.count(),
        'items': [{'product': item.product.name if item.product else None, 'quantity': item.quantity, 'total': str(item.total)} for item in t.items.all()[:5]],
        'date': t.date.strftime('%Y-%m-%d %H:%M') if t.date else None
    } for t in transactions], ensure_ascii=False)


def get_transaction_items():
    """الحصول على تفاصيل عناصر المعاملات (آخر 200 عنصر)."""
    items = TransactionItem.objects.select_related('transaction', 'transaction__user', 'product').order_by('-transaction__date')[:200]
    return json.dumps([{
        'id': ti.id, 
        'transaction_id': ti.transaction_id,
        'transaction_type': ti.transaction.type if ti.transaction else None,
        'transaction_type_display': ti.transaction.get_type_display() if ti.transaction else None,
        'user': ti.transaction.user.username if ti.transaction and ti.transaction.user else None,
        'product_id': ti.product.id if ti.product else None,
        'product': ti.product.name if ti.product else None,
        'product_category': ti.product.category.name if ti.product and ti.product.category else None,
        'quantity': ti.quantity,
        'price': str(ti.price) if ti.price else '0',
        'total': str(ti.total) if ti.total else '0',
        'date': ti.transaction.date.strftime('%Y-%m-%d') if ti.transaction and ti.transaction.date else None
    } for ti in items], ensure_ascii=False)


def get_transaction_types():
    """الحصول على أنواع المعاملات المتاحة في النظام."""
    return json.dumps([{'code': code, 'name': name} for code, name in TRANSACTION_TYPES], ensure_ascii=False)


# ==================== Statistics & Analytics ====================

def get_inventory_stats():
    """الحصول على إحصائيات شاملة عن المخزون والنظام."""
    from django.db.models import Sum, Count, Avg
    
    total_stock_value = Product.objects.aggregate(
        total=Sum(F('price') * F('stock'))
    )['total'] or 0
    
    merchants = User.objects.filter(user_type='merchant')
    total_debt = merchants.aggregate(total=Sum('debt'))['total'] or 0
    merchants_with_debt = merchants.filter(debt__gt=0).count()
    
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    stats = {
        # المنتجات
        'total_products': Product.objects.count(),
        'total_categories': Category.objects.count(),
        'total_stock_value': str(total_stock_value),
        'low_stock_products': Product.objects.filter(stock__lte=10, stock__gt=0).count(),
        'out_of_stock_products': Product.objects.filter(stock=0).count(),
        'products_critical_7_days': Product.objects.filter(estimated_stock_out__lte=today + timedelta(days=7), estimated_stock_out__isnull=False).count(),
        
        # المستخدمين
        'total_merchants': merchants.count(),
        'total_representatives': User.objects.filter(user_type='representative').count(),
        'merchants_with_debt': merchants_with_debt,
        'total_debt': str(total_debt),
        
        # المعاملات
        'total_transactions': Transaction.objects.count(),
        'transactions_today': Transaction.objects.filter(date__date=today).count(),
        'transactions_this_week': Transaction.objects.filter(date__date__gte=week_ago).count(),
        'transactions_this_month': Transaction.objects.filter(date__date__gte=month_ago).count(),
        
        # أنواع المعاملات
        'take_transactions_count': Transaction.objects.filter(type='take').count(),
        'payment_transactions_count': Transaction.objects.filter(type='payment').count(),
        'restore_transactions_count': Transaction.objects.filter(type='restore').count(),
        'fees_transactions_count': Transaction.objects.filter(type='fees').count(),
    }
    return json.dumps(stats, ensure_ascii=False)


def get_daily_transactions_summary():
    """الحصول على ملخص المعاملات اليومية لآخر 30 يوم."""
    thirty_days_ago = timezone.now() - timedelta(days=30)
    
    daily_data = Transaction.objects.filter(
        date__gte=thirty_days_ago
    ).annotate(
        day=TruncDate('date')
    ).values('day').annotate(
        total_transactions=Count('id'),
        total_amount=Sum('amount'),
        take_count=Count('id', filter=Q(type='take')),
        payment_count=Count('id', filter=Q(type='payment')),
        restore_count=Count('id', filter=Q(type='restore'))
    ).order_by('-day')
    
    return json.dumps([{
        'date': d['day'].strftime('%Y-%m-%d'),
        'total_transactions': d['total_transactions'],
        'total_amount': str(d['total_amount']) if d['total_amount'] else '0',
        'take_count': d['take_count'],
        'payment_count': d['payment_count'],
        'restore_count': d['restore_count']
    } for d in daily_data], ensure_ascii=False)


def get_top_products_by_sales():
    """الحصول على أكثر المنتجات مبيعاً (سحباً من المخزون)."""
    top_products = TransactionItem.objects.filter(
        transaction__type='take'
    ).values(
        'product__id', 'product__name', 'product__category__name'
    ).annotate(
        total_quantity=Sum('quantity'),
        total_revenue=Sum('total'),
        transactions_count=Count('transaction', distinct=True)
    ).order_by('-total_quantity')[:20]
    
    return json.dumps([{
        'product_id': p['product__id'],
        'product_name': p['product__name'],
        'category': p['product__category__name'],
        'total_quantity_sold': p['total_quantity'],
        'total_revenue': str(p['total_revenue']) if p['total_revenue'] else '0',
        'transactions_count': p['transactions_count']
    } for p in top_products], ensure_ascii=False)


def get_top_merchants_by_debt():
    """الحصول على التجار الأكثر ديوناً."""
    merchants = User.objects.filter(
        user_type='merchant',
        debt__gt=0
    ).order_by('-debt')[:20]
    
    return json.dumps([{
        'id': m.id,
        'username': m.username,
        'full_name': f"{m.first_name} {m.last_name}".strip() or m.username,
        'phone': m.phone,
        'debt': str(m.debt),
        'products_count': m.products_count
    } for m in merchants], ensure_ascii=False)


def get_top_merchants_by_transactions():
    """الحصول على التجار الأكثر نشاطاً في المعاملات."""
    merchants = User.objects.filter(
        user_type='merchant'
    ).annotate(
        transactions_count=Count('transactions'),
        total_amount=Sum('transactions__amount')
    ).order_by('-transactions_count')[:20]
    
    return json.dumps([{
        'id': m.id,
        'username': m.username,
        'full_name': f"{m.first_name} {m.last_name}".strip() or m.username,
        'transactions_count': m.transactions_count,
        'total_amount': str(m.total_amount) if m.total_amount else '0',
        'debt': str(m.debt)
    } for m in merchants], ensure_ascii=False)


def get_low_stock_alert():
    """الحصول على تنبيهات المخزون المنخفض والمنتجات المنفذة."""
    low_stock = Product.objects.filter(stock__lte=10).order_by('stock')
    
    return json.dumps([{
        'id': p.id,
        'name': p.name,
        'category': p.category.name if p.category else None,
        'stock': p.stock,
        'price': str(p.price),
        'status': 'نفذ' if p.stock == 0 else 'منخفض',
        'estimated_stock_out': p.estimated_stock_out.strftime('%Y-%m-%d') if p.estimated_stock_out else None,
        'days_until_stock_out': p.days_until_stock_out
    } for p in low_stock], ensure_ascii=False)


def get_stock_predictions():
    """الحصول على توقعات نفاذ المخزون للمنتجات."""
    products = Product.objects.filter(
        estimated_stock_out__isnull=False
    ).order_by('estimated_stock_out')[:30]
    
    return json.dumps([{
        'id': p.id,
        'name': p.name,
        'category': p.category.name if p.category else None,
        'stock': p.stock,
        'estimated_stock_out': p.estimated_stock_out.strftime('%Y-%m-%d'),
        'days_until_stock_out': p.days_until_stock_out,
        'urgency': 'حرج' if p.days_until_stock_out and p.days_until_stock_out < 7 else ('متوسط' if p.days_until_stock_out and p.days_until_stock_out < 30 else 'عادي')
    } for p in products], ensure_ascii=False)


def get_products_by_category():
    """الحصول على المنتجات مصنفة حسب الفئة."""
    categories = Category.objects.prefetch_related('product_set').all()
    
    result = []
    for category in categories:
        products = category.product_set.all()
        result.append({
            'category_id': category.id,
            'category_name': category.name,
            'products_count': products.count(),
            'total_stock': sum(p.stock for p in products),
            'total_value': str(sum(p.stock * p.price for p in products)),
            'products': [{
                'id': p.id,
                'name': p.name,
                'price': str(p.price),
                'stock': p.stock
            } for p in products[:10]]  # Limit to 10 products per category
        })
    
    return json.dumps(result, ensure_ascii=False)


def get_monthly_revenue():
    """الحصول على الإيرادات الشهرية (من معاملات الأخذ)."""
    six_months_ago = timezone.now() - timedelta(days=180)
    
    monthly_data = Transaction.objects.filter(
        type='take',
        date__gte=six_months_ago
    ).annotate(
        month=TruncMonth('date')
    ).values('month').annotate(
        total_revenue=Sum('amount'),
        transactions_count=Count('id')
    ).order_by('-month')
    
    return json.dumps([{
        'month': d['month'].strftime('%Y-%m'),
        'month_name': d['month'].strftime('%B %Y'),
        'total_revenue': str(d['total_revenue']) if d['total_revenue'] else '0',
        'transactions_count': d['transactions_count']
    } for d in monthly_data], ensure_ascii=False)


def get_monthly_payments():
    """الحصول على المدفوعات الشهرية من التجار."""
    six_months_ago = timezone.now() - timedelta(days=180)
    
    monthly_data = Transaction.objects.filter(
        type='payment',
        date__gte=six_months_ago
    ).annotate(
        month=TruncMonth('date')
    ).values('month').annotate(
        total_payments=Sum('amount'),
        transactions_count=Count('id')
    ).order_by('-month')
    
    return json.dumps([{
        'month': d['month'].strftime('%Y-%m'),
        'month_name': d['month'].strftime('%B %Y'),
        'total_payments': str(d['total_payments']) if d['total_payments'] else '0',
        'transactions_count': d['transactions_count']
    } for d in monthly_data], ensure_ascii=False)


def get_user_transactions(user_id: int = None):
    """الحصول على معاملات مستخدم محدد. إذا لم يتم تحديد المستخدم، يتم إرجاع رسالة خطأ."""
    if not user_id:
        return json.dumps({'error': 'يجب تحديد معرف المستخدم'}, ensure_ascii=False)
    
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return json.dumps({'error': f'لم يتم العثور على مستخدم بالمعرف {user_id}'}, ensure_ascii=False)
    
    transactions = Transaction.objects.filter(user=user).prefetch_related('items__product').order_by('-date')[:50]
    
    return json.dumps({
        'user_id': user.id,
        'username': user.username,
        'full_name': f"{user.first_name} {user.last_name}".strip() or user.username,
        'user_type': user.user_type,
        'debt': str(user.debt),
        'products_count': user.products_count,
        'transactions': [{
            'id': t.id,
            'type': t.get_type_display(),
            'amount': str(t.amount) if t.amount else '0',
            'items_count': t.items.count(),
            'date': t.date.strftime('%Y-%m-%d %H:%M') if t.date else None
        } for t in transactions]
    }, ensure_ascii=False)


def get_product_transactions(product_id: int = None):
    """الحصول على معاملات منتج محدد. إذا لم يتم تحديد المنتج، يتم إرجاع رسالة خطأ."""
    if not product_id:
        return json.dumps({'error': 'يجب تحديد معرف المنتج'}, ensure_ascii=False)
    
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return json.dumps({'error': f'لم يتم العثور على منتج بالمعرف {product_id}'}, ensure_ascii=False)
    
    items = TransactionItem.objects.filter(product=product).select_related('transaction', 'transaction__user').order_by('-transaction__date')[:50]
    
    return json.dumps({
        'product_id': product.id,
        'product_name': product.name,
        'category': product.category.name if product.category else None,
        'price': str(product.price),
        'stock': product.stock,
        'transactions': [{
            'transaction_id': item.transaction.id,
            'type': item.transaction.get_type_display(),
            'user': item.transaction.user.username if item.transaction.user else None,
            'quantity': item.quantity,
            'total': str(item.total) if item.total else '0',
            'date': item.transaction.date.strftime('%Y-%m-%d') if item.transaction.date else None
        } for item in items]
    }, ensure_ascii=False)


def get_today_summary():
    """الحصول على ملخص اليوم (المعاملات والإحصائيات)."""
    today = timezone.now().date()
    
    today_transactions = Transaction.objects.filter(date__date=today)
    
    summary = {
        'date': today.strftime('%Y-%m-%d'),
        'date_arabic': today.strftime('%d/%m/%Y'),
        'total_transactions': today_transactions.count(),
        'take_transactions': {
            'count': today_transactions.filter(type='take').count(),
            'total_amount': str(today_transactions.filter(type='take').aggregate(total=Sum('amount'))['total'] or 0)
        },
        'payment_transactions': {
            'count': today_transactions.filter(type='payment').count(),
            'total_amount': str(today_transactions.filter(type='payment').aggregate(total=Sum('amount'))['total'] or 0)
        },
        'restore_transactions': {
            'count': today_transactions.filter(type='restore').count(),
            'total_amount': str(today_transactions.filter(type='restore').aggregate(total=Sum('amount'))['total'] or 0)
        },
        'fees_transactions': {
            'count': today_transactions.filter(type='fees').count(),
            'total_amount': str(today_transactions.filter(type='fees').aggregate(total=Sum('amount'))['total'] or 0)
        }
    }
    
    return json.dumps(summary, ensure_ascii=False)


def search_products(query: str = None):
    """البحث في المنتجات حسب الاسم أو الوصف."""
    if not query:
        return json.dumps({'error': 'يجب تحديد نص البحث'}, ensure_ascii=False)
    
    products = Product.objects.filter(
        Q(name__icontains=query) | Q(description__icontains=query)
    ).select_related('category')[:20]
    
    return json.dumps([{
        'id': p.id,
        'name': p.name,
        'category': p.category.name if p.category else None,
        'price': str(p.price),
        'stock': p.stock
    } for p in products], ensure_ascii=False)


def search_users(query: str = None):
    """البحث في المستخدمين حسب الاسم أو اسم المستخدم أو الهاتف."""
    if not query:
        return json.dumps({'error': 'يجب تحديد نص البحث'}, ensure_ascii=False)
    
    users = User.objects.filter(
        Q(username__icontains=query) |
        Q(first_name__icontains=query) |
        Q(last_name__icontains=query) |
        Q(phone__icontains=query)
    ).exclude(user_type='admin')[:20]
    
    return json.dumps([{
        'id': u.id,
        'username': u.username,
        'full_name': f"{u.first_name} {u.last_name}".strip() or u.username,
        'user_type': u.user_type,
        'phone': u.phone,
        'debt': str(u.debt)
    } for u in users], ensure_ascii=False)
