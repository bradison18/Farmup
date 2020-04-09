from django.shortcuts import render
import boto3
from boto3.dynamodb.conditions import Key, Attr

def buyingpage(request):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Products')
    names = ['tomato','beans','cabbage','rice','wheat','almonds']
    rates = [25,60,30,50,75,1000]
    available = [7,5,25,10,6,5]
    # for i in range(6,12):
    #     response = table.put_item(
    #         Item={
    #             'product_id':i,
    #             'product_name':names[i-6],
    #             'product_cost':rates[i-6],
    #             'available_amount':available[i-6]
    #         }
    #     )
    response = table.scan()
    data = response['Items']
    print(data)
    return render(request,'shopping_cart/shop.html')