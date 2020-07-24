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
        address = request.POST.get('address')

        geolocator = Nominatim(user_agent="farmup01")
        location = geolocator.geocode(address)
        print(location)
        center = (location.latitude, location.longitude)
        new_location = geolocator.reverse(str(location.latitude)+','+str(location.longitude), exactly_one=True)
        address = new_location.raw['address']
        print(address)
        city = address.get('city', '')
        state = address.get('state', '')
        if not city:
            city = address.get('village', '')
        if not city:
            city = address.get('town', '')

        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('LandInfo')
        response = table.scan(FilterExpression=Attr('city').eq(city))

        if (len(response['Items'])>0):
            locs = response['Items'];
            display_lands = []
            for land in locs:
                position = (float(land['latitude']),float(land['longitude']))
                dist = geodesic(center,position).kilometers
                lat = position[0]
                lng = position[1]

                display_lands.append({'lat':lat,'lng':lng,'dist':dist,'land_id':land['land_id']})
            print(display_lands)
            return render(request,'geosearch/g_search.html',{'lat':center[0],'lng':center[1],'display_lands':json.dumps(display_lands)})
    else:
        return redirect('registration:login_display')

def get_address(request):
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
        return render(request,'geosearch/auto_complete.html',{'address':address})
    else:
        return redirect('registration:login_display')