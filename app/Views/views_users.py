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
# def register(request):
#     frmDangKy = CreateUserForm()    
#     if request.method == 'POST':
#         frmDangKy = CreateUserForm(request.POST)
#         if frmDangKy.is_valid:
#             frmDangKy.save()
#             u = User.objects.get(username=request.POST.get('username'))
#             cust = Customer.objects.create(user=u,name= request.POST.get('username'),email= request.POST.get('email'))
#             return redirect("login")
#     context={'form':frmDangKy}
#     return render(request,'app/register.html',context)

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

def change_password(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = CustomPasswordChangeForm(request.user, request.POST)
            if form.is_valid():
                user = form.save()
                update_session_auth_hash(request, user)  # Để người dùng không bị logout sau khi đổi mật khẩu
                messages.success(request, 'Mật khẩu đã được thay đổi thành công.')
                return redirect('change_password')
            else:
                messages.error(request, 'Có lỗi xảy ra. Vui lòng kiểm tra lại thông tin.')
        else:
            form = CustomPasswordChangeForm(request.user)

        return render(request, 'app/change_password.html', {'form': form})
    else:            
        return redirect("/login/")
    
def create_user(request):
     if request.user.is_authenticated:
        if request.user.is_staff:
            if request.method == 'POST' and request.FILES['excel_file']:
                excel_file = request.FILES['excel_file']

                try:
                    df = pd.read_excel(excel_file)

                    for _, row in df.iterrows():
                        # Tạo người dùng
                        sUser = row['username']
                        spass= row['password']
                        user = User.objects.create_user(username=row['username'], password=row['password'])

                        # Tạo sinh viên
                        sname = row['Họ và tên']
                        sPhong =row['Phòng/Đội']
                        sCQT = row['Đơn vị']
                        student = Student.objects.create(user=user, name=row['Họ và tên'], email=row['email'], department = row['Phòng/Đội'], organization = row['Đơn vị'])

                    messages.success(request, 'Đã tạo người dùng và sinh viên thành công từ file Excel.')
                    return HttpResponse('Đã tạo người dùng thành công')  # Chuyển hướng đến trang thành công

                except Exception as e:
                    messages.error(request, f'Có lỗi xảy ra: {str(e)}')
                    return HttpResponse('Lỗi')  # Chuyển hướng đến trang lỗi

            return render(request, 'app/process_excel.html')

def info(request):
    if request.user.is_authenticated:
        student = Student.objects.get(user=request.user)
        course = Course.objects.get(course_student__Course__status = True, course_student__user = student)
        course_name = course.course_name
        context ={
            'student':student,
            'course_name':course_name
        }
        return render(request,"app/info.html",context)
    else:
        return redirect("/login/")
#endregion
