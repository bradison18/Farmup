from django.shortcuts import render

def buyingpage(request):
    return render(request,'crop_selling_portal/shop.html')