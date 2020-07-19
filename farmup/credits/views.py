from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.conf import settings
from boto3.dynamodb.conditions import Key, Attr
from twilio.rest import Client
import datetime
import uuid
import boto3
import stripe
from django.http.response import JsonResponse
from django.views.decorators.csrf import csrf_exempt
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
            return HttpResponse('<html><p> you have insufficient balanace.  </p><a href="/credits/add_balance/"> You can add balance here. </a></html>')
        # auth_token = '55f9a8db2286ced48a7203fd9b06b512'
        auth_token = 'fee9d1c80d8250c006f9c97a67d1115f'
        account_sid = 'ACb702ef99316a96af55ee6415656e9486'
        # account_sid = ''
        client = Client(account_sid, auth_token)
        client.messages.create(
            to="+91" + str(9121467576),
            from_="+12025190638",
            body="Use {} code for verification.Amount requested to redeem is {}".format(responses_redeem['Items'][0]['code'], amount))
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
            ':r': balance_user-int(amount)
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
        FilterExpression=Attr('email').eq(cur) and Attr('is_purchased').eq(False)
    )['Items']
    order_ids = []
    print(user_orders)
    for i in user_orders:
        order_ids.append(i['order_id'])
    print(order_ids)
    for i in order_ids:
        res = table_order.update_item(
            Key={
                'order_id': i
            },
            UpdateExpression="set is_purchased = :r, delivery_status = :t, ordered_date = :d, ordered_time = :s",
            ExpressionAttributeValues={
                ':r': True,
                ':t': 'Purchased',
                ':d': datetime.date.today().strftime('%B %d,%Y'),
                ':s': datetime.datetime.now().time().strftime('%H:%M:%S')
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
            'amount':amount,
            'type':'debit'
        }
    )
    return redirect('tracking:track')


def add_balance(request):
    return render(request,'credits/add_balance.html')

def home(request):
    amount = request.POST['amount']
    dynamodb = boto3.resource('dynamodb')
    # table_balance = dynamodb.Table('Balances')
    table_pending = dynamodb.Table('pending_transactions')
    pending_redeems = table_pending.scan(
        FilterExpression=Attr('email').eq(request.session['email'])
    )['Items']
    trans_ids = [i['transaction_id'] for i in pending_redeems]
    if len(trans_ids)>0:
        for i in trans_ids:
            table_pending.delete_item(
                Key={
                    'transaction_id':i
                }
            )
    trans_id = "CR" + uuid.uuid4().hex[:9].upper()

    table_pending.put_item(
        Item={
            'transaction_id': trans_id,
            'username': request.session['username'],
            'email': request.session['email'],
            'date': datetime.date.today().strftime('%B %d,%Y'),
            'time': datetime.datetime.now().time().strftime('%H:%M:%S'),
            'amount': amount,
            # 'status':'pending'

        }
    )


    return render(request,'credits/home.html')

@csrf_exempt
def stripe_config(request):
    if request.method == 'GET':
        stripe_config = {'publicKey': settings.STRIPE_PUBLISHABLE_KEY}
        return JsonResponse(stripe_config, safe=False)


@csrf_exempt
def create_checkout_session(request):
    if request.method == 'GET':
        domain_url = 'http://127.0.0.1:8000/'
        stripe.api_key = settings.STRIPE_SECRET_KEY
        try:
            dynamodb = boto3.resource('dynamodb')
            table_pending = dynamodb.Table('pending_transactions')
            pending_redeems = table_pending.scan(
                FilterExpression=Attr('email').eq(request.session['email'])
            )['Items']
            trans_id = pending_redeems[0]['transaction_id']
            print('amount',pending_redeems[0]['amount'])
            amt = int(pending_redeems[0]['amount'])*100
            # ?session_id={CHECKOUT_SESSION_ID} means the redirect will have the session ID set as a query param
            checkout_session = stripe.checkout.Session.create(
                # success_url=domain_url + 'success',
                success_url=domain_url + 'credits/success/{CHECKOUT_SESSION_ID}/'+trans_id,
                cancel_url=domain_url + 'credits/cancelled/{CHECKOUT_SESSION_ID}/'+trans_id,
                payment_method_types=['card'],
                # customer_email='santosh.265559@gmail.com',
                billing_address_collection='required',
                shipping_address_collection={
                    'allowed_countries': ['IN'],
                },
                # shipping_address_collection='IN',
                mode='payment',
                line_items=[
                    {
                        'name': 'T-shirt',
                        'quantity': 1,
                        'currency': 'inr',
                        'amount': str(amt),
                    }
                ]
            )
            table_pending.delete_item(
                Key={
                    'transaction_id':trans_id
                }
            )
            print(checkout_session)
            return JsonResponse({'sessionId': checkout_session['id']})
        except Exception as e:
            return JsonResponse({'error': str(e)})



def success(request,session_id,trans_id):
    print(session_id)
    print(trans_id)
    dynamodb = boto3.resource('dynamodb')
    table_balance = dynamodb.Table('Balances')
    balance = table_balance.scan(
        FilterExpression=Attr('email').eq(request.session['email'])
    )
    balance_user = int(balance['Items'][0]['balance'])

    table_transaction= dynamodb.Table('transactions')
    pending_redeems = table_balance.scan(
        FilterExpression=Attr('email').eq(request.session['email'])
    )['Items']
    stripe.api_key = settings.STRIPE_SECRET_KEY
    x = stripe.checkout.Session.retrieve(session_id)
    print(x['display_items'][0]['amount'])
    table_transaction.put_item(
        Item={
            'transaction_id':trans_id,
            'amount': int(x['display_items'][0]['amount']/100),
            'date': datetime.date.today().strftime('%B %d,%Y'),
            'time': datetime.datetime.now().time().strftime('%H:%M:%S'),
            'username': request.session['username'],
            'email': request.session['email'],
            'type':'credit'
        }
    )
    response = table_balance.update_item(
        Key={
            'email': request.session['email']
        },
        UpdateExpression="set balance = :r",
        ExpressionAttributeValues={
            ':r':int(balance_user) +  int(x['display_items'][0]['amount']/100),

        },
        ReturnValues="UPDATED_NEW"
    )
    return render(request,'credits/success.html')
def cancel(request):
    dynamodb = boto3.resource('dynamodb')
    table_balance = dynamodb.Table('Balances')
    ids = table_balance.scan(
        FilterExpression=Attr('email').eq(request.session['email'])

    )['Items']
    if not ids:
        ids = table_balance.scan()['Items']
        all_idds = [int(i['id']) for i in ids]
        print(all_idds)
        id = max(all_idds)+1
        table_balance.put_item(
            Item={
                'email':request.session['email'],
                'balance':0,
                'id':id,
                'user':request.session['username']
            }
        )
    else:
        print('yes balance')
    return render(request,'credits/cancelled.html')

def transactions(request):
    dynamodb = boto3.resource('dynamodb')
    table_transactions = dynamodb.Table('transactions')
    transactions = table_transactions.scan(
        FilterExpression=Attr('email').eq(request.session['email'])
    )['Items']
    # print(transactions)
    return render(request,'credits/transaction.html',{'context':transactions})