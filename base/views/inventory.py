from django.shortcuts import render
from base.models import Product

def inventory_view(request):
    products = Product.objects.all()
    
    # Handle search
    q = request.GET.get('q')
    if q:
        products = products.filter(name__icontains=q)
    # Handle sorting
    sort_by = request.GET.get('sort_by')
    if sort_by:
        products = products.order_by(sort_by)
    context = {
        'products': products
    }
    return render(request, 'inventory.html', context)
