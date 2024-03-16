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
from app.Views.views_Utils import *

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

def get_course_info(request, course_id):
    if request.user.is_authenticated:
        if request.user.is_staff:
            course = Course.objects.get(id=course_id)
            data = {
                'course_name': course.course_name,
                'numberofquestion': course.numberofquestion,
                'status': course.status,
                'timeofquiz': course.timeofquiz,
            }
            return JsonResponse(data)
        else:
            return HttpResponse("Bạn không có quyền thực hiện chức năng này")
    else:
        return redirect("/login/")
    
def update_course(request, course_id):
    if request.user.is_authenticated:
        if request.user.is_staff:
            course = Course.objects.get(id=course_id)
            exam = course.exam
            if request.method == 'POST':
                form = CourseForm(request.POST, instance=course)
                print(form.errors)
                if form.is_valid():
                    form.instance.exam = exam
                    form.save()
                    data = {'success': True}
                else:
                    data = {'success': False, 'errors': form.errors}
                return JsonResponse(data)
        else:
            return HttpResponse("Bạn không có quyền thực hiện chức năng này")
    else:
        return redirect("/login/")


def add_course_category(request, course_id):
    course = Course.objects.get(id=course_id)
    categories = Category.objects.all()
    category_question_counts = {}
    for category in categories:
        course_category, created = Course_Category.objects.get_or_create(
            course=course,
            category=category,
            defaults={'numberofquestion': 0}
        )
        category_question_counts[category.category_name] = course_category.numberofquestion
    if request.method == 'POST':
        for category in categories:
            quantity_key = f'numberofquestion_{category.category_name}'
            # Sử dụng .get() để tránh KeyError và cung cấp giá trị mặc định là "0"
            quantity_value = request.POST.get(quantity_key, "0")

            # Sử dụng try-except để xử lý trường hợp quantity_value không phải là số
            try:
                quantity_value = int(quantity_value)
                if quantity_value >= 0:
                    course_category, created = Course_Category.objects.get_or_create(
                        course=course,
                        category=category,
                        defaults={'numberofquestion': quantity_value}
                    )
                    if not created:
                        course_category.numberofquestion = quantity_value
                        course_category.save()
            except ValueError:
                # Xử lý lỗi nếu quantity_value không phải là số
                # Ví dụ: thông báo lỗi cho người dùng hoặc ghi log
                print(f"Giá trị nhập cho {category.category_name} không phải là số hợp lệ.")
                
        return HttpResponse('Đã cập nhật thành công')

    else:
        form = CourseCategoryForm()

    context = {'course': course, 'categories': categories, 'category_question_counts': category_question_counts}
    return render(request, 'app/add_course_category.html', context)


def add_user_to_course(request, course_id):
     if request.user.is_authenticated:
        if request.user.is_staff:
            if request.method == 'POST':
                form = ExcelUploadForm(request.POST, request.FILES)
                if form.is_valid():
                    excel_file = request.FILES['excel_file']
                    handle_uploaded_file(excel_file, course_id)
                    return HttpResponse('Thêm thành công')  # Chuyển hướng đến trang thành công hoặc trang khác
            else:
                form = ExcelUploadForm()
            course = Course.objects.get(id=course_id)
            return render(request, 'app/upload_excel.html', {'form': form, 'course_id': course_id,'course':course})
        
def member_course(request, courseid, additional_param=None):    
    if request.user.is_authenticated:
        if request.user.is_staff:
            course = Course.objects.get(id=courseid)
            students_in_course = Student.objects.filter(course_student__Course__id=courseid)            
            page = request.GET.get('page')
            search_name = request.GET.get('search_name')  # Thêm biến tìm kiếm
            search_department = request.GET.get('search_department')                         
            if students_in_course is not None:    
                if search_name:
                    students_in_course = students_in_course.filter(name__icontains=search_name)
                else:
                    search_name = ""
                if search_department:
                    students_in_course = students_in_course.filter(course_student__Course__course_name__icontains=search_department)
                else:
                    search_department = ""
               
                items_per_page = 20
                paginator = Paginator(students_in_course, items_per_page)

                try:
                    students_in_course = paginator.page(page)
                except PageNotAnInteger:
                    students_in_course = paginator.page(1)
                except EmptyPage:
                    students_in_course = paginator.page(paginator.num_pages)

                context = {
                    'students':students_in_course,
                    'course': course,
                    'additional_param': additional_param,  
                    'search_name': search_name,
                    'search_department': search_department,
                }
                return render(request, 'app/member_course.html', context)            
            else:
                return HttpResponse("Không có thi sinh trong nhóm này")
        else:
            return HttpResponse("Bạn không có quyền thực hiện chức năng này")
    else:
        return redirect("/login/")      

def delete_student_from_course(request, student_id, course_id):
    if request.user.is_authenticated:
        if request.user.is_staff:
            try:
               course_student = Course_Student.objects.get(user__user__username = student_id, Course__id = course_id)
               course_student.delete()
            except Course_Student.DoesNotExist:
                pass  # Nếu không tìm thấy, không làm gì cả

            return redirect('member_course', courseid=course_id)
        else:
            return HttpResponse("Bạn không có quyền thực hiện chức năng này")
    else:
        return redirect("/login/")    