from django.shortcuts import render
import boto3

def addCropElements(request):
    vegetables=['Brocclie','Green Peas','Corriander','Strawberry','Califlower','Small Cherries','Corn','Potato','Papaya']
    vegetablecost=[40,25,10,70,40,95,20,35,55]
    dynamodb=boto3.resource('dynamodb')
    table=dynamodb.Table('cropinfo')
    for i in range(len(vegetables)):
        table.put_item(
            Item={
                'crop_id':i+1,
                'crop_name':vegetables[i],
                'crop_amount':500,
                'cost':vegetablecost[i],
                'crop_image_link':'https://askbootstrap.com/preview/osahan-grocery-v1-4/img/item/'+str(i+1)+'.jpg',
            }
        )
    return render(request,'crop_selling_portal/sellingpage.html')

def buyingpage(request):
    dynamodb=boto3.resource('dynamodb')
    crop_table=dynamodb.Table('cropinfo')

    crop_table_elements=crop_table.scan()['Items']
    crop_name=[]
    crop_cost=[]
    crop_amount=[]
    crop_image_link=[]

    for i in range(len(crop_table_elements)):
        crop_name.append(crop_table_elements[i]['crop_name'])
        crop_cost.append(crop_table_elements[i]['cost'])
        crop_amount.append(crop_table_elements[i]['crop_amount'])
        crop_image_link.append(crop_table_elements[i]['crop_image_link'])
    
    print(crop_name)

    crop_info=zip(crop_name,crop_cost,crop_amount,crop_image_link)
    context={
        'crop_info':crop_info
    }

    return render(request,'crop_selling_portal/shop.html',context)
