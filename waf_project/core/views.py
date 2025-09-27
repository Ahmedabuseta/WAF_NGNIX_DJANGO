from django.shortcuts import render
from django.http import HttpResponse

def api_docs(request):
    """API documentation page"""
    return render(request, 'core/api_docs.html')

def test_protected_site(request):
    """Test route for WAF demonstration"""
    return HttpResponse("This is a test protected site")

def chart_test(request):
    """Chart testing page"""
    return render(request, 'core/chart_test.html')
