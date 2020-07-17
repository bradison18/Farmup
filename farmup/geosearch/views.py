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
import pgeocode
from geopy.distance import geodesic
import json
from geopy.geocoders import Nominatim

def gmaps(request):
    if is_loggedin(request):
        email = request.session['email']
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('user')
        response = table.scan(FilterExpression=Attr('email').eq(email))
        if (len(response['Items']) != 0):
            user = response['Items'][0]
        else:
            user = None
        address = user['address']
        geolocator = Nominatim(user_agent="farmup")
        location = geolocator.geocode(address)
        center = (location.latitude, location.longitude)
        locs = [(16.325369,80.423197),(16.333173,80.420688),(16.321788,80.412736),(16.312505, 80.427527),(16.311515,80.441133)]
        display_lands = []
        for land in locs:
            dist = geodesic(center,land).kilometers
            lat = land[0]
            lng = land[1]
            display_lands.append({'lat':lat,'lng':lng,'dist':dist})

        return render(request,'geosearch/g_search.html',{'lat':location.latitude,'lng':location.longitude,'display_lands':json.dumps(display_lands)})
    else:
        return redirect('home')