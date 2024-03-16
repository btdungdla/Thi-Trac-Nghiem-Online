from django.contrib import admin
from django.urls import path
from . import views
from app.Views.views_users import * 
from app.Views.views_courses import *
from app.Views.views_exams import *
from app.Views.views_categorys import *
from app.Views.views_questions import *
from app.Views.views_quizs import *
from app.Views.view_questions import *

urlpatterns = [
    path('', views.home, name="home"),
    # path('register/', register, name="register"),
    path('login/', loginPage, name="login"),
    path('logout/', logoutPage, name="logout"),    
    path('search/', views.search, name="search"),
    path('CreateQuestion/', upload_word_file, name="CreateQuestion"),
    path('CreateQuestion/<int:categoryid>/', upload_word_file, name="CreateQuestion"),
    path('take-quiz/', take_quiz, name="take_quiz"),
    path('submit_quiz/', submit_quiz, name='submit_quiz'),
    path('courses/', GetCourse, name='courses'),
    path('save_answers/', save_answers, name='save_answers'),
    path('result/<int:quiz_id>/', ResultPage, name='result'),
    path('result/<int:quiz_id>/<int:usr>/', ResultPage, name='result_page_with_user'),
    path('Result_Course/', Result_Course, name="Result_Course"),
    path('add_course_category/<int:course_id>/', add_course_category, name='add_course_category'),
    path('manage_course/<int:exam_id>', manage_course, name="manage_course"),
    path('get_course_info/<int:course_id>/', get_course_info, name='get_course_info'),
    path('update_course/<int:course_id>/', update_course, name='update_course'),
    path('manage_exam/', manage_exam, name="manage_exam"),
    path('get_exam_info/<int:exam_id>/', get_exam_info, name='get_exam_info'),
    path('update_exam/<int:exam_id>/', update_exam, name='update_exam'),
    path('manage_category/<int:exam_id>', manage_category, name="manage_category"),
    path('get_category_info/<int:category_id>/', get_category_info, name='get_category_info'),
    path('update_category/<int:category_id>/', update_category, name='update_category'),
    path('questions_by_category/<int:category_id>/', questions_by_category, name='questions_by_category'),
    path('manage_questions/<int:category_id>/', manage_questions, name='manage_questions'),
    path('create_user/', create_user, name="create_user"),
    path('add_user_to_course/<int:course_id>/', add_user_to_course, name='add_user_to_course'),
    path('upload_quiz_excel/', upload_quiz_excel, name="upload_quiz_excel"),
    path('generate_quizs/', views.generate_quizs, name="generate_quizs"),
    path('check_question/', check_question, name="check_question"),
    path('upload_quiz_excel_1/', views.upload_quiz_excel_1, name="upload_quiz_excel_1"),
    path('support/', views.support, name="support"),
    path('member_course/<int:courseid>/', member_course, name="member_course"),
    path('delete_student/<str:student_id>/<int:course_id>/', delete_student_from_course, name='delete_student'),
    path('ajax_check_number_of_questions/', ajax_check_number_of_questions, name='ajax_check_number_of_questions'),
    path('result_dash_board/<int:exam_id>/', result_dash_board, name='result_dash_board'),
    path('info/', info, name='info'),
    path('change_password/', change_password, name='change_password'),
    path('export_result_to_excel/<int:exam_id>', export_result_to_excel, name='export_result_to_excel'),
    path('download_sample_file/<str:tenmau>', download_sample_file, name='download_sample_file'),
    path('question_by_id/<int:question_id>/', question_by_id, name='question_by_id'),
]

