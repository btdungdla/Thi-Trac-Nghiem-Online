from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Customer)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(QuizResult)
admin.site.register(Quiz)
admin.site.register(Exam)
admin.site.register(Course)
admin.site.register(Category)
admin.site.register(Student)
admin.site.register(Course_Category)
admin.site.register(Course_Student)
