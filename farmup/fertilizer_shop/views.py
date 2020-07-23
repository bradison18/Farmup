from django.shortcuts import render,redirect,HttpResponse
import boto3
from boto3.dynamodb.conditions import Key, Attr
# Create your views here.

#For storing images
from django.core.files.storage import FileSystemStorage

#For Pagination
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def addfertilizer(request):

    dynamodb=boto3.resource("dynamodb")
    table=dynamodb.Table("fertilizer_info")
    added=0    

    if request.method=="POST":
        name=request.POST.get("name")
        quantity=request.POST.get("quantity")
        cost=request.POST.get("cost")
        soiltype=request.POST.get("type")
        info=request.POST.get("info")
        physicalform=request.POST.get("phyform")
        perpackquantity=request.POST.get("perpackqty")
        img_file=request.FILES['img_file']

        fs = FileSystemStorage()
        fs.save(img_file.name, img_file)
        s3 = boto3.client('s3')
        bucket = 'farmup-s3'

        file_name = str(img_file)
        key_name = str(img_file)

        s3.upload_file(file_name, bucket, key_name)

        link = "https://s3-ap-south-1.amazonaws.com/{0}/{1}".format(
             bucket,
             key_name)

        id=len(table.scan()["Items"])
        id=str(id+1)

        table.put_item(
            Item={
            "fertilizer_id":id,
            "fertilizer_name":name,
            "quantity":quantity,
            "cost":cost,
            "soiltype":soiltype,
            "info":info,
            "physicalform":physicalform,
            "perpackquantity":perpackquantity,
            "img_url":link
        })

        data={
            "added":1,
            "checker":1,
            "fertilizer_id":id,
            "fertilizer_name":name,
            "quantity":quantity,
            "cost":cost,
            "soiltype":soiltype,
            "info":info,
            "physicalform":physicalform,
            "perpackquantity":perpackquantity,
            "img_url":link
        }
        return render(request,'fertilizer_shop/new_fertilizer.html',context=data)
    data={
        "added":0,
        "checker":1
    }
    return render(request,'fertilizer_shop/new_fertilizer.html',context=data)


def createnew(request):
    return redirect("fertilizer_shop:addfertilizer")

def shop(request):
    dynamodb=boto3.resource("dynamodb")
    table=dynamodb.Table("fertilizer_info")

    information=table.scan()["Items"]

    page = request.GET.get('page', 1)


    if request.method=="POST":
        pricelist=request.POST.getlist("a")
        soillist=request.POST.getlist("b")
        physicalform=request.POST.getlist("c")

        datalist1=[]
        datalist2=[]
        datalist3=[]

        if (len(pricelist)!=0):
            for element in pricelist:
                if("<" in element):
                    for info in information:
                        if int(info["cost"])<100:
                            datalist1.append(info)  
                elif (">" in element):
                    for info in information:
                        if int(info["cost"])>400:
                            datalist1.append(info)
                else:
                    price=element.split("-")
                    low=int(price[0])
                    high=int(price[1])
                    for info in information:
                        if (int(info["cost"])>=low) and (int(info["cost"])<=high) :
                            datalist1.append(info)


        if (len(soillist)!=0):
            for element in soillist:
                for info in information:
                    if (info["soiltype"]==element) :
                        datalist2.append(info)

        if (len(physicalform)!=0):
            for element in physicalform:
                for info in information:
                    if (info["physicalform"]==element) :
                        datalist3.append(info)


        if ((len(pricelist)!=0) and (len(soillist)!=0) and (len(physicalform)!=0)):
            output1=[element1 for element1 in datalist1 for element2 in datalist2 if element1['fertilizer_id']==element2['fertilizer_id']]
            filterOutput=[element1 for element1 in output1 for element2 in datalist3 if element1['fertilizer_id']==element2['fertilizer_id']]
        elif ((len(pricelist)!=0) and (len(soillist)!=0)):
            filterOutput=[element1 for element1 in datalist1 for element2 in datalist2 if element1['fertilizer_id']==element2['fertilizer_id']]
        elif ((len(pricelist)!=0) and (len(physicalform)!=0)):
            filterOutput=[element1 for element1 in datalist1 for element2 in datalist3 if element1['fertilizer_id']==element2['fertilizer_id']]
        elif ((len(soillist)!=0) and (len(physicalform)!=0)):
            filterOutput=[element1 for element1 in datalist2 for element2 in datalist3 if element1['fertilizer_id']==element2['fertilizer_id']]
        elif ((len(pricelist)!=0)):
            filterOutput=datalist1
        elif ((len(soillist)!=0)):
            filterOutput=datalist2
        elif ((len(physicalform)!=0)):
            filterOutput=datalist3
        else:
            filterOutput=information
            

        fertilizer_info=[]

        for item in filterOutput:
            data={
                "fertilizer_id":item["fertilizer_id"],
                "fertilizer_name":item["fertilizer_name"],
                "cost":item["cost"],
                "soiltype":item["soiltype"],
                "img_url":item["img_url"]
            }
            fertilizer_info.append(data)
        
        

        paginator = Paginator(fertilizer_info, 6)
        try:
            fer_info = paginator.page(page)
        except PageNotAnInteger:
            fer_info = paginator.page(1)
        except EmptyPage:
            fer_info = paginator.page(paginator.num_pages)

        context={
            "fer_info":fer_info
        }

        return render(request,'fertilizer_shop/shop.html',context)


    fertilizer_info=[]

    for item in information:
        data={
            "fertilizer_id":item["fertilizer_id"],
            "fertilizer_name":item["fertilizer_name"],
            "cost":item["cost"],
            "soiltype":item["soiltype"],
            "img_url":item["img_url"]
        }
        fertilizer_info.append(data)
    
    

    paginator = Paginator(fertilizer_info, 6)
    try:
        fer_info = paginator.page(page)
    except PageNotAnInteger:
        fer_info = paginator.page(1)
    except EmptyPage:
        fer_info = paginator.page(paginator.num_pages)

    context={
        "fer_info":fer_info
    }
    
    return render(request,'fertilizer_shop/shop.html',context)


def iteminfo(request,id):
    dynamodb=boto3.resource("dynamodb")
    table=dynamodb.Table("fertilizer_info")

    info = table.scan(
            FilterExpression = Attr('fertilizer_id').eq(id)
        )
    
    data=info["Items"][0]
    available=int(float(data["quantity"])/float(data["perpackquantity"]))
    print(available)

    if data["physicalform"]=="Solid":
        measure="Kg"
    else:
        measure="L"

    context={
        "fertilizer_id":data["fertilizer_id"],
        "name":data["fertilizer_name"],
        "soiltype":data["soiltype"],
        "price":data["cost"],
        "perpackquantity":data["perpackquantity"],
        "info":data["info"],
        "available":available,
        "measure":measure,
        "img_url":data["img_url"]

    }

    return render(request,'fertilizer_shop/item_info.html',context=context)