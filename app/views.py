import os
from random import sample
from django.shortcuts import render,redirect
from django.http import HttpResponse,JsonResponse
import openpyxl

from THITRACNGHIEM import settings
from .models import *
import json
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from .forms import UploadWordFileForm
from .forms import *
from docx import Document
import re
from datetime import datetime, timedelta
from django.core.paginator import Paginator
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q, Count
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash


# Create your views here.
def search(request):
    if request.user.is_authenticated:
        user_login = 'show'
        user_not_login = 'hidden'
    else:
        user_login = 'hidden'
        user_not_login = 'show'
    if request.method == "POST":
        keysearch = request.POST.get('searchkey')
        products = Product.objects.filter(name__contains=keysearch)
        context = {'products':products,'user_login':user_login,'user_not_login':user_not_login}
        return render(request,'app/search.html', context)
    context = {'user_login':user_login,'user_not_login':user_not_login}
    return render(request,'app/search.html', context)

def home(request):
    if request.user.is_authenticated:
        user_login = 'show'
        user_not_login = 'hidden'
    else:
        user_login = 'hidden'
        user_not_login = 'show'   
    context = {'user_login':user_login,'user_not_login':user_not_login}
    return render(request,'app/home.html', context)






#region quiz

def create_custom_quiz(cust, num_questions):
    all_questions = Question.objects.all()

    # Đảm bảo số lượng câu hỏi không vượt quá số lượng câu hỏi có sẵn trong ngân hàng
    num_questions = min(num_questions, all_questions.count())

    random_questions = random.sample(list(all_questions), num_questions)

    quiz = Quiz.objects.create(quiz_name="test", start_time=datetime.now(), numberofQuestion=num_questions)  # Gán số lượng câu hỏi cho bài thi

    quiz.questions.set(random_questions)

    return quiz.questions
#endregion




def upload_quiz_excel_1(request):
    return render(request, 'app/upload_quiz_excel_1.html')

def generate_quizs(request):
    if request.method == 'POST':
        excel_file = request.FILES.get('excel_file')

        if excel_file.name.endswith(('.xls', '.xlsx')):
            # Đọc dữ liệu từ file Excel
            df = pd.read_excel(excel_file)

            for _, row in df.iterrows():
                user_id = row['user_id']
                course_id = row['course_id']
                total_correct = row['total']

                # Tạo bài thi tự động và chọn đáp án ngẫu nhiên
                create_quiz(user_id, course_id)
                select_answer_1(user_id,course_id,total_correct)

            return HttpResponse("Bài thi tự động đã được tạo từ file Excel.")
        else:
            return HttpResponse("Vui lòng tải lên file Excel hợp lệ.")
    else:
        return redirect('upload_quiz_excel')

def support(request):
    if request.method == 'POST':
        excel_file = request.FILES.get('excel_file')

        if excel_file.name.endswith(('.xls', '.xlsx')):
            # Đọc dữ liệu từ file Excel
            df = pd.read_excel(excel_file)

            for _, row in df.iterrows():
                user_id = row['user_id']
                course_id = row['course_id']
                number_of_correct = row['num']
                # select_answer(user_id,course_id)
                select_answer_1(user_id,course_id,number_of_correct)

            return HttpResponse("Hoàn thành.")
        else:
            return HttpResponse("Vui lòng tải lên file Excel hợp lệ.")
    else:
        return redirect('upload_excel')

def create_quiz(accountid,courseid):
    try:   
        course = Course.objects.get(id=courseid)    
        student = Student.objects.get(user__username=accountid)         
        myquiz = Quiz.objects.get(course__id=courseid,user__name=accountid)  
        pass        
    except ObjectDoesNotExist:
        course_cats = Course_Category.objects.filter(course_id=courseid)
        quiz_questions = []
        for c_c in course_cats:
            questions1 = Question.objects.filter(category=c_c.category)
            # Chọn ngẫu nhiên 5 câu hỏi            
            quiz_questions1 = sample(list(questions1),c_c.numberofquestion)
            quiz_questions = quiz_questions + quiz_questions1
        

        s_time = datetime.now()
        e_time = s_time + timedelta(minutes=course.timeofquiz)

        quiz = Quiz.objects.create(user=student, 
                                   quiz_name="Tên Bài Thi Của Bạn", 
                                   numberofQuestion=course.numberofquestion,
                                   course = course,
                                   start_time = s_time, 
                                   end_time = e_time )
        
        quiz.questions.set(quiz_questions)
        quiz.question_order = [question.id for question in quiz_questions]
        quiz.save()        
        
def select_answer(accountid,courseid):
    quiz =Quiz.objects.get(user__user__username=accountid, course__id=courseid)
    questions = quiz.questions.all()
    student = Student.objects.get(user__username=accountid)
    for ques in questions:        
        try:
            answer = Answer.objects.get(question__id=ques.id,is_correct=True)
            quiz_results = QuizResult.objects.get_or_create(
            quiz = quiz,
            user = student,
            question = ques,
            selected_answer = answer,
            is_correct = True,
        )
        except:
            print(ques.question_text + accountid)
    quiz.finish = True
    quiz.save()    

def select_answer_1(accountid,courseid,numberofcorrect):
    quiz =Quiz.objects.get(user__user__username=accountid, course__id=courseid)
    questions = quiz.questions.all()
    student = Student.objects.get(user__username=accountid)
    i =0
    for ques in questions:        
        i += 1
        if i<=numberofcorrect:
            try:
                answer = Answer.objects.get(question__id=ques.id,is_correct=True)
                quiz_results = QuizResult.objects.get_or_create(
                quiz = quiz,
                user = student,
                question = ques,
                selected_answer = answer,
                is_correct = True,
            )
            except:
                print(ques.question_text + accountid)
        else:
            try:
                answer = Answer.objects.get(question__id=ques.id,is_correct=False).first()
                quiz_results = QuizResult.objects.get_or_create(
                quiz = quiz,
                user = student,
                question = ques,
                selected_answer = answer,
                is_correct = True,
            )
            except:
                print(ques.question_text + accountid)
    quiz.finish = True
    quiz.save()    




def manage_question(request):    
    #quiz_questions = myquiz.questions.all()
    quiz_questions = Question.objects.all()
                    
    #selected_answers ={}
    answers = Answer.objects.all()

    context = {
        'quiz_questions': quiz_questions,  'answers': answers
    }                 
    return render(request, 'app/MagageQuestion.html', context)


def grading(score,exam_id):
    exam = Exam.objects.get(id=exam_id)

    if score < exam.satisfactory:
        return "Yếu"
    elif score < exam.good:
        return "Trung bình"
    elif score < exam.excellent:
        return "Khá"
    elif score < exam.outstanding:
        return "Giỏi"
    else:
        return "Xuất sắc"
    
def download_sample_file(request,tenmau):
    #file_path = os.path.join(settings.MEDIA_ROOT1, tenmau)  # Thay đổi đường dẫn đến file mẫu
    file_path = os.path.join(settings.BASE_DIR, 'app/media/'+tenmau)
    with open(file_path, 'rb') as file:
        response = HttpResponse(file.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=sample_file.xlsx'
        return response