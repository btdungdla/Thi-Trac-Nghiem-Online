from django import forms
from .models import *
from django.contrib.auth.forms import PasswordChangeForm

class UploadWordFileForm(forms.Form):
    word_file = forms.FileField()     
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        #empty_label="Chọn danh mục"  # Đổi văn bản trong danh sách thả xuống theo ý của bạn
    )
    

    def __init__(self, categoryid, *args, **kwargs):
        super(UploadWordFileForm, self).__init__(*args, **kwargs)
        #c_cats = Course_Category.objects.filter(course_id=course_id)
        #cat_ids = c_cats.values_list('category_id', flat=True)        
        #self.fields['category'].queryset = Category.objects.filter(id__in=cat_ids)
        self.fields['category'].queryset = Category.objects.filter(id=categoryid)

 
  
class UploadQuestionWordFileForm1(forms.Form):
    word_file = forms.FileField()     
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        #empty_label="Chọn danh mục"  # Đổi văn bản trong danh sách thả xuống theo ý của bạn
    )
    

    def __init__(self, examid, *args, **kwargs):
        super(UploadQuestionWordFileForm1, self).__init__(*args, **kwargs)
        #c_cats = Course_Category.objects.filter(course_id=course_id)
        #cat_ids = c_cats.values_list('category_id', flat=True)        
        #self.fields['category'].queryset = Category.objects.filter(id__in=cat_ids)
        self.fields['category'].queryset = Category.objects.filter(exam__id=examid)

class UploadQuestionWordFileForm(forms.Form):
    word_file = forms.FileField()     


class CourseCategoryForm(forms.ModelForm):
    class Meta:
        model = Course_Category
        fields = ['numberofquestion']


# Trong CourseForm
class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['course_name', 'numberofquestion', 'status', 'timeofquiz', 'exam']

    def __init__(self, *args, **kwargs):
        # Nhận đối tượng 'exam' từ kwargs nếu có
        exam = kwargs.pop('exam', None)

        super(CourseForm, self).__init__(*args, **kwargs)

        # Mặc định trạng thái là True (checked)
        self.fields['status'].initial = True

        # Nếu có đối tượng 'exam', thì thiết lập giá trị của trường 'exam'
        if exam:
            self.fields['exam'].initial = exam

        # Đặt required=False cho trường exam
        self.fields['exam'].required = False


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['category_name', 'status','exam']

    def __init__(self, *args, **kwargs):
        # Nhận đối tượng 'exam' từ kwargs nếu có
        exam = kwargs.pop('exam', None)

        super(CategoryForm, self).__init__(*args, **kwargs)

        # Mặc định trạng thái là True (checked)
        self.fields['status'].initial = True

        # Nếu có đối tượng 'exam', thì thiết lập giá trị của trường 'exam'
        if exam:
            self.fields['exam'].initial = exam

        # Đặt required=False cho trường exam
        self.fields['exam'].required = False


    

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['category_name', 'status']


class ExamForm(forms.ModelForm):
    class Meta:
        model = Exam
        fields = ['exam_name', 'year', 'status','outstanding','excellent','good','satisfactory']


class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['answer_text', 'is_correct']
        widgets = {
            'answer_text': forms.Textarea(attrs={'rows': 2, 'cols': 70}),
        }

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['question_text']
        widgets = {
            'question_text': forms.Textarea(attrs={'rows': 3, 'cols': 70}),
        }

    correct_answer = forms.ModelChoiceField(
        queryset=Answer.objects.none(),
        widget=forms.RadioSelect,
        empty_label=None,
    )

    def __init__(self, *args, **kwargs):
        super(QuestionForm, self).__init__(*args, **kwargs)
        # Thiết lập queryset cho correct_answer
        if 'instance' in kwargs:
            question = kwargs['instance']
            self.fields['correct_answer'].queryset = question.answer_set.all()


class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        label="Mật khẩu cũ",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )
    new_password1 = forms.CharField(
        label="Mật khẩu mới",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )
    new_password2 = forms.CharField(
        label="Nhập lại mật khẩu mới",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )