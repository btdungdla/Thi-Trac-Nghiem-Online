import os
from random import sample
from django.shortcuts import render,redirect
from django.http import HttpResponse,JsonResponse
import openpyxl

from THITRACNGHIEM import settings
from app.models import *
import json
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from app.forms import UploadWordFileForm
from app.forms import *
from docx import Document
import re
from datetime import datetime, timedelta
from django.core.paginator import Paginator
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q, Count
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash

#region User
def register(request):
    frmDangKy = CreateUserForm()    
    if request.method == 'POST':
        frmDangKy = CreateUserForm(request.POST)
        if frmDangKy.is_valid:
            frmDangKy.save()
            u = User.objects.get(username=request.POST.get('username'))
            cust = Customer.objects.create(user=u,name= request.POST.get('username'),email= request.POST.get('email'))
            return redirect("login")
    context={'form':frmDangKy}
    return render(request,'app/register.html',context)

def loginPage(request):
    if request.user.is_authenticated:
        return redirect ("home")
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request,username=username,password=password)
        if user is not None:
            login(request,user)
            return redirect ("home")
        else:
            messages.info(request,"User or Password is not correct!")
    context={}
    return render(request,'app/login.html',context)

def logoutPage(request):
    logout(request)
    return redirect("login")
#endregion
