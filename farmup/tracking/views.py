from django.shortcuts import render,redirect
from registration.login_required import is_loggedin
import boto3
from boto3.dynamodb.conditions import Key, Attr
from decimal import *
from django.http import HttpResponse
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
        crop_order_id = []
        corps = table_crop.scan()['Items']
        # print(corps[0]['cr'])
        for i in order_items:

            crops = table_crop.scan(
                FilterExpression=Attr('crop_id').eq(str(i['crop_id']))
            )['Items'][0]
            # print(crops)
            if crops['crop_id'] not in crop_order_id:
                crop_order_id.append(crops['crop_id'])
                crop_orders.append(crops)
        # print(crop_orders)
        context = {
            'orders':order_items,
            'is_admin':is_admin,
            'crop_orders':crop_orders
        }
        return render(request,'tracking/tracking.html',context)
    else:
        return redirect('registration:login_display')


def change_status(request):

    if request.method=='POST':
        dynamodb = boto3.resource('dynamodb')
        table_order = dynamodb.Table('Order')
        item = request.POST['change']
        order_id = request.POST['order_id']
        orders = table_order.update_item(
            Key={

                'order_id': order_id
            },
            UpdateExpression="set delivery_status = :r",
            ExpressionAttributeValues={
                ':r': item
            },
            ReturnValues="UPDATED_NEW"
        )
    return HttpResponse('ad')