from django.shortcuts import render
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.core.mail import send_mail
from django.conf import settings
from random import *
from boto3.dynamodb.conditions import Key, Attr
import uuid
import string
from datetime import datetime
from twilio.rest import Client
from django.utils.crypto import get_random_string
from django.contrib.auth.decorators import login_required
import boto3
# Create your views here.

try:
    import httplib
except:
    import http.client as httplib


def have_internet():
    conn = httplib.HTTPConnection("www.google.com", timeout=5)
    try:
        conn.request("HEAD", "/")
        conn.close()
        return True
    except:
        conn.close()
        return False

def index(request):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('user_balance')
    print('session when not loggied in ',request.session)
    cur = request.session['email']
    response = table.scan(
        FilterExpression = Attr('email').eq(cur)
    )
    print(response)
    if len(response['Items'])>0:
        balance = response['Items'][0]['balance']
    else:
        cur_ids = []
        for i in response["Items"]:
            cur_ids.append(i['id'])
        if cur_ids:
            max_id = max(cur_ids)
        else:
            max_id = 1
        responses = table.put_item(
            Item = {
                'id':max_id,
                'balance':100,
                'email':cur
            }
        )
        balance = 100
    balances = {'bal':balance}
    return render(request,'credits/index.html',context=balances)

def pending_redeem(request):
    redeem_amount = request.POST['redeem_amount']
    seed()
    code = get_random_string(length=6,allowed_chars='1234567890')
