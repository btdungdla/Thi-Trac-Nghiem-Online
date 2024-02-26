from django.contrib import admin
from django.urls import path
from . import views
from app.Views.views_users import * 
from app.Views.views_courses import *
from app.Views.views_exams import *

urlpatterns = [
    path('', views.home, name="home"),
    path('register/', register, name="register"),
    path('login/', loginPage, name="login"),
    path('logout/', logoutPage, name="logout"),    
    path('search/', views.search, name="search"),
    path('CreateQuestion/', views.upload_word_file, name="CreateQuestion"),
    path('CreateQuestion/<int:categoryid>/', views.upload_word_file, name="CreateQuestion"),
    path('take-quiz/', views.take_quiz, name="take_quiz"),
    path('submit_quiz/', views.submit_quiz, name='submit_quiz'),
    path('courses/', GetCourse, name='courses'),
    path('save_answers/', views.save_answers, name='save_answers'),
    path('result/<int:quiz_id>/', views.ResultPage, name='result'),
    path('result/<int:quiz_id>/<int:usr>/', views.ResultPage, name='result_page_with_user'),
    path('Result_Course/', Result_Course, name="Result_Course"),
    path('add_course_category/<int:course_id>/', views.add_course_category, name='add_course_category'),
    path('manage_course/<int:exam_id>', manage_course, name="manage_course"),
    path('get_course_info/<int:course_id>/', views.get_course_info, name='get_course_info'),
    path('update_course/<int:course_id>/', views.update_course, name='update_course'),
    path('manage_exam/', manage_exam, name="manage_exam"),
    path('get_exam_info/<int:exam_id>/', get_exam_info, name='get_exam_info'),
    path('update_exam/<int:exam_id>/', update_exam, name='update_exam'),
    path('manage_category/<int:exam_id>', views.manage_category, name="manage_category"),
    path('get_category_info/<int:category_id>/', views.get_category_info, name='get_category_info'),
    path('update_category/<int:category_id>/', views.update_category, name='update_category'),
    path('questions_by_category/<int:category_id>/', views.questions_by_category, name='questions_by_category'),
    path('manage_questions/<int:category_id>/', views.manage_questions, name='manage_questions'),
    path('create_user/', views.create_user, name="create_user"),
    path('add_user_to_course/<int:course_id>/', views.add_user_to_course, name='add_user_to_course'),
    path('upload_quiz_excel/', views.upload_quiz_excel, name="upload_quiz_excel"),
    path('generate_quizs/', views.generate_quizs, name="generate_quizs"),
    path('check_question/', views.check_question, name="check_question"),
    path('upload_quiz_excel_1/', views.upload_quiz_excel_1, name="upload_quiz_excel_1"),
    path('support/', views.support, name="support"),
    path('member_course/<int:courseid>/', views.member_course, name="member_course"),
    path('delete_student/<str:student_id>/<int:course_id>/', views.delete_student_from_course, name='delete_student'),
    path('ajax_check_number_of_questions/', views.ajax_check_number_of_questions, name='ajax_check_number_of_questions'),
    path('result_dash_board/<int:exam_id>/', result_dash_board, name='result_dash_board'),
    path('info/', views.info, name='info'),
    path('change_password/', change_password, name='change_password'),
    path('export_result_to_excel/<int:exam_id>', views.export_result_to_excel, name='export_result_to_excel'),
    path('download_sample_file/<str:tenmau>', views.download_sample_file, name='download_sample_file'),
    path('question_by_id/<int:question_id>/', views.question_by_id, name='question_by_id'),
]

