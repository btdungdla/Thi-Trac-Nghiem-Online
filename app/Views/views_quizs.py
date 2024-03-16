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

def take_quiz(request):
    if request.method=="POST":
        courseid = request.POST.get('CourseID')
        mycourse = Course.objects.get(id=courseid)
        if courseid is not None:      
            try:                
                myquiz = Quiz.objects.get(course=mycourse,user=request.user.student)  
                
                if myquiz.finish == True:
                    return redirect("result",myquiz.id)    
                else:
                    #quiz_questions = myquiz.questions.all()
                    quiz_questions = Question.objects.filter(id__in=myquiz.question_order)
                    
                    #selected_answers ={}
                    selected_answers = get_selected_answers_for_quiz(myquiz, request.user.student)

                    context = {
                        'quiz_questions': quiz_questions, "course": mycourse, 'quiz': myquiz, 'selected_answers': selected_answers
                    }
                    # Lưu danh sách câu hỏi trong session
                    request.session['quiz_questions'] = [question.id for question in quiz_questions]
                    request.session['courseid'] = [courseid]                  
                    return render(request, 'app/quiz.html', context) 
            except ObjectDoesNotExist:
                course_cats = Course_Category.objects.filter(course_id=courseid)
                quiz_questions = []
                for c_c in course_cats:
                    questions1 = Question.objects.filter(category=c_c.category)
                    # Chọn ngẫu nhiên 5 câu hỏi            
                    quiz_questions1 = sample(list(questions1),c_c.numberofquestion)
                    quiz_questions = quiz_questions + quiz_questions1
                

                s_time = datetime.now()
                e_time = s_time + timedelta(minutes=mycourse.timeofquiz)

                quiz = Quiz.objects.create(user=request.user.student, quiz_name="Tên Bài Thi Của Bạn", numberofQuestion=mycourse.numberofquestion,course = mycourse,
                                           start_time = s_time, end_time = e_time )
                
                quiz.questions.set(quiz_questions)
                quiz.question_order = [question.id for question in quiz_questions]
                quiz.save()
                quiz_questions = Question.objects.filter(id__in=quiz.question_order)
                context = {
                    'quiz_questions': quiz_questions, "course":mycourse,'quiz': quiz
                }
                
                request.session['quiz_questions'] = [question.id for question in quiz_questions]
                request.session['courseid'] = [courseid]  # Lưu danh sách câu hỏi trong session
                
                return render(request, 'app/quiz.html', context)            
        else:
            return render(request, 'app/quiz.html', context)
            #return JsonResponse('add',safe=False)
    return render(request, 'app/quiz.html', context)



def save_answers(request):    
    if request.method == 'POST':# and request.META.get("HTTP_X_REQUESTED_WITH") == "XMLHttpRequest":
        # Lấy dữ liệu đáp án đã chọn từ JSON được gửi bằng phương thức POST
        #return JsonResponse({"message": "Đáp án đã được lưu lại."})
        #count = 0        
        selected_answers = json.loads(request.body)
        quiz_id = request.GET.get('quiz_id')                        
        myquiz = Quiz.objects.get(id=quiz_id)
        
        # Xử lý và lưu đáp án đã chọn vào cơ sở dữ liệu
        for question_id, selected_answer_id in selected_answers.items():
            
            question = Question.objects.get(id=question_id)
            selected_answer = Answer.objects.get(pk=selected_answer_id)
            is_correct = selected_answer.is_correct

                # Lưu kết quả quiz vào cơ sở dữ liệu
            quiz_result, created = QuizResult.objects.get_or_create(
                quiz=myquiz,
                user=request.user.student,
                question=question,
                selected_answer=selected_answer,
            )
            quiz_result.is_correct = is_correct
            quiz_result.save()
        
        return JsonResponse({"message": "Đáp án đã được lưu lại"})
    else:
        return JsonResponse({"error": "Yêu cầu không hợp lệ."}, status=400)
    
def submit_quiz(request):
    if request.method == 'POST':
        # Lấy danh sách câu hỏi từ session
        quiz_question_ids = request.session.get('quiz_questions')
        courseid = request.session.get('courseid')
        quiz_id = request.GET.get('quiz_id')                        
        myquiz = Quiz.objects.get(id=quiz_id)
        score = 0
        if myquiz.finish == False:            
            #cse = Course.objects.get(id=myquiz.course.id)
            totalQuestion = Course.objects.get(id=myquiz.course.id).numberofquestion
            if quiz_question_ids:
                # Lấy dữ liệu đáp án đã chọn từ JSON được gửi bằng phương thức POST
                selected_answers = json.loads(request.body)

                # Tính điểm và cập nhật quiz_result hoặc tạo mới nếu chưa có
                for question_id, selected_answer_id in selected_answers.items():
                    question = Question.objects.get(id=question_id)
                    selected_answer = Answer.objects.get(pk=selected_answer_id)
                    is_correct = selected_answer.is_correct

                    # Kiểm tra xem quiz_result đã tồn tại chưa
                    quiz_result, created = QuizResult.objects.get_or_create(
                    quiz=myquiz,
                    user=request.user.student
                    ,
                    question=question,
                    selected_answer=selected_answer,
                    is_correct = selected_answer.is_correct,      
                    )

                    
                    if selected_answer.is_correct:
                        score += 1
                    """ try:
                        quiz_result = QuizResult.objects.get(user=request.user.customer, question=question)
                    except QuizResult.DoesNotExist:
                        quiz_result = QuizResult(user=request.user.customer, question=question)

                    quiz_result.selected_answer = selected_answer
                    quiz_result.is_correct = is_correct
                    quiz_result.save() """

                myquiz.finish = True
                myquiz.save()
                # Xóa danh sách câu hỏi khỏi session sau khi đã xử lý
                del request.session['quiz_questions']
                del request.session['courseid']

                return JsonResponse({"message": "Bài thi đã được nộp thành công.","score":score,"totalquestion":totalQuestion})
            else:
                return JsonResponse({"error": "Không có dữ liệu bài thi để nộp."}, status=400)
        else:
            score = myquiz.Total_Correct_Answer
            totalQuestion = myquiz.numberofQuestion
            return JsonResponse({"message": "Bài thi đã được nộp thành công.","score":score,"totalquestion":totalQuestion})
    else:
        return JsonResponse({"error": "Yêu cầu không hợp lệ."}, status=400)
    
#def ResultPage(request,quiz_id):
def ResultPage(request, quiz_id, usr=None):
    myquiz = Quiz.objects.get(id=quiz_id)
    mycourse = Course.objects.get(id=myquiz.course.id)
    quiz_questions = Question.objects.filter(id__in=myquiz.question_order)
    if usr is None:
        usr = request.user.student
    selected_answers = get_selected_answers_for_quiz(myquiz, usr)
    correctanswers = {}
    
    for q in quiz_questions:
        correct_answer = Answer.objects.get(question=q, is_correct=True)
        correctanswers[q.id] = correct_answer.id
    context = {
        'quiz_questions': quiz_questions, "course": mycourse, 'quiz': myquiz, 'correctanswers': correctanswers,'selected_answers':selected_answers
    }
    return render(request,"app/Result_Page.html",context)

def get_selected_answers_for_quiz(quiz, user):
    selected_answers = {}  # Khởi tạo một từ điển để lưu các đáp án đã chọn

    # Lấy tất cả kết quả bài thi của người dùng cho bài thi cụ thể
    quiz_results = QuizResult.objects.filter(quiz=quiz, user=user)

    # Duyệt qua từng kết quả bài thi và lấy đáp án đã chọn
    i = 0
    for quiz_result in quiz_results:
        question_id = quiz_result.question.id
        selected_answer_id = quiz_result.selected_answer.id
        selected_answers[selected_answer_id] = selected_answer_id

    return selected_answers