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

def manage_category(request, exam_id):
    if request.user.is_authenticated:
        if request.user.is_staff:
            exam = Exam.objects.get(id=exam_id)
            try:
                categorys = Category.objects.filter(exam__id = exam_id)
            except ValueError:
                categorys = None
            if request.method == 'POST':
                form = CategoryForm(request.POST)
                if form.is_valid():
                    # Thêm giá trị của exam vào form trước khi lưu
                    form.instance.exam = Exam.objects.get(id=exam_id)
                    form.save()
                    return redirect('manage_category', exam_id=exam_id)
            else:
                form = CategoryForm()

            context = {'categorys': categorys, 'form': form, 'exam': exam}
            return render(request, 'app/manage_category.html', context)
        else:
            return HttpResponse("Bạn không có quyền thực hiện chức năng này")
    else:
        return redirect("/login/")
    
def get_category_info(request, category_id):
    if request.user.is_authenticated:
        if request.user.is_staff:
            category = Category.objects.get(id=category_id)
            data = {
                'category_name': category.category_name,
                'status': category.status,
            }
            return JsonResponse(data)
        else:
            return HttpResponse("Bạn không có quyền thực hiện chức năng này")
    else:
        return redirect("/login/")
    
def update_category(request, category_id):
    if request.user.is_authenticated:
        if request.user.is_staff:
            category = Category.objects.get(id=category_id)
            if request.method == 'POST':
                form = CategoryForm(request.POST, instance=category)
                if form.is_valid():
                    form.instance.exam = category.exam
                    form.save()
                    data = {'success': True}
                else:
                    data = {'success': False, 'errors': form.errors}
                return JsonResponse(data)
        else:
            return HttpResponse("Bạn không có quyền thực hiện chức năng này")
    else:
        return redirect("/login/")
    