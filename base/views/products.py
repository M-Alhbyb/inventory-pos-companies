from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from base.models import Category, Product
from django.contrib import messages
from base.forms import ProductForm

def products_view(request):
    products = Product.objects.all()
    if request.method == 'GET':
        q = request.GET.get('q')
        if q:
            products = products.filter(name__icontains=q)
    form = ProductForm()
    return render(request, 'products.html', {'products': products, 'form': form})

@require_http_methods(["POST"])
def add_product(request):
    """Handle adding a new product"""
    try:
        form = ProductForm(request.POST)
        
        # Validate inputs
        if form.is_valid():
            product = form.save()
            messages.success(request, 'تم إضافة المنتج بنجاح')    
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False})   
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@require_http_methods(["POST", "GET"])
def edit_product(request, product_id):
    """Handle adding a new category"""
    try:
        if request.method == "GET":
            product = Product.objects.get(id=product_id)
            name = product.name
            category = product.category.id
            price = product.price
            stock = product.stock
            return JsonResponse({'success':True, 'name': name, 'category': category, 'price': price, 'stock': stock})

        form = ProductForm(request.POST, instance=Product.objects.get(id=product_id))
        if form.is_valid():
            product = form.save()
            messages.success(request, 'تم تعديل المنتج بنجاح')
            return JsonResponse({'success': True})
        else:
            messages.error(request, 'حدث خطأ أثناء تعديل المنتج')
            return JsonResponse({'success': False})
        
    except Exception as e:
        messages.error(request, f'حدث خطأ أثناء تعديل المنتج {e}')
        return JsonResponse({'success': False, 'error': str(e)})

@require_http_methods(["POST"])
def delete_product(request, product_id):
    """Handle deleting a product"""
    try: 
        Product.objects.get(id=product_id).delete()
        messages.success(request, 'تم حذف المنتج بنجاح')
        return JsonResponse({'success': True})
    except Exception as e:
        messages.error(request, f'حدث خطأ أثناء حذف المنتج {e}')
        return JsonResponse({'success': False, 'error': str(e)})

