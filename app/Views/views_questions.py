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


def upload_word_file(request, categoryid):
    cat = Category.objects.get(id=categoryid)
    if request.method == 'POST':
        #form = UploadWordFileForm(request.POST, request.FILES)
        form = UploadQuestionWordFileForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            # Xử lý tệp Word
            word_file = form.cleaned_data['word_file']
           
            doc = Document(word_file)

            current_question = None  # Dùng để theo dõi câu hỏi đang được xử lý
            is_answer = False  # Bắt đầu với giả định rằng đoạn văn bản không phải là câu trả lời

            for paragraph in doc.paragraphs:
                # Kiểm tra nếu đoạn văn bản không trống
                if paragraph.text.strip():
                    if re.match(r'^\s*Câu\s+\d+\.', paragraph.text.strip()):  # Xác định câu hỏi bắt đầu bằng "Câu"
                        question_text = re.sub(r'^\s*Câu\s+\d+\.', '', paragraph.text).strip()
                        current_question = Question.objects.create(question_text=question_text,category=cat)
                        is_answer = False  # Sau đó, đoạn tiếp theo sẽ không phải là câu trả lời
                    # elif re.match(r'^\s*[A-Da-d]\.|^\s*[A-Da-d]\)', paragraph.text.strip()):  # Xác định đáp án bắt đầu bằng "A.", "B.", "C.", "D.", "A)", hoặc "B)"
                    elif  paragraph.text.strip()[0].upper() in ['A', 'B', 'C', 'D']:  # Xác định đáp án bắt đầu bằng "A.", "B.", "C.", "D.", "A)", hoặc "B)"    
                        answer_text = re.sub(r'^\s*[A-Da-d]\.|^\s*[A-Da-d]\)', '', paragraph.text).strip()# Lấy phần sau của đáp án
                        is_correct = False
                        #answer_text = paragraph.text

                        for run in paragraph.runs:
                            if run.bold:
                                is_correct = True
                                #answer_text = run.text[2:].strip()
                                #answer_text = run.text

                        Answer.objects.create(question=current_question, answer_text=answer_text, is_correct=is_correct)
            messages.success(request, 'Đã tạo câu hỏi thành công.')
            
            return JsonResponse({'success': True})  # Trả về phản hồi JSON
    else:
        form = UploadQuestionWordFileForm()
   
    return render(request, 'app/upload_word_file.html', {'form': form,'exam_id':cat.exam.id,'category_id':cat.id,'category_name':cat.category_name})
