import datetime
from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django import forms
import random
import pandas as pd
from django.shortcuts import render, redirect
from django.contrib import messages

# Create your models here.
class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username','email','first_name','last_name','password1','password2']


class Student(models.Model):
    user = models.OneToOneField(User,on_delete=models.SET_NULL,null=True,blank=False)
    name = models.CharField(max_length=200,null=True)
    email = models.CharField(max_length=200,null=True)    
    department = models.CharField(max_length=200,null=True)
    organization = models.CharField(max_length=200,null=True)
    def __str__(self):
        return self.name


    
class Exam(models.Model):
    exam_name = models.CharField(max_length=200)
    year=models.IntegerField()
    status=models.BooleanField(default=True)
    outstanding = models.IntegerField()
    excellent = models.IntegerField()
    good = models.IntegerField()
    satisfactory = models.IntegerField()
    def __str__(self):
        return f"{self.exam_name} - {self.id}"

class Course(models.Model):
    course_name = models.CharField(max_length=200)
    numberofquestion = models.IntegerField()
    status = models.BooleanField()
    timeofquiz = models.IntegerField()
    exam =models.ForeignKey(Exam, on_delete=models.CASCADE)
    def __str__(self):
        return f"{self.course_name} - {self.id}"

class Category(models.Model):
    category_name = models.CharField(max_length=200)
    status = models.BooleanField(default=True)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE,default=None)
    @property
    def numberofQuestion(self):
        # Sử dụng self.question_set.count() để tính số lượng câu hỏi trong danh mục
        return self.question_set.count()
    
    def __str__(self):
        return f"{self.category_name } - {self.id}"
class Course_Category(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    numberofquestion = models.IntegerField(default=0)
    def __str__(self):
        return f"{self.course.course_name} - {self.category.category_name}"

class Course_Student(models.Model):
    user = models.ForeignKey(Student, on_delete=models.CASCADE)
    Course = models.ForeignKey(Course, on_delete=models.CASCADE,null=True)
    

class Question(models.Model):
    question_text = models.TextField()
    category = models.ForeignKey(Category,on_delete=models.CASCADE,null=True)
    def __str__(self):
        return f"{self.question_text} - {self.id}"
    
class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer_text = models.TextField()
    is_correct = models.BooleanField(default=False)
    def __str__(self):
        return f"{self.question.question_text} - {self.question.id}"
class Quiz(models.Model):
    user = models.ForeignKey(Student, on_delete=models.CASCADE,blank=True,null=True)
    course = models.ForeignKey(Course,on_delete=models.CASCADE,blank=True,null=True)
    quiz_name = models.CharField(max_length=200)
    questions = models.ManyToManyField(Question)  # Liên kết với các câu hỏi
    start_time = models.DateTimeField(null=True, blank=True)  # Thời gian bắt đầu (tùy chọn)
    end_time = models.DateTimeField(null=True, blank=True)    # Thời gian kết thúc (tùy chọn)
    numberofQuestion = models.IntegerField()
    finish = models.BooleanField(default=False)
    question_order = models.JSONField(null=True, blank=True)

    def __str__(self):
        return self.quiz_name
 
    @property
    def Total_Correct_Answer(self):
        total = 0
        quizresults = self.quizresult_set.all()
        for qr in quizresults:
            if qr.is_correct:
                total += 1
        return total

class QuizResult(models.Model):
    quiz = models.ForeignKey(Quiz,on_delete=models.CASCADE,blank=True,null=True)
    user = models.ForeignKey(Student, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_answer = models.ForeignKey(Answer, on_delete=models.CASCADE)
    is_correct = models.BooleanField(default=False)

class ExcelUploadForm(forms.Form):
    excel_file = forms.FileField()



    
