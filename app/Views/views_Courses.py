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

def GetCourse(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            try:   
                exams= Exam.objects.filter(status=True)             
                courses = Course.objects.filter(status = True,exam__status=True)
                context = {'courses':courses,'exams':exams}
                return render(request,"app/courses.html",context)
            except ObjectDoesNotExist:
                return HttpResponse("Người dùng chưa là học viên")
        else:
            try:
                co_users = Course_Student.objects.filter(user=request.user.student)
                course_ids = co_users.values_list('Course_id', flat=True)
                courses = Course.objects.filter(id__in=course_ids)
                context = {'courses':courses}
                return render(request,"app/courses.html",context)
            except ObjectDoesNotExist:
                return HttpResponse("Người dùng chưa là học viên")
    else:
        return redirect("/login/")
    
def Result_Course(request, additional_param=None):    
    if request.user.is_authenticated:
        if request.user.is_staff:
            if request.method == "POST":
                examid = request.POST.get('ExamID_Result')
                exam = Exam.objects.get(id=examid)
                if examid is not None:      
                    try:
                        quizs = Quiz.objects.filter(course__exam__id=examid).order_by('id')  
                        #total_quizs = Quiz.objects.filter(course__exam__id=examid)
                        items_per_page = 3
                        paginator = Paginator(quizs, items_per_page)

                        # Trang được yêu cầu
                        page = request.GET.get('page')
                        try:
                            quizs = paginator.page(page)
                        except PageNotAnInteger:
                            quizs = paginator.page(1)
                        except EmptyPage:
                            quizs = paginator.page(paginator.num_pages)

                        context = {
                            'exam': exam,
                            'quizs': quizs,
                            'len': quizs.__len__,
                            #'total_quizs': total_quizs,
                            'additional_param': additional_param,  # Thêm đối số vào context
                        }
                        return render(request, 'app/Result_Course.html', context) 
                    except ObjectDoesNotExist:                
                        return render(request, 'app/Result_Course.html', context)            
                else:
                    return render(request, 'app/Result_Course.html', context)
            else:
                page = request.GET.get('page')
                search_name = request.GET.get('search_name')  # Thêm biến tìm kiếm
                search_department = request.GET.get('search_department')  # Thêm biến tìm kiếm
                search_group = request.GET.get('search_group')
                examid = request.GET.get('examid')
                exam = Exam.objects.get(id=examid)
                
                if examid is not None:      
                    try:
                        quizs = Quiz.objects.filter(course__exam__id=examid)
                        
                        if search_name:
                            quizs = quizs.filter(user__name__icontains=search_name)
                        if search_department:
                            quizs = quizs.filter(user__department__icontains=search_department)
                        if search_group:
                            quizs = quizs.filter(course__course_name__icontains=search_group)
                        #total_quizs = Quiz.objects.filter(course__exam__id=examid)
                        items_per_page = 3
                        paginator = Paginator(quizs, items_per_page)

                        try:
                            quizs = paginator.page(page)
                        except PageNotAnInteger:
                            quizs = paginator.page(1)
                        except EmptyPage:
                            quizs = paginator.page(paginator.num_pages)

                        context = {
                            'exam': exam,
                            'quizs': quizs,
                            'len': quizs.__len__,
                            #'total_quizs': total_quizs,
                            'additional_param': additional_param,  # Thêm đối số vào context
                            'search_name': search_name,
                            'search_department': search_department,
                        }
                        return render(request, 'app/Result_Course.html', context) 
                    except ObjectDoesNotExist:                
                        return render(request, 'app/Result_Course.html', context)            
                else:
                    return render(request, 'app/Result_Course.html', context)      


def result_dash_board(request,exam_id):
    exam_id = 3
    quizs = Quiz.objects.filter(course__exam__id = exam_id,finish =True)
    result= data_analysis(quizs)
    context={
        "result":result,
    }
    return render(request, 'app/result_dash_board.html',context)

def data_analysis(quizs):
    q = quizs.first()
    exam = q.course.exam
    diem_xuat_sac = exam.outstanding
    diem_gioi = exam.excellent
    diem_kha = exam.good
    diem_trung_binh = exam.satisfactory
    so_luong_gioi = 0
    so_luong_xuat_sac= 0
    so_luong_kha = 0
    so_luong_trung_binh = 0
    so_luong_yeu =0
    
    for quiz in quizs:
        if quiz.Total_Correct_Answer < diem_trung_binh:
            so_luong_yeu += 1
        elif quiz.Total_Correct_Answer < diem_kha:
            so_luong_kha += 1
        elif quiz.Total_Correct_Answer < diem_gioi:
            so_luong_kha += 1
        elif quiz.Total_Correct_Answer < diem_xuat_sac:
            so_luong_gioi += 1
        else:
            so_luong_xuat_sac += 1   
    mylist = [so_luong_xuat_sac,so_luong_gioi,so_luong_kha,so_luong_kha,so_luong_yeu]
    return mylist

def manage_course(request, exam_id):
    if request.user.is_authenticated:
        if request.user.is_staff:
            exam = Exam.objects.get(id=exam_id)
            try:
                courses = Course.objects.filter(exam__id = exam_id)
            except ValueError:
                courses = None
            if request.method == 'POST':
                form = CourseForm(request.POST)
                if form.is_valid():
                    # Thêm giá trị của exam vào form trước khi lưu
                    form.instance.exam = Exam.objects.get(id=exam_id)
                    form.save()
                    return redirect('manage_course', exam_id=exam_id)
            else:
                form = CourseForm(exam=exam)

            context = {'courses': courses, 'form': form, 'exam': exam}
            return render(request, 'app/manage_course.html', context)
        else:
            return HttpResponse("Bạn không có quyền thực hiện chức năng này")
    else:
        return redirect("/login/")
