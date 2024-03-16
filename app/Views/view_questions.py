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


def manage_questions(request, category_id):
    category = Category.objects.get(id=category_id)
    questions = Question.objects.filter(category=category).prefetch_related('answer_set')
    forms_data = []

    if request.method == 'POST':
        for question in questions:
            question_form = QuestionForm(request.POST, instance=question, prefix=f'question_{question.pk}')
            answer_forms = [AnswerForm(request.POST, instance=answer, prefix=f'answer_{answer.pk}') for answer in question.answer_set.all()]

            if question_form.is_valid() and all(answer_form.is_valid() for answer_form in answer_forms):
                question_instance = question_form.save(commit=False)
                question_instance.save()

                # Lưu đáp án và cập nhật giá trị is_correct
                correct_answer_id = request.POST.get(f'correct_answer_{question.pk}')
                for answer_form in answer_forms:
                    answer_instance = answer_form.save(commit=False)
                    answer_instance.is_correct = str(answer_instance.id) == correct_answer_id
                    answer_instance.save()

        return redirect('manage_questions', category_id=category_id)
    else:
        for question in questions:
            question_form = QuestionForm(instance=question, prefix=f'question_{question.pk}')
            answer_forms = [AnswerForm(instance=answer, prefix=f'answer_{answer.pk}') for answer in question.answer_set.all()]
            forms_data.append((question, question_form, answer_forms))  # Tuple gồm Question, QuestionForm và danh sách AnswerForms

    context = {'category': category, 'forms_data': forms_data}
    return render(request, 'app/manage_question.html', context)

def questions_by_category(request, category_id):
    category = Category.objects.get(id=category_id)
    questions = Question.objects.filter(category=category).prefetch_related('answer_set')
    forms_data = []

    if request.method == 'POST':
        for question in questions:
            question_form = QuestionForm(request.POST, instance=question, prefix=f'question_{question.pk}')
            answer_forms = [AnswerForm(request.POST, instance=answer, prefix=f'answer_{answer.pk}') for answer in question.answer_set.all()]
            if question_form.is_valid() and all(answer_form.is_valid() for answer_form in answer_forms):
                question_instance = question_form.save()
                correct_answer_id = request.POST.get(f'{question_form.prefix}-correct_answer')
                for answer_form in answer_forms:
                    answer_instance = answer_form.save(commit=False)
                    answer_instance.is_correct = str(answer_instance.id) == correct_answer_id
                    answer_instance.save()

        return redirect('questions_by_category', category_id=category_id)
    else:
        for question in questions:
            question_form = QuestionForm(instance=question, prefix=f'question_{question.pk}')
            answer_forms = [AnswerForm(instance=answer, prefix=f'answer_{answer.pk}') for answer in question.answer_set.all()]
            forms_data.append((question_form, answer_forms))

    context = {'category': category, 'forms_data': forms_data}
    return render(request, 'app/questions_by_category.html', context)

def question_by_id(request, question_id):
    question = Question.objects.get(id=question_id)
    forms_data = []

    if request.method == 'POST':
        question_form = QuestionForm(request.POST, instance=question, prefix=f'question_{question.pk}')
        answer_forms = [AnswerForm(request.POST, instance=answer, prefix=f'answer_{answer.pk}') for answer in question.answer_set.all()]
        if question_form.is_valid() and all(answer_form.is_valid() for answer_form in answer_forms):
            question_instance = question_form.save()
            correct_answer_id = request.POST.get(f'{question_form.prefix}-correct_answer')
            for answer_form in answer_forms:
                answer_instance = answer_form.save(commit=False)
                answer_instance.is_correct = str(answer_instance.id) == correct_answer_id
                answer_instance.save()

        return redirect('question_by_id', question_id=question_id)
    else:       
        question_form = QuestionForm(instance=question, prefix=f'question_{question.pk}')
        answer_forms = [AnswerForm(instance=answer, prefix=f'answer_{answer.pk}') for answer in question.answer_set.all()]
        forms_data.append((question_form, answer_forms))

    context = {'question_id': question_id, 'forms_data': forms_data}
    return render(request, 'app/question_by_id.html', context)




def check_question(request):
    # Lấy tất cả câu hỏi không có đáp án
    questions_without_correct_answers = Question.objects.exclude(
        Q(answer__is_correct=True) | Q(answer__isnull=True)
    ).distinct().filter(answer__isnull=False)

    # Lấy tất cả câu hỏi có ít nhất một đáp án đúng
    questions_with_multiple_correct_answers = Question.objects.annotate(
            num_correct_answers=Count('answer', filter=Q(answer__is_correct=True))
        ).filter(num_correct_answers__gte=2)

    context = {
        'questions_without_correct_answers': questions_without_correct_answers,
        'questions_with_multiple_correct_answers': questions_with_multiple_correct_answers,
    }

    return render(request, 'app/check_question.html', context)


    
def ajax_check_number_of_questions(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        course_id = data.get('course_id')        
        number_of_questions = data.get('number_of_questions')
        course = Course.objects.get(id=course_id)
        if course.numberofquestion != number_of_questions:
            is_valid = False
        else:
            is_valid  = True
        response_data = {'is_valid': is_valid}
        return JsonResponse(response_data)

    return JsonResponse({'error': 'Invalid request method'})

