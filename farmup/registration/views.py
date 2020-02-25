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

def landing(request):
    if request.method == 'POST':
        print(request.POST)
    return render(request, 'index.html')


def about(request):
    return render(request, 'about.html')


def timeline(request):
    return render(request, 'timeline.html')


def auth(request):
    return render(request, 'auth.html')


def login(request):
    # if request.method == 'POST':
    email = request.POST.get('email')
    password = request.POST.get('password')
    password = hashlib.sha256(password.encode())
    password = password.hexdigest()

    dynamodb = boto3.resource('dynamodb')
    if (email != '' and password != ''):
        table = dynamodb.Table('user')
        response = table.scan(FilterExpression=Attr('email').eq(email))
        if (len(response['Items']) > 0):
            if (response['Items'][0]['password'] == password):

                request.session['username'] = response['Items'][0]['username']
                request.session['email'] = response['Items'][0]['email']
                print(request.session['username'], request.session['email'])

                return redirect('landing')
            else:
                messages.success(request, 'Failed to login as the password does not match.')
                return redirect('auth')
        else:
            messages.success(request, 'Failed to login as the email ID is not registered.')
            return redirect('auth')
    else:
        messages.success(request, 'Failed to login as the email or password is provided empty')
        return redirect('auth')


def register(request):
    username = request.POST.get('username')
    email = request.POST.get('email')
    password = request.POST.get('password')
    re_password = request.POST.get('repassword')

    if (username != '' and email != '' and password != '' and re_password != ''):
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

                # request.session['username'] = username
                # request.session['email'] = email
                #
                # return redirect('landing')
                current_site = get_current_site(request)
                mail_subject = 'Activate your account.'
                message = render_to_string('registration/acc_active_email.html', {
                    'user': username,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(username)).decode(),
                    'token': account_activation_token.make_token(username),
                })

                send_mail(mail_subject, message, 'iiits2021@gmail.com', [email])
                return render(request, 'login/email_confirmation.html')


            else:
                messages.success(request, 'The email ID is already registerd')
                return redirect('auth')
        else:
            messages.success(request, 'Failed to register as the password and confirm password do not match')
            return redirect('auth')
    else:
        messages.success(request, 'Fill all the fields')
        return redirect('auth')


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        print(uid)
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return redirect('registration:course_selection')

    else:
        return HttpResponse('Activation link is invalid!')
