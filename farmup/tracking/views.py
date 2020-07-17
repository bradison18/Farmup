from django.shortcuts import render,redirect
from registration.login_required import is_loggedin
import boto3
from boto3.dynamodb.conditions import Key, Attr
from decimal import *

# Create your views here.
def track(request):
    if is_loggedin(request):
        dynamodb = boto3.resource('dynamodb')
        table_order = dynamodb.Table('Order')
        table_crop = dynamodb.Table('cropinfo')
        table_user = dynamodb.Table('user')
        cur = request.session['email']
        is_admin = False

        users = table_user.scan(
            FilterExpression=Attr('email').eq(cur)
        )['Items']
        try:
            if users[0]['is_admin']:
                is_admin = True
        except:
            is_admin = False
        if not is_admin:
            order_items = table_order.scan(
                FilterExpression=Attr('email').eq(cur)
            )['Items']
        else:
            order_items = table_order.scan()['Items']
        # print(order_items)
        crop_orders = []
        for i in order_items:
            crops = table_crop.scan(
                FilterExpression=Attr('cropid').eq(Decimal(i['crop_id']))
            )
            print(crops)
        context = {
            'orders':order_items,
            'is_admin':is_admin
        }
        return render(request,'tracking/tracking.html',context)
    else:
        return redirect('registration:login_display')