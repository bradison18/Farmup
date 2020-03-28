from django.shortcuts import render
import boto3
from boto3.dynamodb.conditions import Key, Attr
from django.http import HttpResponse
import hashlib
from django.shortcuts import render, redirect
from rest_framework.response import Response
from rest_framework import status
from django.contrib import sessions
from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .tokens import account_activation_token
from django.core.mail import send_mail

def home(request):
    user = {}
    return render(request, 'registration/index.html',user)

def register_display(request):
    return render(request, 'registration/registration.html')

def test(request):
    return render(request, 'registration/test.html')

def login_display(request):
    return render(request, 'registration/login.html')


def dashboard(request):
    try:
        if request.session['email']:
            user = {'username':request.session['username'],'email':request.session['email']}
            return render(request,'registration/index.html',user)
    except:
        return redirect('home')

def login(request):
    # if request.method == 'POST':
    email = request.POST.get('email')
    password = request.POST.get('password')
    password = hashlib.sha256(password.encode())
    password = password.hexdigest()
    print(email)
    dynamodb = boto3.resource('dynamodb')
    if (email != '' and password != ''):
        table = dynamodb.Table('user')
        response = table.scan(FilterExpression=Attr('email').eq(email))
        if (len(response['Items']) > 0):
            if (response['Items'][0]['password'] == password):
                if (response['Items'][0]['is_active']):
                    request.session['username'] = response['Items'][0]['username']
                    request.session['email'] = response['Items'][0]['email']
                    print(request.session['username'], request.session['email'])

                    return redirect('landing')
                else:
                    messages.success(request, 'User not activated please confirm the email')
                    return redirect('registration:login_display')
            else:
                messages.success(request, 'Failed to login as the password does not match.')
                return redirect('registration:login_display')
        else:
            messages.success(request, 'Failed to login as the email ID is not registered.')
            return redirect('registration:login_display')
    else:
        messages.success(request, 'Failed to login as the email or password is provided empty')
        return redirect('registration:login_display')


def register(request):
    username = request.POST.get('username')
    email = request.POST.get('email')
    password = request.POST.get('password')
    re_password = request.POST.get('repassword')

    if (username  and email and password  and re_password ):
        if (password == re_password):

            dynamodb = boto3.resource('dynamodb')
            table = dynamodb.Table('user')

            response = table.scan(
                ProjectionExpression="email",
                FilterExpression=Attr('email').eq(email)
            )
            password = hashlib.sha256(password.encode())
            password = password.hexdigest()

            if (len(response['Items']) == 0):
                response = table.put_item(
                    Item={
                        'username': username,
                        'email': email,
                        'password': password,
                        'is_active': False,
                    }
                )


                current_site = get_current_site(request)
                mail_subject = 'Activate your account.'
                message = render_to_string('registration/acc_active_email.html', {
                    'user': username,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(email)).decode(),
                    'token': account_activation_token.make_token(email),
                })

                send_mail(mail_subject, message, 'tripplanneread@gmail.com', [email])
                return render(request, 'registration/email_confirmation.html')


            else:
                messages.success(request, 'The email ID is already registerd')
                return redirect('registration:register_display')
        else:
            messages.success(request, 'Failed to register as the password and confirm password do not match')
            return redirect('registration:register_display')
    else:
        messages.success(request, 'Fill all the fields')
        return redirect('registration:register_display')


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        print(uid)
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('user')

        response = table.scan(
            FilterExpression=Attr('email').eq(uid)
        )
        if (len(response['Items']) != 0):
            user = response['Items'][0]
    except(TypeError, ValueError, OverflowError):
        user = None
    if user is not None and account_activation_token.check_token(user['email'], token):

        response = table.update_item(
            Key={
                'email': user['email'],
            },
            UpdateExpression="set is_active = :r",
            ExpressionAttributeValues={
                ':r': True
            },
            ReturnValues="UPDATED_NEW"
        )
        request.session['username'] = user['username']
        request.session['email'] = user['email']
        return redirect('landing')

    else:
        return HttpResponse('Activation link is invalid!')

def logout(request):
    try:
        request.session.flush()
        return redirect('home')
    except:
        return redirect('home')




def reset_display(request):
    return render(request,'registration/reset_form.html',{})


def reset_password(request):
    email = request.POST.get('email')
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('user')
    users = table.scan(FilterExpression=Attr('email').eq(email))
    if(len(users['Items'])!=0):
        user = users['Items'][0]
        current_site = get_current_site(request)
        mail_subject = 'Password Reset Link.'
        message = render_to_string('registration/reset_confirm_email.html', {
            'user': user['username'],
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(user['email'])).decode(),
            'token': account_activation_token.make_token(user['email']),
        })
        send_mail(mail_subject, message, 'tripplanneread@gmail.com', [email])
        return render(request, 'registration/email_confirmation.html',{})
    else:
        messages.success(request, 'The email ID is not registerd')
        return redirect('registration:reset_display')

def verify_reset_password(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        print(uid)
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('user')
        users = table.scan(FilterExpression=Attr('email').eq(uid))
        if(len(users['Items'])!=0):
            user = users['Items'][0]
    except(TypeError, ValueError, OverflowError):
        user = None
    if user is not None and account_activation_token.check_token(user['email'], token):
        # login(request, user)
        request.session['email'] = user['email']
        return render(request,'registration/save_password.html',{})
    else:
        return HttpResponse('Activation link is invalid!')


def save_password(request):
    email = request.session['email']
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('user')
    users = table.scan(FilterExpression=Attr('email').eq(email))
    user = users['Items'][0]
    new_password  = request.POST.get('password')
    password = hashlib.sha256(new_password.encode())
    password = password.hexdigest()
    response = table.update_item(
        Key={
            'email': user['email'],
        },
        UpdateExpression="set password = :r, is_active = :t",
        ExpressionAttributeValues={
            ':r': password,
            ':t':True,
        },
        ReturnValues="UPDATED_NEW"
    )

    return redirect('registration:logout')