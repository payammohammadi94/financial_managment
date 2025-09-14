from django.shortcuts import render

def home(request):
    """صفحه اصلی"""
    return render(request, 'home/index.html')
