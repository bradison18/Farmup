from django.shortcuts import render,redirect
import boto3
from django.contrib.auth.decorators import login_required
from boto3.dynamodb.conditions import Key, Attr
from django.urls import reverse

def addCropElements(request,**kwargs):
    dynamodb=boto3.resource('dynamodb')
    table=dynamodb.Table('Order')
    id = kwargs.get('slug')
    table_crop = dynamodb.Table('cropinfo')
    crops_id = table_crop.scan()['Items']
    # no_of_orders = table.scan()
    order_ids = []
    for k in table.scan()['Items']:
        order_ids.append(k['order_id'])
    # print(order_ids)
    c_id = 0
    order_cost = 0
    for i in crops_id:
        if i['crop_name']==id:
            order_cost += i['cost']
            c_id += i['crop_id']
    table.put_item(
        Item = {
            'order_id':max(order_ids) + 1,
            'crop_id':c_id,
            'username':request.session['username'],
            'email':request.session['email'],
            'quantity':4,
            'cost':3*order_cost
        }
    )
    return redirect(reverse('shopping_cart:buyingpage'))



def checkout(request):
    dynamodb = boto3.resource('dynamodb')
    table_order = dynamodb.Table('Order')
    table_crop = dynamodb.Table('cropinfo')
    crops = table_crop.scan()
    crops_ordered_images = []
    crops_ordered_names = []
    crops_ordered_cost = []
    crops_ava = []
    ord_id = []
    items = table_order.scan(
        FilterExpression = Attr('email').eq(request.session['email'])
    )
    for i in range(len(items['Items'])):
        ord_id.append(items["Items"][i]['crop_id'])
    for j in crops['Items']:
        for k in ord_id:
            if j['crop_id']==k:
                crops_ordered_images.append(j['crop_image_link'])
                crops_ordered_names.append(j['crop_name'])
                crops_ordered_cost.append(j['cost'])
                crops_ava.append(j['crop_amount'])
    total_crops_ordered = zip(crops_ordered_names,crops_ordered_images,crops_ordered_cost,crops_ava)
    context = {
        'total':total_crops_ordered
    }
    return render(request,'shopping_cart/cart.html',context)

def buyingpage(request):
    dynamodb=boto3.resource('dynamodb')
    crop_table=dynamodb.Table('cropinfo')
    order_table = dynamodb.Table('Order')
    responses = order_table.scan(
        FilterExpression = Attr('email').eq(request.session['email'])
    )
    order_ids = []
    for i in responses['Items']:
        order_ids.append(i['crop_id'])
    crop_table_elements=crop_table.scan()['Items']
    crop_id = []
    crop_name=[]
    crop_cost=[]
    crop_amount=[]
    crop_image_link=[]

    for i in range(len(crop_table_elements)):
        crop_id.append(crop_table_elements[i]['crop_id'])
        crop_name.append(crop_table_elements[i]['crop_name'])
        crop_cost.append(crop_table_elements[i]['cost'])
        crop_amount.append(crop_table_elements[i]['crop_amount'])
        crop_image_link.append(crop_table_elements[i]['crop_image_link'])
    
    crop_info=zip(crop_id,crop_name,crop_cost,crop_amount,crop_image_link)
    context={
        'crop_info':crop_info,
        'order_ids':order_ids
    }
    return render(request,'shopping_cart/shop.html',context)

def delete_from_cart(request,item_name):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Order')
    crop_table = dynamodb.Table('cropinfo')
    responses = crop_table.scan(
        FilterExpression = Attr('crop_name').eq(item_name)
    )
    print(responses)
    crop_id = responses['Items'][0]['crop_id']
    print(crop_id)
    delete_orders = table.scan(
        FilterExpression = Attr('crop_id').eq(crop_id) & Attr('email').eq(request.session['email'])
    )
    print(delete_orders)
    order_id = delete_orders['Items'][0]['order_id']
    table.delete_item(
        Key={
            'order_id':order_id
        }
    )
    # for i in table.scan()['Items']:
    #     if i['crop_id']==crop_id:
    #         table.delete_item(
    #             Key={
    #                 'crop_id':crop_id,
    #                 'email':request.session['email']
    #             }
    #         )
#    print(responses)
    return redirect(reverse('shopping_cart:cart'))