from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import *

# Register your models here.
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

def reset_password(modeladmin, request, queryset):
    for user in queryset:
        # Đặt lại mật khẩu cho người dùng
        new_password = 'Abc@1234'  # Thay thế bằng mật khẩu mới mong muốn
        user.set_password(new_password)
        user.save()

reset_password.short_description = "Reset mật khẩu cho người dùng đã chọn"

class CustomUserAdmin(UserAdmin):
    actions = [reset_password]  # Thêm action vào danh sách actions

# Đăng ký UserAdmin với mô hình User
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)