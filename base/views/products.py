"""Product management views."""

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required

from base.models import Product
from base.forms import ProductForm

ITEMS_PER_PAGE = 10

@login_required
def products_view(request):
    """Display all products with search and pagination."""
    products = Product.objects.select_related('category').all()
    
    # Handle search
    q = request.GET.get('q')
    if q:
        products = products.filter(name__icontains=q)
    
    # Pagination
    paginator = Paginator(products, ITEMS_PER_PAGE)
    page = request.GET.get('page', 1)
    page_obj = paginator.get_page(page)
    
    # Handle AJAX requests for infinite scroll
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return get_products_json(page_obj)
    
    return render(request, 'products.html', {
        'products': products,
        'form': ProductForm(),
        'page_obj': page_obj
    })


def get_products_json(page_obj):
    """Return paginated products as JSON for infinite scroll."""
    data = []
    for product in page_obj:
        data.append({
            'id': product.id,
            'name': product.name,
            'category_id': product.category.id if product.category else None,
            'category_name': product.category.name if product.category else '-',
            'price': str(product.price) if product.price else '0',
            'stock': product.stock,
        })
    
    return JsonResponse({
        'success': True,
        'data': data,
        'has_next': page_obj.has_next(),
        'next_page_number': page_obj.next_page_number() if page_obj.has_next() else None,
    })

@login_required
@require_http_methods(["POST"])
def add_product(request):
    """Handle adding a new product."""
    try:
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم إضافة المنتج بنجاح')
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'error': form.errors})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
@require_http_methods(["POST", "GET"])
def edit_product(request, product_id):
    """Handle editing an existing product."""
    try:
        product = get_object_or_404(Product, id=product_id)
        
        if request.method == "GET":
            return JsonResponse({
                'success': True,
                'name': product.name,
                'category': product.category.id,
                'price': str(product.price),
                'stock': product.stock
            })
        
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تعديل المنتج بنجاح')
            return JsonResponse({'success': True})
        else:
            messages.error(request, 'حدث خطأ أثناء تعديل المنتج')
            return JsonResponse({'success': False, 'error': form.errors})
        
    except Exception as e:
        messages.error(request, f'حدث خطأ أثناء تعديل المنتج {e}')
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
@require_http_methods(["POST"])
def delete_product(request, product_id):
    """Handle deleting a product."""
    try:
        product = get_object_or_404(Product, id=product_id)
        product.delete()
        messages.success(request, 'تم حذف المنتج بنجاح')
        return JsonResponse({'success': True})
    except Exception as e:
        messages.error(request, f'حدث خطأ أثناء حذف المنتج {e}')
        return JsonResponse({'success': False, 'error': str(e)})
