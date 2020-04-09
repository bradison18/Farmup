from django.shortcuts import render
import boto3
from boto3.dynamodb.conditions import Key, Attr

def buyingpage(request):
    return render(request,'shopping_cart/shop.html')