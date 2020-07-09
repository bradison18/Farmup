from django.shortcuts import render,redirect
import boto3
from django.contrib.auth.decorators import login_required
from boto3.dynamodb.conditions import Key, Attr
from django.urls import reverse
from django.http import HttpResponse

def add(request):
    # print('ad')
    dynamodb=boto3.resource('dynamodb')
    table=dynamodb.Table('cropinfo')
    print(table)
    items = ['tomato','potato','carrot','watermelon']
    cost = ['40','20','45','35']
    stock = [10,30,20,30]
    links = ['https://uploads.scratch.mit.edu/users/avatars/443/3561.png','https://3.imimg.com/data3/OE/IJ/MY-331481/potato-250x250.jpg','https://www.fondation-louisbonduelle.org/wp-content/uploads/2016/10/carotte_222805396.png','https://lh3.googleusercontent.com/proxy/K6e0y7jx1yU2gtlPntCMPCVW327GNnKcsk26RDSA_PvCVqzHq8hvIECZP4Rs-O6xHIXpDngdgYlnahn8l7UiIZI4ZA05258I38m8r-RU3tIWyEYthJER1FbayHWHbEc']
    for i in range(len(items)):
        table.put_item(
            Item={
                'crop_id': str(i+1),
                'name': items[i],
                'image_link': links[i],
                'cost':cost[i],
                'stock':stock[i]
            }
        )
    return HttpResponse('add products')


# @login_required(login_url='registration:login')
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


# @login_required(login_url='registration:login')

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
                crops_ordered_images.append(j['image_link'])
                crops_ordered_names.append(j['name'])
                crops_ordered_cost.append(j['cost'])
                crops_ava.append(j['crop_amount'])
    total_crops_ordered = zip(crops_ordered_names,crops_ordered_images,crops_ordered_cost,crops_ava)
    context = {
        'total':total_crops_ordered
    }
    return render(request,'shopping_cart/cart.html',context)



# @login_required(login_url='registration:login')

def buyingpage(request):
    dynamodb=boto3.resource('dynamodb')
    crop_table=dynamodb.Table('cropinfo')
    order_table = dynamodb.Table('Order')
    print(request.session)
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
        crop_name.append(crop_table_elements[i]['name'])
        crop_cost.append(crop_table_elements[i]['cost'])
        crop_amount.append(crop_table_elements[i]['crop_amount'])
        crop_image_link.append(crop_table_elements[i]['crop_image_link'])
    
    crop_info=zip(crop_id,crop_name,crop_cost,crop_amount,crop_image_link)
    context={
        'crop_info':crop_info,
        'order_ids':order_ids
    }
    return render(request,'shopping_cart/shop.html',context)

# @login_required(login_url='registration:login')

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