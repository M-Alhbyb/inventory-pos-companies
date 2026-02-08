"""Inventory management view."""

from django.shortcuts import render
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required

from base.models import Product

ITEMS_PER_PAGE = 10

@login_required
def inventory_view(request):
    """Display inventory with search and sorting options."""
    products = Product.objects.select_related('category').all()
    
    # Handle search
    q = request.GET.get('q')
    if q:
        products = products.filter(name__icontains=q)
    
    # Handle sorting
    sort_by = request.GET.get('sort_by')
    if sort_by:
        products = products.order_by(sort_by)
    
    # Pagination
    paginator = Paginator(products, ITEMS_PER_PAGE)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # Handle AJAX requests for infinite scroll
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return get_inventory_json(page_obj)
    
    return render(request, 'inventory.html', {
        'products': products,
        'page_obj': page_obj
    })


def get_inventory_json(page_obj):
    """Return paginated inventory as JSON for infinite scroll."""
    data = []
    for product in page_obj:
        data.append({
            'id': product.id,
            'name': product.name,
            'category_name': product.category.name if product.category else '-',
            'price': str(product.price) if product.price else '0',
            'stock': product.stock,
            'estimated_stock_out': product.estimated_stock_out.isoformat() if product.estimated_stock_out else None,
        })
    
    return JsonResponse({
        'success': True,
        'data': data,
        'has_next': page_obj.has_next(),
        'next_page_number': page_obj.next_page_number() if page_obj.has_next() else None,
    })
