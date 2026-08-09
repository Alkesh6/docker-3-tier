from django.shortcuts import render
from .models import Product

def product_list(request):
    products = Product.objects.all().order_by("id")
    return render(request, "products/index.html", {"products": products})
