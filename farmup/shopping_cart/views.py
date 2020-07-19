from django.shortcuts import render,redirect
import boto3
from boto3.dynamodb.conditions import Key, Attr
from django.urls import reverse
from django.http import HttpResponse
from decimal import *
from registration.login_required import is_loggedin
import uuid
from django.utils.crypto import get_random_string
import datetime
import textdistance
def add(request):
    dynamodb=boto3.resource('dynamodb')
    table=dynamodb.Table('cropinfo')
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


def addCropElements(request):
    dynamodb=boto3.resource('dynamodb')
    table=dynamodb.Table('Order')
    id = request.POST['crop_name']
    quantity = request.POST['quantity']

    table_crop = dynamodb.Table('cropinfo')
    crops_id = table_crop.scan()['Items']
    order_ids = []
    for k in table.scan()['Items']:
        order_ids.append(int(k['order_id']))
    c_id = 0
    order_cost = 0
    for i in crops_id:
        if i['name']==id:
            order_cost += int(i['cost'])
            c_id += int(i['crop_id'])
    if order_ids:
        ids = str(max(order_ids)+1)
    else:
        ids = '1'
    table.put_item(
        Item = {
            'order_id': ids,
            'crop_id':c_id,
            'username':request.session['username'],
            'email':request.session['email'],
            'quantity':quantity,
            'cost':int(quantity)*order_cost,
            'is_purchased':False,
            'delivery_status':'Not Purchased',
            'ordered_date':datetime.date.today().strftime('%B %d,%Y'),
            'ordered_time':datetime.datetime.now().time().strftime('%H:%M:%S')

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
    crops_quant = []
    crops_order_sub_cost = []
    ord_id = []
    items = table_order.scan(
        FilterExpression = Attr('email').eq(request.session['email']) & Attr('is_purchased').eq(False)
    )
    print(items)
    for i in items['Items']:
        crops_quant.append(i['quantity'])
        crops_order_sub_cost.append(int(i['cost']))
    for i in range(len(items['Items'])):
        ord_id.append(items["Items"][i]['crop_id'])

    for j in crops['Items']:
        for k in ord_id:
            if j['crop_id']==str(k):
                crops_ordered_images.append(j['image_link'])
                crops_ordered_names.append(j['name'])
                crops_ordered_cost.append(j['cost'])
                crops_ava.append(j['stock'])

    total_cost = 0
    for i in crops_order_sub_cost:
        total_cost += i

    total_crops_ordered = zip(crops_ordered_names,crops_ordered_images,crops_ordered_cost,crops_ava,crops_order_sub_cost,crops_quant)
    context = {
        'total':total_crops_ordered,
        'total_cost':total_cost
    }
    return render(request,'shopping_cart/cart.html',context)

def buyingpage(request):
    if not is_loggedin(request):
        return redirect('home')
    else:

        dynamodb=boto3.resource('dynamodb')
        crop_table=dynamodb.Table('cropinfo')
        order_table = dynamodb.Table('Order')

        responses = order_table.scan(
            FilterExpression = Attr('email').eq(request.session['email']) & Attr('is_purchased').eq(False)
        )
        # print(type(request.session['email']))
        # print(type(responses['Items'][0]['email']))
        # print(responses)
        order_ids = []
        for i in responses['Items']:
            order_ids.append(str(i['crop_id']))
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
            crop_amount.append(crop_table_elements[i]['stock'])
            crop_image_link.append(crop_table_elements[i]['image_link'])

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
        FilterExpression = Attr('name').eq(item_name)
    )
    print(item_name)
    crop_id = responses['Items'][0]['crop_id']
    delete_orders = table.scan(
        FilterExpression = Attr('crop_id').eq(Decimal(crop_id)) & Attr('email').eq(request.session['email'])
    )
    print(delete_orders)
    order_id = delete_orders['Items'][0]['order_id']
    table.delete_item(
        Key={
            'order_id':order_id
        }
    )
    return redirect(reverse('shopping_cart:cart'))


def checkout_sub(request):
    dynamodb = boto3.resource('dynamodb')
    amount = request.POST.get('amounts')
    username = request.POST.get('username')
    email = request.POST.get('email')
    address1 = request.POST.get('Address1')
    address2 = request.POST.get('Address2')
    state = request.POST.get('state')
    city = request.POST.get('city')
    pincode = request.POST.get('pincode')
    print('username',username)
    billing_table = dynamodb.Table('billing_address')
    billing_adds = billing_table.scan(
        FilterExpression=Attr('email').eq(request.session['email'])
    )['Items']
    if len(billing_adds)==0:
        billing_table.put_item(
            Item={
                'username': request.session['username'],
                'email': request.session['email'],
                'address1': address1,
                'address2': address2,
                'state': state,
                'city': city,
                'pincode': pincode,
            }
        )
    transaction_id= "DR" + uuid.uuid4().hex[:9].upper()
    orders_table = dynamodb.Table('pending_redeem')
    code = get_random_string(length=6,allowed_chars='0123456789')
    redeem_responses = orders_table.scan(
        FilterExpression = Attr('email').eq(request.session['email'])
    )['Items']
    all_transactions = [i['transaction_id'] for i in redeem_responses]
    if len(all_transactions)>0:
        for i in all_transactions:
            orders_table.delete_item(
                Key={
                    'transaction_id':i
                }
            )
    orders_table.put_item(
        Item={
            'transaction_id': transaction_id,
            'username': request.session['username'],
            'email': request.session['email'],
            'code':code,
            'amount':amount,
            'date':datetime.date.today().strftime('%B %d,%Y'),
            'time':datetime.datetime.now().time().strftime('%H:%M:%S')
        }
    )
    return redirect('index')


def add_items(request):
    item = request.POST['quantity']
    id = request.POST['crop_name']
    return redirect('shopping_cart:cart')


def search(request):
    dynamodb = boto3.resource('dynamodb')
    crop_table = dynamodb.Table('cropinfo')
    order_table = dynamodb.Table('Order')

    responses = order_table.scan(
        FilterExpression=Attr('email').eq(request.session['email']) & Attr('is_purchased').eq(False)
    )
    order_ids = []
    for i in responses['Items']:
        order_ids.append(str(i['crop_id']))
    crop_table_elements = crop_table.scan()['Items']
    crop_id = []
    crop_name = []
    crop_cost = []
    crop_amount = []
    crop_image_link = []

    name = request.POST['crop_name']
    quan = request.POST['range']
    print(quan)
    for i in range(len(crop_table_elements)):
        # print(crop_table_elements[i]['name'])
        print(name,crop_table_elements[i]['name'],name.lower() == crop_table_elements[i]['name'].lower())
        print(name,crop_table_elements[i]['name'],name.lower() in crop_table_elements[i]['name'].lower())
        print(name,crop_table_elements[i]['name'], distance(name.lower(),crop_table_elements[i]['name'].lower()) > 0.8)
        print(name,crop_table_elements[i]['name'],crop_table_elements[i]['cost']>quan,crop_table_elements[i]['cost'])
        print((name.lower() == crop_table_elements[i]['name'].lower()  or name.lower() in crop_table_elements[i]['name'].lower() or distance(name.lower(),crop_table_elements[i]['name'].lower()) > 0.8))
        if (name.lower() == crop_table_elements[i]['name'].lower()  or name.lower() in crop_table_elements[i]['name'].lower() or distance(name.lower(),crop_table_elements[i]['name'].lower()) > 0.8) and crop_table_elements[i]['cost'] <quan:
            print('here')
            crop_id.append(crop_table_elements[i]['crop_id'])
            crop_name.append(crop_table_elements[i]['name'])
            crop_cost.append(crop_table_elements[i]['cost'])
            crop_amount.append(crop_table_elements[i]['stock'])
            crop_image_link.append(crop_table_elements[i]['image_link'])

    crop_info = zip(crop_id, crop_name, crop_cost, crop_amount, crop_image_link)
    context = {
        'crop_info': crop_info,
        'order_ids': order_ids
    }

    return render(request,'shopping_cart/shop.html',context)

def distance(word1,word2):
    return textdistance.jaro_winkler(word1,word2)