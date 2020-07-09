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
from registration.login_required import is_loggedin

def gmaps(request):
    if is_loggedin(request):
        return render(request,'geosearch/mapper.html',{})
    else:
        return redirect('home')