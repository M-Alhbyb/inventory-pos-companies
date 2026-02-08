"""Category management views."""

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required

from base.models import Category

ITEMS_PER_PAGE = 10

@login_required
def categories_view(request):
    """Display all categories with search and pagination."""
    categories = Category.objects.all()
    
    # Handle search
    q = request.GET.get('q')
    if q:
        categories = categories.filter(name__icontains=q)
    
    page = request.GET.get('page', 1)
    paginator = Paginator(categories, ITEMS_PER_PAGE)
    page_obj = paginator.get_page(page)
    
    # Handle AJAX requests for infinite scroll
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return get_categories_json(page_obj)
    
    return render(request, 'categories.html', {
        'categories': categories,
        'page_obj': page_obj
    })


def get_categories_json(page_obj):
    """Return paginated categories as JSON for infinite scroll."""
    data = []
    for category in page_obj:
        data.append({
            'id': category.id,
            'name': category.name,
            'description': category.description or '',
            'products_count': category.product_set.count(),
        })
    
    return JsonResponse({
        'success': True,
        'data': data,
        'has_next': page_obj.has_next(),
        'next_page_number': page_obj.next_page_number() if page_obj.has_next() else None,
    })

@login_required
@require_http_methods(["POST"])
def add_category(request):
    """Handle adding a new category."""
    try:
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        
        # Validate inputs
        if not name:
            return JsonResponse({'success': False, 'error': 'اسم الفئة مطلوب'})
        
        if not description:
            return JsonResponse({'success': False, 'error': 'وصف الفئة مطلوب'})
        
        # Check if category already exists
        if Category.objects.filter(name=name).exists():
            return JsonResponse({'success': False, 'error': 'الفئة موجودة بالفعل'})
        
        # Create the category
        category = Category.objects.create(name=name, description=description)
        messages.success(request, 'تم إضافة الفئة بنجاح')
        
        return JsonResponse({
            'success': True,
            'category': {
                'id': category.id,
                'name': category.name,
                'description': category.description
            }
        })
        
    except Exception as e:
        messages.error(request, f'حدث خطأ أثناء إضافة الفئة {e}')
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
@require_http_methods(["POST"])
def edit_category(request, category_id):
    """Handle editing an existing category."""
    try:
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        
        # Validate inputs
        if not name:
            return JsonResponse({'success': False, 'error': 'اسم الفئة مطلوب'})
        
        if not description:
            return JsonResponse({'success': False, 'error': 'وصف الفئة مطلوب'})
        
        # Check if category name already exists (excluding current category)
        if Category.objects.filter(name=name).exclude(id=category_id).exists():
            return JsonResponse({'success': False, 'error': 'الفئة موجودة بالفعل'})
        
        # Update the category
        category = Category.objects.get(id=category_id)
        category.name = name
        category.description = description
        category.save()
        
        messages.success(request, 'تم تعديل الفئة بنجاح')
        
        return JsonResponse({
            'success': True,
            'category': {
                'id': category.id,
                'name': category.name,
                'description': category.description
            }
        })
        
    except Exception as e:
        messages.error(request, f'حدث خطأ أثناء تعديل الفئة {e}')
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
@require_http_methods(["POST"])
def delete_category(request, category_id):
    """Handle deleting a category."""
    try:
        Category.objects.get(id=category_id).delete()
        messages.success(request, 'تم حذف الفئة بنجاح')
        return JsonResponse({'success': True})
    except Exception as e:
        messages.error(request, f'حدث خطأ أثناء حذف الفئة {e}')
        return JsonResponse({'success': False, 'error': str(e)})
