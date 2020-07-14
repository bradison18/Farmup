from django.shortcuts import render
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.core.mail import send_mail
from django.conf import settings
from random import *
from boto3.dynamodb.conditions import Key, Attr
from twilio.rest import Client

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
    print(redeem_response['Items'])
    user = request.session['username']
    response = table.scan(
        FilterExpression = Attr('email').eq(cur)
    )
    if len(response['Items'])>0:
        balance = response['Items'][0]['balance']
        print('if')
    else:
        # print('else')
        # cur_ids = []
        # for i in response["Items"]:
        #     cur_ids.append(i['id'])
        # if cur_ids:
        #     max_id = max(cur_ids)
        # else:
        #     max_id = 1
        # responses = table.put_item(
        #     Item = {
        #         'id':max_id,
        #         'user':user,
        #         'balance':100,
        #         'email':cur
        #     }
        # )
        balance = 100
    if request.method=='POST':
        print('post yes')
        amount = request.POST['amounts']
        print(amount)
        balances = {'bal':balance}
    else:
        print(redeem_response)
        # print(redeem_response[0])
        balances = {'bal': balance,'amount':redeem_response['Items'][0]['amount']}
    return render(request,'credits/index.html',context=balances)

def pending_redeem(request):
    print(request.method)
    if request.method=='POST':
        amount = request.POST.get('redeem_amount',False)
    return HttpResponse('into pending redeem')