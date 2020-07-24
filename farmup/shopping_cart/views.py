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
    prod_id = request.POST['id']
    quantity = request.POST['quantity']
    typeof = request.POST['type']
    order_ids = []
    for k in table.scan()['Items']:
        order_ids.append(int(k['order_id']))
    type_add = ''
    if typeof == 'crops':
        table_crop = dynamodb.Table('cropinfo')
        crops_id = table_crop.scan()['Items']
        c_id = 0
        order_cost = 0
        for i in crops_id:
            if i['name']==id:
                order_cost += int(i['cost'])
                c_id += int(i['crop_id'])
        type_add = 'crops'
    elif typeof == 'fertilizer':
        table_crop = dynamodb.Table('fertilizer_info')
        crops_id = table_crop.scan()['Items']
        c_id = 0
        order_cost = 0
        for i in crops_id:
            print(i['fertilizer_id'], prod_id)
            if i['fertilizer_id']==prod_id:
                order_cost += int(i['cost'])
                c_id += int(i['fertilizer_id'])
        print(c_id)
        type_add = 'fertilizer'
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
            'ordered_time':datetime.datetime.now().time().strftime('%H:%M:%S'),
            'type':type_add

        }
    )
    # if typeof == 'crops':

    if typeof=='crops':
        table_crop = dynamodb.Table('cropinfo')
        crops_id = table_crop.scan()['Items']
        print(crops_id)
        print(type(c_id))
        crops = table_crop.scan(
            FilterExpression = Attr('crop_id').eq(str(c_id))
        )['Items']
        print(crops)
        # print(crops[0]['stock'])
        cur_stock = crops[0]['stock']
        table_crop.update_item(
            Key={
                'crop_id':str(c_id)
            },
         UpdateExpression = "set stock = :r",
        ExpressionAttributeValues={
            ':r': int(cur_stock) - int(quantity),
            },
            ReturnValues="UPDATED_NEW"

        )
    if typeof=='fertilizer':
        table_crop = dynamodb.Table('fertilizer_info')
        crops_id = table_crop.scan()['Items']
        crops = table_crop.scan(
            FilterExpression = Attr('fertilizer_id').eq(str(c_id))
        )['Items']
        print(crops[0]['quantity'])
        cur_stock = crops[0]['quantity']
        table_crop.update_item(
            Key={
                'fertilizer_id':str(c_id)
            },
         UpdateExpression = "set quantity = :r",
        ExpressionAttributeValues={
            ':r': int(cur_stock) - int(quantity),
            },
            ReturnValues="UPDATED_NEW"

        )

    return redirect(reverse('shopping_cart:buyingpage'))



def checkout(request):
    dynamodb = boto3.resource('dynamodb')
    table_order = dynamodb.Table('Order')
    table_crop = dynamodb.Table('cropinfo')
    table_fert = dynamodb.Table('fertilizer_info')
    crops = table_crop.scan()
    ferts = table_fert.scan()
    crops_ordered_images = []
    crops_ordered_names = []
    crops_ordered_cost = []
    crops_ava = []
    crops_quant = []
    crops_order_sub_cost = []
    ord_id_cr = []
    ord_id_fr = []
    items = table_order.scan(
        FilterExpression = Attr('email').eq(request.session['email']) & Attr('is_purchased').eq(False)
    )
    for i in crops['Items']:
        for j in items['Items']:
            if Decimal(i['crop_id'])==j['crop_id'] and j['type']=='crops':
                crops_quant.append(j['quantity'])
                crops_order_sub_cost.append(int(j['quantity'])*int(i['cost']))
    for i in ferts['Items']:
        for j in items['Items']:
            if Decimal(i['fertilizer_id'])==j['crop_id'] and j['type']=='fertilizer':
                crops_quant.append(j['quantity'])
                crops_order_sub_cost.append(int(j['quantity'])*int(i['cost']))

    for i in range(len(items['Items'])):
        if items['Items'][i]['type']=='crops':
            ord_id_cr.append(items["Items"][i]['crop_id'])
    for i in range(len(items['Items'])):
        if items['Items'][i]['type']=='fertilizer':
            ord_id_fr.append(items["Items"][i]['crop_id'])
    for j in crops['Items']:
        for k in ord_id_cr:
            if j['crop_id']==str(k):
                crops_ordered_images.append(j['image_link'])
                crops_ordered_names.append(j['name'])
                crops_ordered_cost.append(j['cost'])
                crops_ava.append(j['stock'])
    for j in ferts['Items']:
        for k in ord_id_fr:
            if j['fertilizer_id']==str(k):
                crops_ordered_images.append(j['img_url'])
                crops_ordered_names.append(j['fertilizer_name'])
                crops_ordered_cost.append(j['cost'])
                crops_ava.append(j['quantity'])

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
        order_ids_cr = []
        order_ids_fr = []
        for i in responses['Items']:
            if i['type']=='crops':
                order_ids_cr.append(str(i['crop_id']))
            if i['type']=='fertilizer':
                order_ids_fr.append(str(i['crop_id']))
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
            'order_ids':order_ids_cr
        }
        return render(request,'shopping_cart/shop.html',context)


def delete_from_cart(request,item_name):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Order')
    crop_table = dynamodb.Table('cropinfo')
    fert_table = dynamodb.Table('fertilizer_info')
    responses = crop_table.scan(
        FilterExpression = Attr('name').eq(item_name)
    )
    responses_fert = fert_table.scan(
        FilterExpression = Attr('fertilizer_name').eq(item_name)
    )
    # if responses
    try:
        crop_id = responses['Items'][0]['crop_id']
        cur_stock = responses['Items'][0]['stock']
        order_quan = table.scan(
            FilterExpression = Attr('crop_id').eq(Decimal(crop_id)) & Attr('email').eq(request.session['email'])
        )['Items'][0]['quantity']
        print('here')

        crop_table.update_item(
            Key={
                'crop_id': crop_id
            },
            UpdateExpression="set stock = :r",
            ExpressionAttributeValues={
                ':r': int(cur_stock) + int(order_quan),
            },
            ReturnValues="UPDATED_NEW"
        )
    except:
        crop_id = responses_fert['Items'][0]['fertilizer_id']
        cur_stock = responses_fert['Items'][0]['quantity']
        order_quan = table.scan(
            FilterExpression = Attr('crop_id').eq(Decimal(crop_id)) & Attr('email').eq(request.session['email'])
        )['Items'][0]['quantity']
        fert_table.update_item(
            Key={
                'fertilizer_id': crop_id
            },
            UpdateExpression="set quantity = :r",
            ExpressionAttributeValues={
                ':r': int(cur_stock) + int(order_quan),
            },
            ReturnValues="UPDATED_NEW"
        )

    delete_orders = table.scan(
        FilterExpression = Attr('crop_id').eq(Decimal(crop_id)) & Attr('email').eq(request.session['email'])
    )
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
    address1 = request.POST.get('Address1')
    address2 = request.POST.get('Address2')
    state = request.POST.get('state')
    city = request.POST.get('city')
    pincode = request.POST.get('pincode')
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
    for i in range(len(crop_table_elements)):
        if (name.lower() == crop_table_elements[i]['name'].lower()  or name.lower() in crop_table_elements[i]['name'].lower() or distance(name.lower(),crop_table_elements[i]['name'].lower()) > 0.8) and int(crop_table_elements[i]['cost']) <int(quan):
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

def change_quantity(request,cropname,quan,oper):
    dynamodb = boto3.resource('dynamodb')
    crop_table = dynamodb.Table('cropinfo')
    fert_table = dynamodb.Table('fertilizer_info')
    order_table = dynamodb.Table('Order')
    crops = crop_table.scan(
        FilterExpression = Attr('name').eq(cropname)
    )['Items']
    ferts = fert_table.scan(
        FilterExpression = Attr('fertilizer_name').eq(cropname)
    )['Items']
    if crops:
        id = crops[0]['crop_id']
        cur_stock = crops[0]['stock']
        order_ids = order_table.scan(
            FilterExpression = Attr('email').eq(request.session['email']) & Attr('is_purchased').eq(False) & Attr('crop_id').eq(Decimal(id))
        )['Items'][0]['order_id']
        if oper=='add':
            order_table.update_item(
                Key={
                    'order_id':order_ids
                },
             UpdateExpression = "set quantity = :r",
            ExpressionAttributeValues={
                ':r': int(quan)+1,
                },
                ReturnValues="UPDATED_NEW"

            )
            crop_table.update_item(
                Key={
                    'crop_id': id
                },
                UpdateExpression="set stock = :r",
                ExpressionAttributeValues={
                    ':r': int(cur_stock)-1,
                },
                ReturnValues="UPDATED_NEW"

            )
        elif oper=='minus':
            if int(quan) > 1:
                order_table.update_item(
                    Key={
                        'order_id': order_ids
                    },
                    UpdateExpression="set quantity = :r",
                    ExpressionAttributeValues={
                        ':r': int(quan) - 1,
                    },
                    ReturnValues="UPDATED_NEW"
                )
            crop_table.update_item(
                Key={
                    'crop_id': id
                },
                UpdateExpression="set stock = :r",
                ExpressionAttributeValues={
                    ':r': int(cur_stock)+1,
                },
                ReturnValues="UPDATED_NEW"
            )
    else:
        id = ferts[0]['fertilizer_id']
        cur_stock = ferts[0]['quantity']
        order_ids = order_table.scan(
            FilterExpression=Attr('email').eq(request.session['email']) & Attr('is_purchased').eq(False) & Attr('crop_id').eq(Decimal(id))
        )['Items'][0]['order_id']
        if oper == 'add':
            order_table.update_item(
                Key={
                    'order_id': order_ids
                },
                UpdateExpression="set quantity = :r",
                ExpressionAttributeValues={
                    ':r': int(quan) + 1,
                },
                ReturnValues="UPDATED_NEW"

            )
            fert_table.update_item(
                Key={
                    'fertilizer_id': id
                },
                UpdateExpression="set quantity = :r",
                ExpressionAttributeValues={
                    ':r': int(cur_stock) - 1,
                },
                ReturnValues="UPDATED_NEW"

            )
        elif oper == 'minus':
            if int(quan) > 1:
                order_table.update_item(
                    Key={
                        'order_id': order_ids
                    },
                    UpdateExpression="set quantity = :r",
                    ExpressionAttributeValues={
                        ':r': int(quan) - 1,
                    },
                    ReturnValues="UPDATED_NEW"
                )
            fert_table.update_item(
                Key={
                    'fertilizer_id': id
                },
                UpdateExpression="set quantity = :r",
                ExpressionAttributeValues={
                    ':r': int(cur_stock) + 1,
                },
                ReturnValues="UPDATED_NEW"
            )

    return redirect('shopping_cart:cart')
