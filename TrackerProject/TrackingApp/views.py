from django.shortcuts import render,redirect,HttpResponse
from django.contrib.auth import login,logout,authenticate
from datetime import datetime
import csv
from django.conf import settings
import pathlib
import os
import numpy as np
from django.http import JsonResponse

def loginUser(request):
    msg = ""
    if request.user.is_authenticated:
        #return render(request,"banknifty.html",{'username': request.user.username ,'index':'Bank Nifty'})
        return showBankNiftyPage(request)
    if request.method == "POST" :
        d = request.POST
        user = d["username"]
        pwd = d['password']
        user = authenticate(username = user , password = pwd)
        if user:
            login(request,user)
            #return render(request,"banknifty.html",{'username':user.username,'index':'Bank Nifty'} )
            return showBankNiftyPage(request)
        else:
            msg = 'invalidlogin'
    return render(request,'login.html', {'msg':msg})

def logoutUser(request):
    logout(request)
    msg = 'logoutsuccess'
    return redirect(loginUser)


def showNiftyPage(request):
    username = request.user.username
    index = "Nifty"
    limit=200
    today = datetime.now().date()
    path = settings.CSV_DIR
    niftycsv = open(str(path)+r'/NIFTY-'+str(today)+".csv",'r')
    reader = csv.DictReader(niftycsv)
    headers = [col for col in reader.fieldnames[:-3]]
    out = [row for row in reader]
    length = len(out)
    if(length!= 0):
        recent = out[::-1][0]
    else:
        recent = {}
    if(length > limit):
        data_last = out[length-limit:]
        data_first = out[:length-limit]
    else:
        data_last = out
        data_first = []
        
    try:
        with open('prevdayEODFile.txt','r') as f:
            lines = f.readlines()
            prevLTPstrike =lines[0].split()[2]
    except:
        pass

    return render(request,'nifty.html',{'username':username.title(),'index':index , 'headers' : headers,'recent':recent, 'data_first' :data_first ,'data_last':data_last, 'prevLTPstrike':prevLTPstrike } )

def showBankNiftyPage(request):
    username = request.user.username
    index = "Bank Nifty"
    limit=200
    today = datetime.now().date()
    path = settings.CSV_DIR
    bankniftycsv = open(str(path)+r'/BANKNIFTY-'+str(today)+".csv",'r')
    reader = csv.DictReader(bankniftycsv)
    headers = [col for col in reader.fieldnames[:-3]]
    out = [row for row in reader]
    length = len(out)
    if(length!= 0):
        recent = out[::-1][0]
    else:
        recent = {}
    if(length > limit):
        data_last = out[length-limit:]
        data_first = out[:length-limit]
    else:
        data_last = out
        data_first = []
    
    try:
        with open('prevdayEODFile.txt','r') as f:
            lines = f.readlines()
            prevLTPstrike =lines[1].split()[2]
    except:
        pass
    
    return render(request,'banknifty.html',{'username':username.title(),'index':index, 'headers' : headers,'recent':recent, 'data_first' :data_first ,'data_last':data_last,'prevLTPstrike':prevLTPstrike})

def fetchNiftyValues(request):
    today = datetime.now().date()
    lastline=""
    try:
        with open(str(settings.CSV_DIR)+r'/NIFTY-'+str(today)+".csv",'rb') as f:
            last = lastLine(f)
    except:
        last = ['00:00:00', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0','0', '0', '0', '0', '0', '0']
    return JsonResponse(last, safe=False)


def fetchBankNiftyValues(request):
    today = datetime.now().date()
    lastline=""
    try:
        with open(str(settings.CSV_DIR)+r'/BANKNIFTY-'+str(today)+".csv",'rb') as f:
            last = lastLine(f)
    except:
        last = ['00:00:00', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0','0', '0', '0', '0', '0', '0']
    print(last)
    return JsonResponse(last, safe=False)

def download_file(request,index):
    today = datetime.now().date()
    with open(str(settings.CSV_DIR)+r'/'+index+'-'+str(today)+".csv",'rb') as f:
        response = HttpResponse(f, content_type="text/csv")
        response['Content-Disposition'] = "attachment; filename=%s" % index +'-'+str(today)+".csv"
        return response
    raise 404

def showBankNiftyGraph(request):
    today = datetime.now().date()
    path = settings.CSV_DIR
    bankniftycsv = open(str(path)+r'/BANKNIFTY-'+str(today)+".csv",'r')
    reader = csv.DictReader(bankniftycsv)
    out = []
    for row in reader:
        out.append(row)
    #optimizations

    # reqIndexes = [5,6,7,11]
    # npout = np.array(out)
    # newArray = npout[:, reqIndexes]
    # out = newArray.tolist()
    # print(out)
    
    return render(request,'bankniftygraph.html',{'data':out})

# custom function

def lastLine(f):
    f.seek(-150,os.SEEK_END)
    last = f.readlines()[-1]
    return str(last)[2:-5].split(",")
