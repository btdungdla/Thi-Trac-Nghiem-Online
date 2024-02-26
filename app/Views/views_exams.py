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

def manage_exam(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            exams = Exam.objects.all()
            if request.method == 'POST':
                form = ExamForm(request.POST)
                if form.is_valid():
                    form.save()
                    # Redirect để tránh việc gửi lại dữ liệu khi người dùng làm mới trang
                    return redirect('manage_exam')
            else:
                form = ExamForm()

            context = {'exams': exams, 'form': form}
            return render(request, 'app/manage_exam.html', context)
        else:
            return HttpResponse("Bạn không có quyền thực hiện chức năng này")
    else:
        return redirect("/login/")
    
def get_exam_info(request, exam_id):
    if request.user.is_authenticated:
        if request.user.is_staff:
            exam = Exam.objects.get(id=exam_id)
            data = {
                'exam_name': exam.exam_name,
                'year': exam.year,
                'status': exam.status,
                'outstanding':exam.outstanding,
                'excellent':exam.excellent,
                'good':exam.good,
                'satisfactory':exam.satisfactory
            }
            return JsonResponse(data)
        else:
            return HttpResponse("Bạn không có quyền thực hiện chức năng này")
    else:
        return redirect("/login/")
    
def update_exam(request, exam_id):
    if request.user.is_authenticated:
        if request.user.is_staff:
            exam = Exam.objects.get(id=exam_id)
            if request.method == 'POST':
                form = ExamForm(request.POST, instance=exam)
                if form.is_valid():
                    form.save()
                    data = {'success': True}
                else:
                    data = {'success': False, 'errors': form.errors}
                return JsonResponse(data)
        else:
            return HttpResponse("Bạn không có quyền thực hiện chức năng này")
    else:
        return redirect("/login/")