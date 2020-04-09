from django.shortcuts import render
import boto3
from boto3.dynamodb.conditions import Key, Attr



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
    return render(request,'shopping_cart/sellingpage.html')


def buyingpage(request):
#     dynamodb = boto3.resource('dynamodb')
#     table = dynamodb.Table('Products')
#     names = ['tomato','beans','cabbage','rice','wheat','almonds']
#     rates = [25,60,30,50,75,1000]
#     available = [7,5,25,10,6,5]
#     # for i in range(6,12):
#     #     response = table.put_item(
#     #         Item={
#     #             'product_id':i,
#     #             'product_name':names[i-6],
#     #             'product_cost':rates[i-6],
#     #             'available_amount':available[i-6]
#     #         }
#     #     )
#     response = table.scan()
#     data = response['Items']
#     print(data)
#     return render(request,'shopping_cart/shop.html')
# =======
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
    
    crop_info=zip(crop_name,crop_cost,crop_amount,crop_image_link)
    context={
        'crop_info':crop_info
    }

    return render(request,'shopping_cart/shop.html',context)
