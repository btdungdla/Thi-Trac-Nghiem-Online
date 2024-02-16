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

class Customer(models.Model):
    user = models.OneToOneField(User,on_delete=models.SET_NULL,null=True,blank=False)
    name = models.CharField(max_length=200,null=True)
    email = models.CharField(max_length=200,null=True)

    def __str__(self):
        return self.name

class Student(models.Model):
    user = models.OneToOneField(User,on_delete=models.SET_NULL,null=True,blank=False)
    name = models.CharField(max_length=200,null=True)
    email = models.CharField(max_length=200,null=True)    
    department = models.CharField(max_length=200,null=True)
    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=200,null=True)
    price = models.FloatField()
    digital = models.BooleanField(default=False, null=True,blank=False)
    image = models.ImageField(null=True,blank=True)

    def __str__(self):
        return self.name
    
    @property
    def ImageURL(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url
    
class Order(models.Model):
    customer = models.ForeignKey(Customer,on_delete=models.SET_NULL,blank=True,null=True)
    date_order = models.DateTimeField(auto_now_add=True)
    complete = models.BooleanField(default=False)
    transaction_id = models.CharField(max_length=200,null=True)
   

    def __str__(self):
        return str(self.id)
    
    @property
    def Total_Quantity(self):
        order_items = self.orderitem_set.all()
        total = sum([item.quantity for item in order_items])
        return total
    
    @property
    def Total_Bill(self):
        order_items = self.orderitem_set.all()
        total = sum([item.total_item for item in order_items])
        return total
    
class OrderItem(models.Model):
    product = models.ForeignKey(Product,on_delete=models.SET_NULL,blank=True,null=True)
    order = models.ForeignKey(Order,on_delete=models.SET_NULL,blank=True,null=True)
    quantity = models.IntegerField(default=1)
    date_added = models.DateTimeField(auto_now_add=True)

    @property
    def total_item(self):
        total = self.quantity * self.product.price
        return total
  
class ShippingAddress(models.Model):
    customer = models.ForeignKey(Customer,on_delete=models.SET_NULL,blank=True,null=True)
    order = models.ForeignKey(Order,on_delete=models.SET_NULL,blank=True,null=True)
    address = models.CharField(max_length=200)
    city = models.CharField(max_length=200)
    state = models.CharField(max_length=200)
    mobile = models.CharField(max_length=200)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.address
    
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



    
