from django.shortcuts import render
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.core.mail import send_mail
from django.conf import settings
from random import *
from boto3.dynamodb.conditions import Key, Attr
from twilio.rest import Client
import datetime
from django.utils.crypto import get_random_string
import boto3
# Create your views here.

try:
    import httplib
except:
    import http.client as httplib


def index(request):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Balances')
    cur = request.session['email']
    redeem_table = dynamodb.Table('pending_redeem')
    redeem_response = redeem_table.scan(
        FilterExpression = Attr('email').eq(cur)
    )

    user = request.session['username']
    response = table.scan(
        FilterExpression = Attr('email').eq(cur)
    )
    if len(response['Items'])>0:
        balance = response['Items'][0]['balance']
    else:
        balance = 100
    if request.method=='POST':
        amount = request.POST['amounts']
        balances = {'bal':balance}
    else:
        balances = {'bal': balance,'amount':redeem_response['Items'][0]['amount']}
    return render(request,'credits/index.html',context=balances)

def pending_redeem(request):
    dynamodb = boto3.resource('dynamodb')
    table_balance = dynamodb.Table('Balances')
    table_pending = dynamodb.Table('pending_redeem')
    cur = request.session['email']
    responses_redeem = table_pending.scan(
        FilterExpression=Attr('email').eq(cur)
    )
    cur = request.session['email']
    if request.method=='POST':
        amount = request.POST.get('redeem_amount',False)
        balance = request.POST.get('balance',False)
        if int(balance) - int(amount) < 0:
            return HttpResponse('<html><p> you have insufficient balanace.  </p><a href="/credits"> You can add balance here. </a></html>')
        auth_token = '9db2adb42474888f2d72068004f30e15'
        account_sid = 'ACb702ef99316a96af55ee6415656e9486'
        client = Client(account_sid, auth_token)
        # client.messages.create(
        #     to="+91" + str(9121467576),
        #     from_="+12025190638",
        #     body="Use {} code for verification.Amount requested to redeem is {}".format(responses_redeem['Items'][0]['code'], amount))
    return render(request,'credits/pending_redeem.html')

def verify_sms(request):
    code = request.POST['code']
    dynamodb = boto3.resource('dynamodb')
    table_balance = dynamodb.Table('Balances')
    table_pending = dynamodb.Table('pending_redeem')
    table_order = dynamodb.Table('Order')
    table_user = dynamodb.Table('user')
    cur = request.session['email']
    responses_redeem = table_pending.scan(
        FilterExpression=Attr('email').eq(cur)
    )
    if code!=responses_redeem['Items'][0]['code']:
        return HttpResponse('<html><script>alert("Incorrect code");window.location="/credits/pending_redeem";</script></html>')
    balance = table_balance.scan(
        FilterExpression=Attr('email').eq(cur)
    )
    user = table_user.scan(
        FilterExpression=Attr('email').eq(cur)
    )['Items'][0]['username']
    amount = responses_redeem['Items'][0]['amount']
    balance_user = int(balance['Items'][0]['balance'])
    response = table_balance.update_item(
        Key={
            #'email': user['email'],
            # 'user':user
            'email':request.session['email']
        },
        UpdateExpression="set balance = :r",
        ExpressionAttributeValues={
            ':r': balance_user-int(amount),

        },
        ReturnValues="UPDATED_NEW"
    )
    trans_id = responses_redeem['Items'][0]['transaction_id']
    table_pending.delete_item(
        Key={
            'transaction_id':trans_id
        }
    )
    user_orders = table_order.scan(
        FilterExpression=Attr('email').eq(cur)
    )['Items']
    order_ids = []
    print(user_orders)
    for i in user_orders:
        order_ids.append(i['order_id'])
    print(order_ids)
    for i in order_ids:
        res = table_order.update_item(
            Key={
                # 'email': user['email'],
                # 'user':user
                'order_id': i
            },
            UpdateExpression="set is_purchased = :r",
            ExpressionAttributeValues={
                ':r': True,

            },
            ReturnValues="UPDATED_NEW"
        )
    table_tr = dynamodb.Table('transactions')
    table_tr.put_item(
        Item={
            'transaction_id':trans_id,
            'username': request.session['username'],
            'email': request.session['email'],
            'date': datetime.date.today().strftime('%B %d,%Y'),
            'time': datetime.datetime.now().time().strftime('%H:%M:%S'),
            'amount':amount

        }
    )
    return HttpResponse('redeem sucess')