<<<<<<< HEAD


# Create your views here.
from django.shortcuts import render
import boto3
from boto3.dynamodb.conditions import Key, Attr
from django.http import HttpResponse
import hashlib
from django.shortcuts import render, redirect
from geopy.geocoders import Nominatim
from registration.login_required import is_loggedin


#from rest_framework.response import Response

def farmersearch(request):
	#land_area=250
	if request.method=="POST":
		if request.POST.get('wages_description') !='':
			wages_description=int(request.POST.get('wages_description'))
		else:
			wages_description=None
		if request.POST.get('land_pin_code') !='':
			land_pin_code=request.POST.get('land_pin_code')
		else:
			land_pin_code=None

		
		#isa=True
		type_of_crop=request.POST.get('type_of_crop')
		dynamodb = boto3.resource('dynamodb',
		aws_access_key_id='AKIAJIJIVDPBPUMLU37Q',
		aws_secret_access_key='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',
		region_name='ap-south-1')
		dynamodb_client=boto3.client('dynamodb',aws_access_key_id='AKIAJIJIVDPBPUMLU37Q',
		aws_secret_access_key='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',region_name='ap-south-1')
		email=request.session['email']
		table=dynamodb.Table('user')
		response=table.scan(FilterExpression=Attr('email').eq(email))
		user_id=response['Items'][0]['farmer_id']
		table=dynamodb.Table('LandInfo')
		"""uid=table.scan(AttributesToGet=['username'])
		uid=uid['Items']
		flag=0
		s=[]
		for i in range(len(uid)): 
			response = table.scan(FilterExpression=Attr('email').eq(email) & Attr('username').eq(uid[i]['username']) & Attr('password').eq(password) & Attr('is_active').eq(isa))
			if len(response['Items'])> 0:
			#print(uid[i]['username'])
				flag=1
				if response['Items'] not in s:
					s.append(response['Items'])
		#print(s)
		if flag==0:
			print(response)
		"""
		#print(table.scan(AttributesToGet=['username']))
		is_active=True
		#user_id="1e25388fde8290dc286a6164fa2d97e551b53498dcbf7bc378eb1f178"
		


		if land_pin_code !=None and type_of_crop !="" and wages_description !=None:
			response = table.scan(FilterExpression= Attr('wages_description').gt(wages_description-1) & Attr('type_of_crop').eq(type_of_crop) & Attr('land_pin_code').eq(land_pin_code))
		elif land_pin_code !=None and type_of_crop !="":
			response = table.scan(FilterExpression= Attr('type_of_crop').eq(type_of_crop) & Attr('land_pin_code').eq(land_pin_code))
		elif type_of_crop !="" and wages_description !=None:
			response = table.scan(FilterExpression= Attr('wages_description').gt(wages_description-1) & Attr('type_of_crop').eq(type_of_crop))
		elif land_pin_code !=None and wages_description !=None:
			response = table.scan(FilterExpression= Attr('wages_description').gt(wages_description-1) &  Attr('land_pin_code').eq(land_pin_code))
		elif land_pin_code!=None:
			response = table.scan(FilterExpression= Attr('land_pin_code').eq(land_pin_code))
		elif type_of_crop!="":
			response = table.scan(FilterExpression= Attr('type_of_crop').eq(type_of_crop))
		elif wages_description!=None:
			response = table.scan(FilterExpression= Attr('wages_description').gt(wages_description-1))
		else:
			response=table.scan()
		#print(wages_description)
		#print(land_pin_code)
		#print(type_of_crop)
		d={}
		for i in range(len(response['Items'])):
			lid=response['Items'][i]['land_id']
			toc=response['Items'][i]['type_of_crop']
			wd=response['Items'][i]['wages_description']
			lpc=response['Items'][i]['land_pin_code']
			la=response['Items'][i]['land_area']
			tos=response['Items'][i]['type_of_soil']
			#print(wd)
			d[i]={'lid':lid,'toc':toc,'wd':wd,'lpc':lpc,'la':la,'tos':tos,'uid':user_id}
		#print(d)
		return render(request,'farmerandlandlord/displayland.html',{'d':d})

def filterfarmer(request):  
	return render(request,"farmerandlandlord/farmersearch.html") 
def farmerrequest(request,land_id,user_id):
	dynamodb = boto3.resource('dynamodb',
	aws_access_key_id='AKIAJIJIVDPBPUMLU37Q',
	aws_secret_access_key='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',
	region_name='ap-south-1')
	dynamodb_client=boto3.client('dynamodb',aws_access_key_id='AKIAJIJIVDPBPUMLU37Q',
	aws_secret_access_key='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',region_name='ap-south-1')
	table=dynamodb.Table('FarmerRequest')
	table2=dynamodb.Table('FarmerInfo')
	response=table2.scan(FilterExpression=Attr('farmer_id').eq(user_id))
	print(user_id)
	print(response)
	if response['Count']==0 or response['Items'][0]['land_working']=="":
		table.put_item(Item={
						"user_id":user_id,
						"land_id":land_id
					})
	return redirect('farmerandlandlord:dashboardfarmer')
def acceptrequest(request,land_id,user_id,username):
	dynamodb = boto3.resource('dynamodb',
	aws_access_key_id='AKIAJIJIVDPBPUMLU37Q',
	aws_secret_access_key='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',
	region_name='ap-south-1')
	dynamodb_client=boto3.client('dynamodb',aws_access_key_id='AKIAJIJIVDPBPUMLU37Q',
	aws_secret_access_key='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',region_name='ap-south-1')
	table=dynamodb.Table('FarmerInfo')
	response=table.scan(FilterExpression=Attr('farmer_id').eq(user_id))
	if response['Count']==0:
		table.put_item(Item={
						"farmer_id":user_id,
						"username":username,
						"lands_worked":{0},
						"land_working":land_id
					})
	if response['Count']==1:
		table.put_item(Item={
						"farmer_id":user_id,
						"username":username,
						"lands_worked":response['Items'][0]['lands_worked'],
						"land_working":land_id
					})

	table=dynamodb.Table('FarmerRequest')
	response=table.scan(FilterExpression= Attr('user_id').eq(user_id))
	for i in range(response['Count']):
		land_id=response['Items'][i]['land_id']
		table.delete_item(
			Key={
			'user_id':user_id,
			'land_id':land_id
			})
	table=dynamodb.Table('LandInfo')
	response=table.scan(FilterExpression= Attr('land_id').eq(land_id))
	if response['Items'][0]['farmers_working']=={0}:
		a=set()
		b={user_id}
		table.put_item(Item={
					  "is_active": response['Items'][0]['is_active'],
					  "land_area": response['Items'][0]['land_area'],
					  "land_id": response['Items'][0]['land_id'],
					  "land_pin_code": response['Items'][0]['land_pin_code'],
					  "type_of_crop": response['Items'][0]['type_of_crop'],
					  "type_of_soil": response['Items'][0]['type_of_soil'],
					  "wages_description": int(response['Items'][0]['wages_description']),
					  "latitude": response['Items'][0]['latitude'],
					  "longitude": response['Items'][0]['longitude'],
					  "city":response['Items'][0]['city'],
					  "state":response['Items'][0]['state'],
					  "farmers_working":a|b
					})
	else:
		a={response['Items'][0]['farmers_working']}
		b={user_id}
		table.put_item(Item={
					  "is_active": response['Items'][0]['is_active'],
					  "land_area": response['Items'][0]['land_area'],
					  "land_id": response['Items'][0]['land_id'],
					  "land_pin_code": response['Items'][0]['land_pin_code'],
					  "type_of_crop": response['Items'][0]['type_of_crop'],
					  "type_of_soil": response['Items'][0]['type_of_soil'],
					  "wages_description": int(response['Items'][0]['wages_description']),
					  "latitude": response['Items'][0]['latitude'],
					  "longitude": response['Items'][0]['longitude'],
					  "city":response['Items'][0]['city'],
					  "state":response['Items'][0]['state'],
					  "farmers_working":a|b
					})

				
	return redirect('farmerandlandlord:dashboardlandlord')

def formaddland(request):  
	return render(request,"farmerandlandlord/formaddland.html")
def addland(request):
	dynamodb = boto3.resource('dynamodb',
	aws_access_key_id='AKIAJIJIVDPBPUMLU37Q',
	aws_secret_access_key='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',
	region_name='ap-south-1')
	dynamodb_client=boto3.client('dynamodb',aws_access_key_id='AKIAJIJIVDPBPUMLU37Q',
	aws_secret_access_key='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',region_name='ap-south-1')
	table=dynamodb.Table('LandInfo')
	response=table.scan()
	if request.method=="POST":
		if table.scan()['Count']==0:
			land_id=table.scan()['Count'] + 1
		else:
			m=0
			for i in range(response['Count']):
				if int(response['Items'][i]['land_id'])>m:
					m=int(response['Items'][i]['land_id'])
			land_id=m+1
		wages=request.POST.get('wages_description')
		type_of_crop=request.POST.get('type_of_crop')
		type_of_soil=request.POST.get('type_of_soil')
		land_area=request.POST.get('land_area')
		land_pin_code=request.POST.get('land_pin_code')
		latitude=request.POST.get('lat')
		longitude=request.POST.get('long')
		is_active=False
	
	
		
		geolocator = Nominatim(user_agent="bobo")
		location = geolocator.reverse(str(latitude) +","+ str(longitude),exactly_one=True)
		address = location.raw['address']
		city = address.get('city','')
		state = address.get('state','')
		pin = address.get('postcode','')
		if not city:
			city = address.get('village','')
		print(str(latitude) +","+ str(longitude))
		print(city)
		print(address)
		if address and city:
			table.put_item(Item={
			  "is_active": is_active,
			  "land_area": land_area,
			  "land_id": str(land_id),
			  "land_pin_code": land_pin_code,
			  "type_of_crop": type_of_crop,
			  "type_of_soil": type_of_soil,
			  "wages_description": int(wages),
			  "latitude": latitude,
			  "longitude": longitude,
			  "city":city,
			  "state":state,
			  "farmers_working":{0}
			})
			email=request.session['email']
			table=dynamodb.Table('user')
			response=table.scan(FilterExpression=Attr('email').eq(email))
			land_lord_id=response['Items'][0]['land_lord_id']
			land_lord_name=response['Items'][0]['username']
			table=dynamodb.Table('Landlord')
			response=table.scan(FilterExpression=Attr('land_lord_id').eq(land_lord_id))
			#land_lord_name=response['Items'][0]['land_lord_name']
			#response=table.scan()
			if response['Count']>0:
				a=response['Items'][0]['lands_owned']
				print(a)
			else:
				a=set()
			b={land_id}
			print(a|b)
			table.put_item(Item={
				"land_lord_id": land_lord_id,
				"land_lord_name":land_lord_name ,
				#"lands_owned":"{" + str(response['Items'][0]['lands_owned'])+"," + str(land_id) + "}"
				"lands_owned":a|b
			})

	
	return redirect('farmerandlandlord:dashboardlandlord')
def formeditland(request,land_id):  
	return render(request,"farmerandlandlord/formeditland.html",{'land_id':land_id})
def editland(request,land_id):
	dynamodb = boto3.resource('dynamodb',
	aws_access_key_id='AKIAJIJIVDPBPUMLU37Q',
	aws_secret_access_key='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',
	region_name='ap-south-1')
	dynamodb_client=boto3.client('dynamodb',aws_access_key_id='AKIAJIJIVDPBPUMLU37Q',
	aws_secret_access_key='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',region_name='ap-south-1')
	table=dynamodb.Table('LandInfo')
	response=table.scan(FilterExpression=Attr('land_id').eq(land_id))
	if request.method=="POST":
		wages=request.POST.get('wages_description')
		type_of_crop=request.POST.get('type_of_crop')
	table.put_item(Item={
				  "is_active": response['Items'][0]['is_active'],
				  "land_area": response['Items'][0]['land_area'],
				  "land_id": response['Items'][0]['land_id'],
				  "land_pin_code": response['Items'][0]['land_pin_code'],
				  "type_of_crop": type_of_crop,
				  "type_of_soil": response['Items'][0]['type_of_soil'],
				  "wages_description": int(wages),
				  "latitude": response['Items'][0]['latitude'],
				  "longitude": response['Items'][0]['longitude'],
				  "city":response['Items'][0]['city'],
				  "state":response['Items'][0]['state'],
				  "farmers_working":response['Items'][0]['farmers_working']
			})
	return redirect('farmerandlandlord:dashboardlandlord')


def deleteland(request,land_id):
	dynamodb = boto3.resource('dynamodb',
	aws_access_key_id='AKIAJIJIVDPBPUMLU37Q',
	aws_secret_access_key='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',
	region_name='ap-south-1')
	dynamodb_client=boto3.client('dynamodb',aws_access_key_id='AKIAJIJIVDPBPUMLU37Q',
	aws_secret_access_key='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',region_name='ap-south-1')
	email=request.session['email']
	table=dynamodb.Table('user')
	response=table.scan(FilterExpression=Attr('email').eq(email))
	land_lord_id=response['Items'][0]['land_lord_id']
	table=dynamodb.Table('LandInfo')
	#table.delete_item(
	#	Key={
	#	'land_id':land_id
	#	})
	table=dynamodb.Table('Landlord')
	response=table.scan(FilterExpression=Attr('land_lord_id').eq(land_lord_id))
	#for i in range(len(response['Items'])):
	lands_owned=response['Items'][0]['lands_owned']
	land_lord_name=response['Items'][0]['land_lord_name']
	land_lord_id=response['Items'][0]['land_lord_id']
	#print(lands_owned)
	print(land_id)
	if int(land_id) in lands_owned:
		lands_owned.remove(int(land_id))
		print(lands_owned)
		if len(lands_owned)==0:
			table.delete_item(
				Key={
				'land_lord_id':land_lord_id
				})
		#else:
			#table.put_item(Item={
			#	"land_lord_id": land_lord_id,
			#	"land_lord_name":land_lord_name ,
				#"lands_owned":"{" + str(response['Items'][0]['lands_owned'])+"," + str(land_id) + "}"
			#	"lands_owned":lands_owned
			#})

	table=dynamodb.Table('FarmerInfo')
	response=table.scan(FilterExpression=Attr('land_working').eq(land_id))
	for i in range(response['Count']):
		
		if response['Items'][i]['lands_worked']=={0}:
			a=set()
			b={int(response['Items'][i]['land_working'])}
		else:
			a=response['Items'][i]['lands_worked']
			b={int(response['Items'][i]['land_working'])}
		table.put_item(Item={
					"farmer_id":response['Items'][i]['farmer_id'],
					"username":response['Items'][i]['username'],
					"lands_worked":a|b,
					"land_working":""})
	return redirect('farmerandlandlord:dashboardlandlord')
def leaveland(request,lwg):
	dynamodb = boto3.resource('dynamodb',
	aws_access_key_id='AKIAJIJIVDPBPUMLU37Q',
	aws_secret_access_key='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',
	region_name='ap-south-1')
	dynamodb_client=boto3.client('dynamodb',aws_access_key_id='AKIAJIJIVDPBPUMLU37Q',
	aws_secret_access_key='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',region_name='ap-south-1')
	#farmer_id="1e25388fde8290dc286a6164fa2d97e551b53498dcbf7bc378eb1f178"
	email=request.session['email']
	table=dynamodb.Table('user')
	response=table.scan(FilterExpression=Attr('email').eq(email))
	farmer_id=response['Items'][0]['farmer_id']
	table=dynamodb.Table('FarmerInfo')
	response=table.scan(FilterExpression=Attr('farmer_id').eq(farmer_id))
	if response['Items'][0]['lands_worked']=={0}:
		a=set()
		b={int(response['Items'][0]['land_working'])}
	else:
		a=response['Items'][0]['lands_worked']
		b={int(response['Items'][0]['land_working'])}
	table.put_item(Item={
				"farmer_id":response['Items'][0]['farmer_id'],
				"username":response['Items'][0]['username'],
				"lands_worked":a|b,
				"land_working":""})
	table=dynamodb.Table('LandInfo')
	response=table.scan(FilterExpression=Attr('land_id').eq(lwg))
	farmers_working=response['Items'][0]['farmers_working']
		
		#print(lands_owned)
	if farmer_id in farmers_working:
		farmers_working.remove(farmer_id)
		print(farmers_working)
		if len(farmers_working)==0:
			table.put_item(Item={
				  "is_active": response['Items'][0]['is_active'],
				  "land_area": response['Items'][0]['land_area'],
				  "land_id": response['Items'][0]['land_id'],
				  "land_pin_code": response['Items'][0]['land_pin_code'],
				  "type_of_crop": response['Items'][0]['type_of_crop'],
				  "type_of_soil": response['Items'][0]['type_of_soil'],
				  "wages_description": int(response['Items'][0]['wages_description']),
				  "latitude": response['Items'][0]['latitude'],
				  "longitude": response['Items'][0]['longitude'],
				  "city":response['Items'][0]['city'],
				  "state":response['Items'][0]['state'],
				  "farmers_working":{0}
			})

			
		else:
			table.put_item(Item={
				  "is_active": response['Items'][0]['is_active'],
				  "land_area": response['Items'][0]['land_area'],
				  "land_id": response['Items'][0]['land_id'],
				  "land_pin_code": response['Items'][0]['land_pin_code'],
				  "type_of_crop": response['Items'][0]['type_of_crop'],
				  "type_of_soil": response['Items'][0]['type_of_soil'],
				  "wages_description": int(response['Items'][0]['wages_description']),
				  "latitude": response['Items'][0]['latitude'],
				  "longitude": response['Items'][0]['longitude'],
				  "city":response['Items'][0]['city'],
				  "state":response['Items'][0]['state'],
				  "farmers_working":farmers_working
			})


	return redirect('farmerandlandlord:dashboardfarmer')
	
def infoland(request,land_id):
	#print(param)
	dynamodb = boto3.resource('dynamodb',
	aws_access_key_id='AKIAJIJIVDPBPUMLU37Q',
	aws_secret_access_key='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',
	region_name='ap-south-1')
	dynamodb_client=boto3.client('dynamodb',aws_access_key_id='AKIAJIJIVDPBPUMLU37Q',
	aws_secret_access_key='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',region_name='ap-south-1')
	table=dynamodb.Table('LandInfo')
	response=table.scan(FilterExpression=Attr('land_id').eq(land_id))
	d={}
	lid=response['Items'][0]['land_id']
	toc=response['Items'][0]['type_of_crop']
	wd=response['Items'][0]['wages_description']
	lpc=response['Items'][0]['land_pin_code']
	la=response['Items'][0]['land_area']
	tos=response['Items'][0]['type_of_soil']
	lat=response['Items'][0]['latitude']
	logt=response['Items'][0]['longitude']
	city=response['Items'][0]['city']
	state=response['Items'][0]['state']
	farmers_working=response['Items'][0]['farmers_working']
	
	#print(wd)
	table=dynamodb.Table('Landlord')
	#AttributesToGet=['lands_owned']
	response=table.scan()
	#print(response)
	for i in range(len(response['Items'])):
		lands_owned=response['Items'][i]['lands_owned']
		#print(lands_owned)
		for x in lands_owned:
			#print(x)
			if str(x)==land_id:
				land_lord_name=response['Items'][i]['land_lord_name']
				#print(land_lord_name)
				break
	if farmers_working!={0}:
		table=dynamodb.Table('FarmerInfo')
		a=set()
		for x in farmers_working:
			response=table.scan(FilterExpression=Attr('farmer_id').eq(x))
			b={response['Items'][0]['username']}
			a=a|b	
		d={'lid':lid,'toc':toc,'wd':wd,'lpc':lpc,'la':la,'tos':tos,'lad':land_lord_name,'lat':lat,'lgt':logt,'city':city,'state':state,'a':a}
	else:
		d={'lid':lid,'toc':toc,'wd':wd,'lpc':lpc,'la':la,'tos':tos,'lad':land_lord_name,'lat':lat,'lgt':logt,'city':city,'state':state}

	return render(request,"farmerandlandlord/infoland.html",{'d':d})
def landlordsearch(request):
	dynamodb = boto3.resource('dynamodb',
	aws_access_key_id='AKIAJIJIVDPBPUMLU37Q',
	aws_secret_access_key='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',
	region_name='ap-south-1')
	dynamodb_client=boto3.client('dynamodb',aws_access_key_id='AKIAJIJIVDPBPUMLU37Q',
	aws_secret_access_key='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',region_name='ap-south-1')
	table=dynamodb.Table('user')
	farmer=True
	pincode='522006'
	response=table.scan(FilterExpression=Attr('is_farmer').eq(farmer) & Attr('pincode').eq(pincode))
	#print(response)
	l={}
	for i in range(len(response['Items'])):
		l[i]=response['Items'][i]['farmer_id']
	table=dynamodb.Table('FarmerInfo')
	print(l)
	d={}
	for j in range(len(l)):
		new=table.scan(FilterExpression=Attr('farmer_id').eq(l[j]))
		print(new)
		farmer_id=new['Items'][0]['farmer_id']
		farmer_name=new['Items'][0]['farmer_name']
		lands_worked=new['Items'][0]['lands_worked']
		d[j]={'farmer_id':farmer_id,'farmer_name':farmer_name,'lands_worked':lands_worked}
	print(d)
	return render(request,'farmerandlandlord/displayfarmer.html',{'d':d})
def dashboardlandlord(request):
	dynamodb = boto3.resource('dynamodb',
	aws_access_key_id='AKIAJIJIVDPBPUMLU37Q',
	aws_secret_access_key='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',
	region_name='ap-south-1')
	dynamodb_client=boto3.client('dynamodb',aws_access_key_id='AKIAJIJIVDPBPUMLU37Q',
	aws_secret_access_key='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',region_name='ap-south-1')
	if is_loggedin(request):
		email=request.session['email']
		table=dynamodb.Table('user')
		response=table.scan(FilterExpression=Attr('email').eq(email))
		land_lord_id=response['Items'][0]['land_lord_id']
		table=dynamodb.Table('Landlord')
		#land_lord_id="2e25388fde8290dc286a6164fa2d97e551b53498dcbf7bc378eb1f1780"
		
		#pincode=522006
		response=table.scan(FilterExpression=Attr('land_lord_id').eq(land_lord_id))
		if response['Count']==1:
			lands_owned=response['Items'][0]['lands_owned']
			d={}
			table=dynamodb.Table('LandInfo')
			for k in lands_owned:
				new2=table.scan(FilterExpression=Attr('land_id').eq(str(k)))
				#print(new2)
				if new2['Count']==1:
					lid=new2['Items'][0]['land_id']
					toc=new2['Items'][0]['type_of_crop']
					wd=new2['Items'][0]['wages_description']
					lpc=new2['Items'][0]['land_pin_code']
					la=new2['Items'][0]['land_area']
					tos=new2['Items'][0]['type_of_soil']
					d[k]={'lid':lid,'toc':toc,'wd':wd,'lpc':lpc,'la':la,'tos':tos}
			#print(d)
			return render(request,'farmerandlandlord/dashboardlandlord.html',{'d':d})
		else:
			return render(request,'farmerandlandlord/dashboardlandlord.html')
	else:
		return redirect('registration:login_display')
def dashboardfarmer(request):
	dynamodb = boto3.resource('dynamodb',
	aws_access_key_id='AKIAJIJIVDPBPUMLU37Q',
	aws_secret_access_key='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',
	region_name='ap-south-1')
	dynamodb_client=boto3.client('dynamodb',aws_access_key_id='AKIAJIJIVDPBPUMLU37Q',
	aws_secret_access_key='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',region_name='ap-south-1')
	#farmer_id="1e25388fde8290dc286a6164fa2d97e551b53498dcbf7bc378eb1f178"
	if is_loggedin(request):
		email=request.session['email']
		table=dynamodb.Table('user')
		response=table.scan(FilterExpression=Attr('email').eq(email))
		farmer_id=response['Items'][0]['farmer_id']
		table=dynamodb.Table('FarmerInfo')
		response=table.scan(FilterExpression=Attr('farmer_id').eq(farmer_id))
		#print(response)
		if response['Count']==1:
			land_id=response['Items'][0]['land_working']
			lands_worked=response['Items'][0]['lands_worked']
			#print(land_id)
			land_working=land_id
			table=dynamodb.Table('LandInfo')
			response=table.scan(FilterExpression=Attr('land_id').eq(land_id))
			#print(response)
			if land_id!="" and lands_worked=={0}:
				lid=response['Items'][0]['land_id']
				#print(lid)
				toc=response['Items'][0]['type_of_crop']
				wd=response['Items'][0]['wages_description']
				lpc=response['Items'][0]['land_pin_code']
				la=response['Items'][0]['land_area']
				tos=response['Items'][0]['type_of_soil']
				lat=response['Items'][0]['latitude']
				logt=response['Items'][0]['longitude']
				city=response['Items'][0]['city']
				state=response['Items'][0]['state']
				d={'lid':lid,'toc':toc,'wd':wd,'lpc':lpc,'la':la,'tos':tos,'lat':lat,'lgt':logt,'city':city,'state':state}
				#print(lands_worked)
				return render(request,'farmerandlandlord/dashboardfarmer.html',{'d':d,'lwg':land_working})
			if lands_worked!={0} and land_id=="":
				t={}
				for k in lands_worked:
					new2=table.scan(FilterExpression=Attr('land_id').eq(str(k)))
					#print(new2)
					if new2['Count']==1:
						lid=new2['Items'][0]['land_id']
						toc=new2['Items'][0]['type_of_crop']
						wd=new2['Items'][0]['wages_description']
						lpc=new2['Items'][0]['land_pin_code']
						la=new2['Items'][0]['land_area']
						tos=new2['Items'][0]['type_of_soil']
						t[k]={'lid':lid,'toc':toc,'wd':wd,'lpc':lpc,'la':la,'tos':tos}
						print(t)
				return render(request,'farmerandlandlord/dashboardfarmer.html',{'t':t,'lwg':land_working})

				#print(d)
			if lands_worked!={0} and land_id!="":
				lid=response['Items'][0]['land_id']
				#print(lid)
				toc=response['Items'][0]['type_of_crop']
				wd=response['Items'][0]['wages_description']
				lpc=response['Items'][0]['land_pin_code']
				la=response['Items'][0]['land_area']
				tos=response['Items'][0]['type_of_soil']
				lat=response['Items'][0]['latitude']
				logt=response['Items'][0]['longitude']
				city=response['Items'][0]['city']
				state=response['Items'][0]['state']
				d={'lid':lid,'toc':toc,'wd':wd,'lpc':lpc,'la':la,'tos':tos,'lat':lat,'lgt':logt,'city':city,'state':state}
				t={}
				for k in lands_worked:
					new2=table.scan(FilterExpression=Attr('land_id').eq(str(k)))
					#print(new2)
					if new2['Count']==1:
						lid=new2['Items'][0]['land_id']
						toc=new2['Items'][0]['type_of_crop']
						wd=new2['Items'][0]['wages_description']
						lpc=new2['Items'][0]['land_pin_code']
						la=new2['Items'][0]['land_area']
						tos=new2['Items'][0]['type_of_soil']
						t[k]={'lid':lid,'toc':toc,'wd':wd,'lpc':lpc,'la':la,'tos':tos}
						print(t)
				return render(request,'farmerandlandlord/dashboardfarmer.html',{'d':d,'t':t,'lwg':land_working})
				
		else:
			return render(request,'farmerandlandlord/dashboardfarmer.html')
	else:
		return redirect('registration:login_display')
def landlordviewrequest(request):
	dynamodb = boto3.resource('dynamodb',
	aws_access_key_id='AKIAJIJIVDPBPUMLU37Q',
	aws_secret_access_key='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',
	region_name='ap-south-1')
	dynamodb_client=boto3.client('dynamodb',aws_access_key_id='AKIAJIJIVDPBPUMLU37Q',
	aws_secret_access_key='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',region_name='ap-south-1')
	#land_lord_id="2e25388fde8290dc286a6164fa2d97e551b53498dcbf7bc378eb1f1780"
	email=request.session['email']
	table=dynamodb.Table('user')
	response=table.scan(FilterExpression=Attr('email').eq(email))
	land_lord_id=response['Items'][0]['land_lord_id']
	table=dynamodb.Table('FarmerRequest')
	response=table.scan()
	if response['Count']>0:
		l={}
		k={}
		for i in range(response['Count']):
			l[response['Items'][i]['land_id']]=1
			k[response['Items'][i]['user_id']]=1
		#print(l)
		table=dynamodb.Table('Landlord')
		response2=table.scan(FilterExpression=Attr('land_lord_id').eq(land_lord_id))
		d={}
		j=0
		table=dynamodb.Table('LandInfo')
		table3=dynamodb.Table('FarmerRequest')
		table2=dynamodb.Table('user')
		for i in response2['Items'][0]['lands_owned']:
			if str(i) in l:
				new2=table.scan(FilterExpression=Attr('land_id').eq(str(i)))
				response3=table3.scan(FilterExpression=Attr('land_id').eq(str(i)))
				uid=response3['Items'][0]['user_id']
				new=table2.scan(FilterExpression=Attr('farmer_id').eq(uid))
				un=new['Items'][0]['username']
				ue=new['Items'][0]['email']
				uadd=new['Items'][0]['address']
				uph=new['Items'][0]['phone_number']
				lid=i
				toc=new2['Items'][0]['type_of_crop']
				wd=new2['Items'][0]['wages_description']
				lpc=new2['Items'][0]['land_pin_code']
				la=new2['Items'][0]['land_area']
				tos=new2['Items'][0]['type_of_soil']
				d[j]={'uid':uid,'un':un,'ue':ue,'uadd':uadd,'uph':uph,'lid':lid,'toc':toc,'wd':wd,'lpc':lpc,'la':la,'tos':tos}
			j+=1
		print(d)
		
		#new=table2.scan(FilterExpression=Attr('farmer_id').eq())
		return render(request,'farmerandlandlord/displayfarmer.html',{'d':d})
	else:
		return render(request,'farmerandlandlord/displayfarmer.html')

		









	

		
	
	
	





	
=======


# Create your views here.
from django.shortcuts import render
import boto3
from boto3.dynamodb.conditions import Key, Attr
from django.http import HttpResponse
import hashlib
from django.shortcuts import render, redirect
from geopy.geocoders import Nominatim
from registration.login_required import is_loggedin


#from rest_framework.response import Response

def farmersearch(request):
	#land_area=250
	if request.method=="POST":
		if request.POST.get('wages_description') !='':
			wages_description=int(request.POST.get('wages_description'))
		else:
			wages_description=None
		if request.POST.get('land_pin_code') !='':
			land_pin_code=request.POST.get('land_pin_code')
		else:
			land_pin_code=None

		
		#isa=True
		type_of_crop=request.POST.get('type_of_crop')
		dynamodb = boto3.resource('dynamodb',
		aws_access_key_id='AKIAJIJIVDPBPUMLU37Q',
		aws_secret_access_key='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',
		region_name='ap-south-1')
		dynamodb_client=boto3.client('dynamodb',aws_access_key_id='AKIAJIJIVDPBPUMLU37Q',
		aws_secret_access_key='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',region_name='ap-south-1')
		email=request.session['email']
		table=dynamodb.Table('user')
		response=table.scan(FilterExpression=Attr('email').eq(email))
		user_id=response['Items'][0]['farmer_id']
		table=dynamodb.Table('LandInfo')
		"""uid=table.scan(AttributesToGet=['username'])
		uid=uid['Items']
		flag=0
		s=[]
		for i in range(len(uid)): 
			response = table.scan(FilterExpression=Attr('email').eq(email) & Attr('username').eq(uid[i]['username']) & Attr('password').eq(password) & Attr('is_active').eq(isa))
			if len(response['Items'])> 0:
			#print(uid[i]['username'])
				flag=1
				if response['Items'] not in s:
					s.append(response['Items'])
		#print(s)
		if flag==0:
			print(response)
		"""
		#print(table.scan(AttributesToGet=['username']))
		is_active=True
		#user_id="1e25388fde8290dc286a6164fa2d97e551b53498dcbf7bc378eb1f178"
		


		if land_pin_code !=None and type_of_crop !="" and wages_description !=None:
			response = table.scan(FilterExpression= Attr('wages_description').gt(wages_description-1) & Attr('type_of_crop').eq(type_of_crop) & Attr('land_pin_code').eq(land_pin_code))
		elif land_pin_code !=None and type_of_crop !="":
			response = table.scan(FilterExpression= Attr('type_of_crop').eq(type_of_crop) & Attr('land_pin_code').eq(land_pin_code))
		elif type_of_crop !="" and wages_description !=None:
			response = table.scan(FilterExpression= Attr('wages_description').gt(wages_description-1) & Attr('type_of_crop').eq(type_of_crop))
		elif land_pin_code !=None and wages_description !=None:
			response = table.scan(FilterExpression= Attr('wages_description').gt(wages_description-1) &  Attr('land_pin_code').eq(land_pin_code))
		elif land_pin_code!=None:
			response = table.scan(FilterExpression= Attr('land_pin_code').eq(land_pin_code))
		elif type_of_crop!="":
			response = table.scan(FilterExpression= Attr('type_of_crop').eq(type_of_crop))
		elif wages_description!=None:
			response = table.scan(FilterExpression= Attr('wages_description').gt(wages_description-1))
		else:
			response=table.scan()
		#print(wages_description)
		#print(land_pin_code)
		#print(type_of_crop)
		d={}
		for i in range(len(response['Items'])):
			lid=response['Items'][i]['land_id']
			toc=response['Items'][i]['type_of_crop']
			wd=response['Items'][i]['wages_description']
			lpc=response['Items'][i]['land_pin_code']
			la=response['Items'][i]['land_area']
			tos=response['Items'][i]['type_of_soil']
			#print(wd)
			d[i]={'lid':lid,'toc':toc,'wd':wd,'lpc':lpc,'la':la,'tos':tos,'uid':user_id}
		#print(d)
		return render(request,'farmerandlandlord/displayland.html',{'d':d})

def filterfarmer(request):  
	return render(request,"farmerandlandlord/farmersearch.html") 
def farmerrequest(request,land_id,user_id):
	dynamodb = boto3.resource('dynamodb',
	aws_access_key_id='AKIAJIJIVDPBPUMLU37Q',
	aws_secret_access_key='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',
	region_name='ap-south-1')
	dynamodb_client=boto3.client('dynamodb',aws_access_key_id='AKIAJIJIVDPBPUMLU37Q',
	aws_secret_access_key='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',region_name='ap-south-1')
	table=dynamodb.Table('FarmerRequest')
	table2=dynamodb.Table('FarmerInfo')
	response=table2.scan(FilterExpression=Attr('farmer_id').eq(user_id))
	print(user_id)
	print(response)
	if response['Count']==0 or response['Items'][0]['land_working']=="":
		table.put_item(Item={
						"user_id":user_id,
						"land_id":land_id
					})
	return redirect('farmerandlandlord:dashboardfarmer')
def acceptrequest(request,land_id,user_id,username):
	dynamodb = boto3.resource('dynamodb',
	aws_access_key_id='AKIAJIJIVDPBPUMLU37Q',
	aws_secret_access_key='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',
	region_name='ap-south-1')
	dynamodb_client=boto3.client('dynamodb',aws_access_key_id='AKIAJIJIVDPBPUMLU37Q',
	aws_secret_access_key='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',region_name='ap-south-1')
	table=dynamodb.Table('FarmerInfo')
	response=table.scan(FilterExpression=Attr('farmer_id').eq(user_id))
	if response['Count']==0:
		table.put_item(Item={
						"farmer_id":user_id,
						"username":username,
						"lands_worked":{0},
						"land_working":land_id
					})
	if response['Count']==1:
		table.put_item(Item={
						"farmer_id":user_id,
						"username":username,
						"lands_worked":response['Items'][0]['lands_worked'],
						"land_working":land_id
					})

	table=dynamodb.Table('FarmerRequest')
	response=table.scan(FilterExpression= Attr('user_id').eq(user_id))
	for i in range(response['Count']):
		land_id=response['Items'][i]['land_id']
		table.delete_item(
			Key={
			'user_id':user_id,
			'land_id':land_id
			})
	table=dynamodb.Table('LandInfo')
	response=table.scan(FilterExpression= Attr('land_id').eq(land_id))
	if response['Items'][0]['farmers_working']=={0}:
		a=set()
		b={user_id}
		table.put_item(Item={
					  "is_active": response['Items'][0]['is_active'],
					  "land_area": response['Items'][0]['land_area'],
					  "land_id": response['Items'][0]['land_id'],
					  "land_pin_code": response['Items'][0]['land_pin_code'],
					  "type_of_crop": response['Items'][0]['type_of_crop'],
					  "type_of_soil": response['Items'][0]['type_of_soil'],
					  "wages_description": int(response['Items'][0]['wages_description']),
					  "latitude": response['Items'][0]['latitude'],
					  "longitude": response['Items'][0]['longitude'],
					  "city":response['Items'][0]['city'],
					  "state":response['Items'][0]['state'],
					  "farmers_working":a|b
					})
	else:
		a={response['Items'][0]['farmers_working']}
		b={user_id}
		table.put_item(Item={
					  "is_active": response['Items'][0]['is_active'],
					  "land_area": response['Items'][0]['land_area'],
					  "land_id": response['Items'][0]['land_id'],
					  "land_pin_code": response['Items'][0]['land_pin_code'],
					  "type_of_crop": response['Items'][0]['type_of_crop'],
					  "type_of_soil": response['Items'][0]['type_of_soil'],
					  "wages_description": int(response['Items'][0]['wages_description']),
					  "latitude": response['Items'][0]['latitude'],
					  "longitude": response['Items'][0]['longitude'],
					  "city":response['Items'][0]['city'],
					  "state":response['Items'][0]['state'],
					  "farmers_working":a|b
					})

				
	return redirect('farmerandlandlord:dashboardlandlord')

def formaddland(request):  
	return render(request,"farmerandlandlord/formaddland.html")
def addland(request):
	dynamodb = boto3.resource('dynamodb',
	aws_access_key_id='AKIAJIJIVDPBPUMLU37Q',
	aws_secret_access_key='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',
	region_name='ap-south-1')
	dynamodb_client=boto3.client('dynamodb',aws_access_key_id='AKIAJIJIVDPBPUMLU37Q',
	aws_secret_access_key='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',region_name='ap-south-1')
	table=dynamodb.Table('LandInfo')
	response=table.scan()
	if request.method=="POST":
		if table.scan()['Count']==0:
			land_id=table.scan()['Count'] + 1
		else:
			m=0
			for i in range(response['Count']):
				if int(response['Items'][i]['land_id'])>m:
					m=int(response['Items'][i]['land_id'])
			land_id=m+1
		wages=request.POST.get('wages_description')
		type_of_crop=request.POST.get('type_of_crop')
		type_of_soil=request.POST.get('type_of_soil')
		land_area=request.POST.get('land_area')
		land_pin_code=request.POST.get('land_pin_code')
		latitude=request.POST.get('lat')
		longitude=request.POST.get('long')
		is_active=False
	
	
		
		geolocator = Nominatim(user_agent="bobo")
		location = geolocator.reverse(str(latitude) +","+ str(longitude),exactly_one=True)
		address = location.raw['address']
		city = address.get('city','')
		state = address.get('state','')
		pin = address.get('postcode','')
		if not city:
			city = address.get('village','')
		print(str(latitude) +","+ str(longitude))
		print(city)
		print(address)
		if address and city:
			table.put_item(Item={
			  "is_active": is_active,
			  "land_area": land_area,
			  "land_id": str(land_id),
			  "land_pin_code": land_pin_code,
			  "type_of_crop": type_of_crop,
			  "type_of_soil": type_of_soil,
			  "wages_description": int(wages),
			  "latitude": latitude,
			  "longitude": longitude,
			  "city":city,
			  "state":state,
			  "farmers_working":{0}
			})
			email=request.session['email']
			table=dynamodb.Table('user')
			response=table.scan(FilterExpression=Attr('email').eq(email))
			land_lord_id=response['Items'][0]['land_lord_id']
			land_lord_name=response['Items'][0]['username']
			table=dynamodb.Table('Landlord')
			response=table.scan(FilterExpression=Attr('land_lord_id').eq(land_lord_id))
			#land_lord_name=response['Items'][0]['land_lord_name']
			#response=table.scan()
			if response['Count']>0:
				a=response['Items'][0]['lands_owned']
				print(a)
			else:
				a=set()
			b={land_id}
			print(a|b)
			table.put_item(Item={
				"land_lord_id": land_lord_id,
				"land_lord_name":land_lord_name ,
				#"lands_owned":"{" + str(response['Items'][0]['lands_owned'])+"," + str(land_id) + "}"
				"lands_owned":a|b
			})

	
	return redirect('farmerandlandlord:dashboardlandlord')
def formeditland(request,land_id):  
	return render(request,"farmerandlandlord/formeditland.html",{'land_id':land_id})
def editland(request,land_id):
	dynamodb = boto3.resource('dynamodb',
	aws_access_key_id='AKIAJIJIVDPBPUMLU37Q',
	aws_secret_access_key='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',
	region_name='ap-south-1')
	dynamodb_client=boto3.client('dynamodb',aws_access_key_id='AKIAJIJIVDPBPUMLU37Q',
	aws_secret_access_key='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',region_name='ap-south-1')
	table=dynamodb.Table('LandInfo')
	response=table.scan(FilterExpression=Attr('land_id').eq(land_id))
	if request.method=="POST":
		wages=request.POST.get('wages_description')
		type_of_crop=request.POST.get('type_of_crop')
	table.put_item(Item={
				  "is_active": response['Items'][0]['is_active'],
				  "land_area": response['Items'][0]['land_area'],
				  "land_id": response['Items'][0]['land_id'],
				  "land_pin_code": response['Items'][0]['land_pin_code'],
				  "type_of_crop": type_of_crop,
				  "type_of_soil": response['Items'][0]['type_of_soil'],
				  "wages_description": int(wages),
				  "latitude": response['Items'][0]['latitude'],
				  "longitude": response['Items'][0]['longitude'],
				  "city":response['Items'][0]['city'],
				  "state":response['Items'][0]['state'],
				  "farmers_working":response['Items'][0]['farmers_working']
			})
	return redirect('farmerandlandlord:dashboardlandlord')


def deleteland(request,land_id):
	dynamodb = boto3.resource('dynamodb',
	aws_access_key_id='AKIAJIJIVDPBPUMLU37Q',
	aws_secret_access_key='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',
	region_name='ap-south-1')
	dynamodb_client=boto3.client('dynamodb',aws_access_key_id='AKIAJIJIVDPBPUMLU37Q',
	aws_secret_access_key='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',region_name='ap-south-1')
	email=request.session['email']
	table=dynamodb.Table('user')
	response=table.scan(FilterExpression=Attr('email').eq(email))
	land_lord_id=response['Items'][0]['land_lord_id']
	table=dynamodb.Table('LandInfo')
	#table.delete_item(
	#	Key={
	#	'land_id':land_id
	#	})
	table=dynamodb.Table('Landlord')
	response=table.scan(FilterExpression=Attr('land_lord_id').eq(land_lord_id))
	#for i in range(len(response['Items'])):
	lands_owned=response['Items'][0]['lands_owned']
	land_lord_name=response['Items'][0]['land_lord_name']
	land_lord_id=response['Items'][0]['land_lord_id']
	#print(lands_owned)
	print(land_id)
	if int(land_id) in lands_owned:
		lands_owned.remove(int(land_id))
		print(lands_owned)
		if len(lands_owned)==0:
			table.delete_item(
				Key={
				'land_lord_id':land_lord_id
				})
		#else:
			#table.put_item(Item={
			#	"land_lord_id": land_lord_id,
			#	"land_lord_name":land_lord_name ,
				#"lands_owned":"{" + str(response['Items'][0]['lands_owned'])+"," + str(land_id) + "}"
			#	"lands_owned":lands_owned
			#})

	table=dynamodb.Table('FarmerInfo')
	response=table.scan(FilterExpression=Attr('land_working').eq(land_id))
	for i in range(response['Count']):
		
		if response['Items'][i]['lands_worked']=={0}:
			a=set()
			b={int(response['Items'][i]['land_working'])}
		else:
			a=response['Items'][i]['lands_worked']
			b={int(response['Items'][i]['land_working'])}
		table.put_item(Item={
					"farmer_id":response['Items'][i]['farmer_id'],
					"username":response['Items'][i]['username'],
					"lands_worked":a|b,
					"land_working":""})
	return redirect('farmerandlandlord:dashboardlandlord')
def leaveland(request,lwg):
	dynamodb = boto3.resource('dynamodb',
	aws_access_key_id='AKIAJIJIVDPBPUMLU37Q',
	aws_secret_access_key='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',
	region_name='ap-south-1')
	dynamodb_client=boto3.client('dynamodb',aws_access_key_id='AKIAJIJIVDPBPUMLU37Q',
	aws_secret_access_key='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',region_name='ap-south-1')
	#farmer_id="1e25388fde8290dc286a6164fa2d97e551b53498dcbf7bc378eb1f178"
	email=request.session['email']
	table=dynamodb.Table('user')
	response=table.scan(FilterExpression=Attr('email').eq(email))
	farmer_id=response['Items'][0]['farmer_id']
	table=dynamodb.Table('FarmerInfo')
	response=table.scan(FilterExpression=Attr('farmer_id').eq(farmer_id))
	if response['Items'][0]['lands_worked']=={0}:
		a=set()
		b={int(response['Items'][0]['land_working'])}
	else:
		a=response['Items'][0]['lands_worked']
		b={int(response['Items'][0]['land_working'])}
	table.put_item(Item={
				"farmer_id":response['Items'][0]['farmer_id'],
				"username":response['Items'][0]['username'],
				"lands_worked":a|b,
				"land_working":""})
	table=dynamodb.Table('LandInfo')
	response=table.scan(FilterExpression=Attr('land_id').eq(lwg))
	farmers_working=response['Items'][0]['farmers_working']
		
		#print(lands_owned)
	if farmer_id in farmers_working:
		farmers_working.remove(farmer_id)
		print(farmers_working)
		if len(farmers_working)==0:
			table.put_item(Item={
				  "is_active": response['Items'][0]['is_active'],
				  "land_area": response['Items'][0]['land_area'],
				  "land_id": response['Items'][0]['land_id'],
				  "land_pin_code": response['Items'][0]['land_pin_code'],
				  "type_of_crop": response['Items'][0]['type_of_crop'],
				  "type_of_soil": response['Items'][0]['type_of_soil'],
				  "wages_description": int(response['Items'][0]['wages_description']),
				  "latitude": response['Items'][0]['latitude'],
				  "longitude": response['Items'][0]['longitude'],
				  "city":response['Items'][0]['city'],
				  "state":response['Items'][0]['state'],
				  "farmers_working":{0}
			})

			
		else:
			table.put_item(Item={
				  "is_active": response['Items'][0]['is_active'],
				  "land_area": response['Items'][0]['land_area'],
				  "land_id": response['Items'][0]['land_id'],
				  "land_pin_code": response['Items'][0]['land_pin_code'],
				  "type_of_crop": response['Items'][0]['type_of_crop'],
				  "type_of_soil": response['Items'][0]['type_of_soil'],
				  "wages_description": int(response['Items'][0]['wages_description']),
				  "latitude": response['Items'][0]['latitude'],
				  "longitude": response['Items'][0]['longitude'],
				  "city":response['Items'][0]['city'],
				  "state":response['Items'][0]['state'],
				  "farmers_working":farmers_working
			})


	return redirect('farmerandlandlord:dashboardfarmer')
	
def infoland(request,land_id):
	#print(param)
	dynamodb = boto3.resource('dynamodb',
	aws_access_key_id='AKIAJIJIVDPBPUMLU37Q',
	aws_secret_access_key='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',
	region_name='ap-south-1')
	dynamodb_client=boto3.client('dynamodb',aws_access_key_id='AKIAJIJIVDPBPUMLU37Q',
	aws_secret_access_key='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',region_name='ap-south-1')
	table=dynamodb.Table('LandInfo')
	response=table.scan(FilterExpression=Attr('land_id').eq(land_id))
	d={}
	lid=response['Items'][0]['land_id']
	toc=response['Items'][0]['type_of_crop']
	wd=response['Items'][0]['wages_description']
	lpc=response['Items'][0]['land_pin_code']
	la=response['Items'][0]['land_area']
	tos=response['Items'][0]['type_of_soil']
	lat=response['Items'][0]['latitude']
	logt=response['Items'][0]['longitude']
	city=response['Items'][0]['city']
	state=response['Items'][0]['state']
	farmers_working=response['Items'][0]['farmers_working']
	
	#print(wd)
	table=dynamodb.Table('Landlord')
	#AttributesToGet=['lands_owned']
	response=table.scan()
	#print(response)
	for i in range(len(response['Items'])):
		lands_owned=response['Items'][i]['lands_owned']
		#print(lands_owned)
		for x in lands_owned:
			#print(x)
			if str(x)==land_id:
				land_lord_name=response['Items'][i]['land_lord_name']
				#print(land_lord_name)
				break
	if farmers_working!={0}:
		table=dynamodb.Table('FarmerInfo')
		a=set()
		for x in farmers_working:
			response=table.scan(FilterExpression=Attr('farmer_id').eq(x))
			b={response['Items'][0]['username']}
			a=a|b	
		d={'lid':lid,'toc':toc,'wd':wd,'lpc':lpc,'la':la,'tos':tos,'lad':land_lord_name,'lat':lat,'lgt':logt,'city':city,'state':state,'a':a}
	else:
		d={'lid':lid,'toc':toc,'wd':wd,'lpc':lpc,'la':la,'tos':tos,'lad':land_lord_name,'lat':lat,'lgt':logt,'city':city,'state':state}

	return render(request,"farmerandlandlord/infoland.html",{'d':d})
def landlordsearch(request):
	dynamodb = boto3.resource('dynamodb',
	aws_access_key_id='AKIAJIJIVDPBPUMLU37Q',
	aws_secret_access_key='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',
	region_name='ap-south-1')
	dynamodb_client=boto3.client('dynamodb',aws_access_key_id='AKIAJIJIVDPBPUMLU37Q',
	aws_secret_access_key='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',region_name='ap-south-1')
	table=dynamodb.Table('user')
	farmer=True
	pincode='522006'
	response=table.scan(FilterExpression=Attr('is_farmer').eq(farmer) & Attr('pincode').eq(pincode))
	#print(response)
	l={}
	for i in range(len(response['Items'])):
		l[i]=response['Items'][i]['farmer_id']
	table=dynamodb.Table('FarmerInfo')
	print(l)
	d={}
	for j in range(len(l)):
		new=table.scan(FilterExpression=Attr('farmer_id').eq(l[j]))
		print(new)
		farmer_id=new['Items'][0]['farmer_id']
		farmer_name=new['Items'][0]['farmer_name']
		lands_worked=new['Items'][0]['lands_worked']
		d[j]={'farmer_id':farmer_id,'farmer_name':farmer_name,'lands_worked':lands_worked}
	print(d)
	return render(request,'farmerandlandlord/displayfarmer.html',{'d':d})
def dashboardlandlord(request):
	dynamodb = boto3.resource('dynamodb',
	aws_access_key_id='AKIAJIJIVDPBPUMLU37Q',
	aws_secret_access_key='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',
	region_name='ap-south-1')
	dynamodb_client=boto3.client('dynamodb',aws_access_key_id='AKIAJIJIVDPBPUMLU37Q',
	aws_secret_access_key='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',region_name='ap-south-1')
	if is_loggedin(request):
		email=request.session['email']
		table=dynamodb.Table('user')
		response=table.scan(FilterExpression=Attr('email').eq(email))
		land_lord_id=response['Items'][0]['land_lord_id']
		table=dynamodb.Table('Landlord')
		#land_lord_id="2e25388fde8290dc286a6164fa2d97e551b53498dcbf7bc378eb1f1780"
		
		#pincode=522006
		response=table.scan(FilterExpression=Attr('land_lord_id').eq(land_lord_id))
		if response['Count']==1:
			lands_owned=response['Items'][0]['lands_owned']
			d={}
			table=dynamodb.Table('LandInfo')
			for k in lands_owned:
				new2=table.scan(FilterExpression=Attr('land_id').eq(str(k)))
				#print(new2)
				if new2['Count']==1:
					lid=new2['Items'][0]['land_id']
					toc=new2['Items'][0]['type_of_crop']
					wd=new2['Items'][0]['wages_description']
					lpc=new2['Items'][0]['land_pin_code']
					la=new2['Items'][0]['land_area']
					tos=new2['Items'][0]['type_of_soil']
					d[k]={'lid':lid,'toc':toc,'wd':wd,'lpc':lpc,'la':la,'tos':tos}
			#print(d)
			return render(request,'farmerandlandlord/dashboardlandlord.html',{'d':d})
		else:
			return render(request,'farmerandlandlord/dashboardlandlord.html')
	else:
		return redirect('registration:login_display')
def dashboardfarmer(request):
	dynamodb = boto3.resource('dynamodb',
	aws_access_key_id='AKIAJIJIVDPBPUMLU37Q',
	aws_secret_access_key='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',
	region_name='ap-south-1')
	dynamodb_client=boto3.client('dynamodb',aws_access_key_id='AKIAJIJIVDPBPUMLU37Q',
	aws_secret_access_key='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',region_name='ap-south-1')
	#farmer_id="1e25388fde8290dc286a6164fa2d97e551b53498dcbf7bc378eb1f178"
	if is_loggedin(request):
		email=request.session['email']
		table=dynamodb.Table('user')
		response=table.scan(FilterExpression=Attr('email').eq(email))
		farmer_id=response['Items'][0]['farmer_id']
		table=dynamodb.Table('FarmerInfo')
		response=table.scan(FilterExpression=Attr('farmer_id').eq(farmer_id))
		#print(response)
		if response['Count']==1:
			land_id=response['Items'][0]['land_working']
			lands_worked=response['Items'][0]['lands_worked']
			#print(land_id)
			land_working=land_id
			table=dynamodb.Table('LandInfo')
			response=table.scan(FilterExpression=Attr('land_id').eq(land_id))
			#print(response)
			if land_id!="" and lands_worked=={0}:
				lid=response['Items'][0]['land_id']
				#print(lid)
				toc=response['Items'][0]['type_of_crop']
				wd=response['Items'][0]['wages_description']
				lpc=response['Items'][0]['land_pin_code']
				la=response['Items'][0]['land_area']
				tos=response['Items'][0]['type_of_soil']
				lat=response['Items'][0]['latitude']
				logt=response['Items'][0]['longitude']
				city=response['Items'][0]['city']
				state=response['Items'][0]['state']
				d={'lid':lid,'toc':toc,'wd':wd,'lpc':lpc,'la':la,'tos':tos,'lat':lat,'lgt':logt,'city':city,'state':state}
				#print(lands_worked)
				return render(request,'farmerandlandlord/dashboardfarmer.html',{'d':d,'lwg':land_working})
			if lands_worked!={0} and land_id=="":
				t={}
				for k in lands_worked:
					new2=table.scan(FilterExpression=Attr('land_id').eq(str(k)))
					#print(new2)
					if new2['Count']==1:
						lid=new2['Items'][0]['land_id']
						toc=new2['Items'][0]['type_of_crop']
						wd=new2['Items'][0]['wages_description']
						lpc=new2['Items'][0]['land_pin_code']
						la=new2['Items'][0]['land_area']
						tos=new2['Items'][0]['type_of_soil']
						t[k]={'lid':lid,'toc':toc,'wd':wd,'lpc':lpc,'la':la,'tos':tos}
						print(t)
				return render(request,'farmerandlandlord/dashboardfarmer.html',{'t':t,'lwg':land_working})

				#print(d)
			if lands_worked!={0} and land_id!="":
				lid=response['Items'][0]['land_id']
				#print(lid)
				toc=response['Items'][0]['type_of_crop']
				wd=response['Items'][0]['wages_description']
				lpc=response['Items'][0]['land_pin_code']
				la=response['Items'][0]['land_area']
				tos=response['Items'][0]['type_of_soil']
				lat=response['Items'][0]['latitude']
				logt=response['Items'][0]['longitude']
				city=response['Items'][0]['city']
				state=response['Items'][0]['state']
				d={'lid':lid,'toc':toc,'wd':wd,'lpc':lpc,'la':la,'tos':tos,'lat':lat,'lgt':logt,'city':city,'state':state}
				t={}
				for k in lands_worked:
					new2=table.scan(FilterExpression=Attr('land_id').eq(str(k)))
					#print(new2)
					if new2['Count']==1:
						lid=new2['Items'][0]['land_id']
						toc=new2['Items'][0]['type_of_crop']
						wd=new2['Items'][0]['wages_description']
						lpc=new2['Items'][0]['land_pin_code']
						la=new2['Items'][0]['land_area']
						tos=new2['Items'][0]['type_of_soil']
						t[k]={'lid':lid,'toc':toc,'wd':wd,'lpc':lpc,'la':la,'tos':tos}
						print(t)
				return render(request,'farmerandlandlord/dashboardfarmer.html',{'d':d,'t':t,'lwg':land_working})
				
		else:
			return render(request,'farmerandlandlord/dashboardfarmer.html')
	else:
		return redirect('registration:login_display')
def landlordviewrequest(request):
	dynamodb = boto3.resource('dynamodb',
	aws_access_key_id='AKIAJIJIVDPBPUMLU37Q',
	aws_secret_access_key='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',
	region_name='ap-south-1')
	dynamodb_client=boto3.client('dynamodb',aws_access_key_id='AKIAJIJIVDPBPUMLU37Q',
	aws_secret_access_key='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',region_name='ap-south-1')
	#land_lord_id="2e25388fde8290dc286a6164fa2d97e551b53498dcbf7bc378eb1f1780"
	email=request.session['email']
	table=dynamodb.Table('user')
	response=table.scan(FilterExpression=Attr('email').eq(email))
	land_lord_id=response['Items'][0]['land_lord_id']
	table=dynamodb.Table('FarmerRequest')
	response=table.scan()
	if response['Count']>0:
		l={}
		k={}
		for i in range(response['Count']):
			l[response['Items'][i]['land_id']]=1
			k[response['Items'][i]['user_id']]=1
		#print(l)
		table=dynamodb.Table('Landlord')
		response2=table.scan(FilterExpression=Attr('land_lord_id').eq(land_lord_id))
		d={}
		j=0
		table=dynamodb.Table('LandInfo')
		table3=dynamodb.Table('FarmerRequest')
		table2=dynamodb.Table('user')
		for i in response2['Items'][0]['lands_owned']:
			if str(i) in l:
				new2=table.scan(FilterExpression=Attr('land_id').eq(str(i)))
				response3=table3.scan(FilterExpression=Attr('land_id').eq(str(i)))
				uid=response3['Items'][0]['user_id']
				new=table2.scan(FilterExpression=Attr('farmer_id').eq(uid))
				un=new['Items'][0]['username']
				ue=new['Items'][0]['email']
				uadd=new['Items'][0]['address']
				uph=new['Items'][0]['phone_number']
				lid=i
				toc=new2['Items'][0]['type_of_crop']
				wd=new2['Items'][0]['wages_description']
				lpc=new2['Items'][0]['land_pin_code']
				la=new2['Items'][0]['land_area']
				tos=new2['Items'][0]['type_of_soil']
				d[j]={'uid':uid,'un':un,'ue':ue,'uadd':uadd,'uph':uph,'lid':lid,'toc':toc,'wd':wd,'lpc':lpc,'la':la,'tos':tos}
			j+=1
		print(d)
		
		#new=table2.scan(FilterExpression=Attr('farmer_id').eq())
		return render(request,'farmerandlandlord/displayfarmer.html',{'d':d})
	else:
		return render(request,'farmerandlandlord/displayfarmer.html')

		









	

		
	
	
	





	
>>>>>>> 8eb17c4ea19341b7b31051556e0cbc6c2306e44c
	