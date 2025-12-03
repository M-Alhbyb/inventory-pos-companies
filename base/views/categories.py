from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from base.models import Category
from django.contrib import messages

def categories_view(request):
    categories = Category.objects.all()
    if request.method == 'GET':
        q = request.GET.get('q')
        if q:
            categories = categories.filter(name__icontains=q)
    return render(request, 'categories.html', {'categories': categories})

@require_http_methods(["POST"])
def add_category(request):
    """Handle adding a new category"""
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
        category = Category.objects.create(
            name=name,
            description=description
        )
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

@require_http_methods(["POST"])
def edit_category(request, category_id):
    """Handle adding a new category"""
    try:
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        
        # Validate inputs
        if not name:
            return JsonResponse({'success': False, 'error': 'اسم الفئة مطلوب'})
        
        if not description:
            return JsonResponse({'success': False, 'error': 'وصف الفئة مطلوب'})
        
        # Check if category already exists
        if Category.objects.filter(name=name and id!=category_id).exists():
            return JsonResponse({'success': False, 'error': 'الفئة موجودة بالفعل'})
            
        # Create the category
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

@require_http_methods(["POST"])
def delete_category(request, category_id):
    print('category_id', category_id)
    """Handle deleting a category"""
    try: 
        Category.objects.get(id=category_id).delete()
        messages.success(request, 'تم حذف الفئة بنجاح')
        return JsonResponse({'success': True})
    except Exception as e:
        messages.error(request, f'حدث خطأ أثناء حذف الفئة {e}')
        return JsonResponse({'success': False, 'error': str(e)})

