"""AI-powered stock prediction views."""

from datetime import datetime

from django.shortcuts import render
from django.http import JsonResponse
from django.core.paginator import Paginator

from base.models import Product
from base.tasks import estimate_stock_out_task

ITEMS_PER_PAGE = 10


def ai_view(request):
    """Display AI predictions for stock-out dates."""
    products = Product.objects.all().order_by('estimated_stock_out')
    
    paginator = Paginator(products, ITEMS_PER_PAGE)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # Handle AJAX requests for infinite scroll
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return get_ai_predictions_json(page_obj)
    
    return render(request, 'ai.html', {
        'page_obj': page_obj,
        'current_date': datetime.now()
    })


def get_ai_predictions_json(page_obj):
    """Return paginated AI predictions as JSON for infinite scroll."""
    data = []
    for product in page_obj:
        if product.estimated_stock_out:
            data.append({
                'id': product.id,
                'name': product.name,
                'category_name': product.category.name if product.category else '-',
                'stock': product.stock,
                'estimated_stock_out': product.estimated_stock_out.strftime('%Y/%m/%d') if product.estimated_stock_out else None,
                'days_until_stock_out': product.days_until_stock_out,
            })
    
    return JsonResponse({
        'success': True,
        'data': data,
        'has_next': page_obj.has_next(),
        'next_page_number': page_obj.next_page_number() if page_obj.has_next() else None,
    })


def get_process_status(request, task_id):
    """Get the status of an async stock estimation task."""
    task = estimate_stock_out_task.AsyncResult(task_id)
    
    if task.state == 'PENDING':
        response = {'state': task.state, 'progress': 0}
    elif task.state == 'PROGRESS':
        progress = (task.info.get('current', 0) / task.info.get('total', 1)) * 100
        response = {'state': task.state, 'progress': round(progress)}
    elif task.state == 'SUCCESS':
        response = {'state': task.state, 'progress': 100, 'result': task.result}
    else:
        response = {'state': task.state, 'progress': 0, 'error': str(task.info)}
    
    return JsonResponse(response)


def ai_refresh(request):
    """Trigger async stock estimation task."""
    task = estimate_stock_out_task.delay()
    return JsonResponse({'task_id': task.id})