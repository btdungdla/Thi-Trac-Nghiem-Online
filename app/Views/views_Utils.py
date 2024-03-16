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

def handle_uploaded_file(file, course_id):   
    # Đọc dữ liệu từ file Excel bằng pandas
    df = pd.read_excel(file)

    # Lặp qua từng hàng trong DataFrame và tạo bản ghi mới trong bảng Course_Student
    for index, row in df.iterrows():
        username = row['username']  # Điều này phụ thuộc vào cột trong file Excel
        user = Student.objects.get(user__username=username)  # Thay đổi tùy thuộc vào cách bạn lưu thông tin người dùng

        # Tạo Course_Student mới
        Course_Student.objects.create(user=user, Course_id=course_id)


def export_result_to_excel(request,exam_id):
    # Xử lý tra cứu (thay thế bằng mã của bạn)
    quizs = Quiz.objects.filter(course__exam__id = exam_id)

    # Tạo workbook và worksheet
    wb = openpyxl.Workbook()
    ws = wb.active

    # Ghi dòng tiêu đề
    header = ['Phòng/CCT', 'Tên', 'Nhóm', 'Kết quả','Xếp loại']
    ws.append(header)

    # Ghi dữ liệu
    for row in quizs:
        row_data = [
            str(row.user.department),
            str(row.user.name),
            str(row.course.course_name),
            row.Total_Correct_Answer,
            str(grading(row.Total_Correct_Answer,exam_id))
        ]
        ws.append(row_data)

    # Tạo HttpResponse
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=result.xlsx'
    wb.save(response)

    return response

def download_sample_file(request,tenmau):
    #file_path = os.path.join(settings.MEDIA_ROOT1, tenmau)  # Thay đổi đường dẫn đến file mẫu
    file_path = os.path.join(settings.BASE_DIR, 'app/media/'+tenmau)
    with open(file_path, 'rb') as file:
        response = HttpResponse(file.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=sample_file.xlsx'
        return response
    
def upload_quiz_excel(request):
    return render(request, 'app/upload_quiz_excel.html')