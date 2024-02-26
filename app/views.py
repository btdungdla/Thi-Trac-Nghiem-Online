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
    products = Product.objects.all()
    context = {'products':products,'user_login':user_login,'user_not_login':user_not_login}
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

def upload_word_file(request, categoryid):
    cat = Category.objects.get(id=categoryid)
    if request.method == 'POST':
        #form = UploadWordFileForm(request.POST, request.FILES)
        form = UploadQuestionWordFileForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            # Xử lý tệp Word
            word_file = form.cleaned_data['word_file']
           
            doc = Document(word_file)

            current_question = None  # Dùng để theo dõi câu hỏi đang được xử lý
            is_answer = False  # Bắt đầu với giả định rằng đoạn văn bản không phải là câu trả lời

            for paragraph in doc.paragraphs:
                # Kiểm tra nếu đoạn văn bản không trống
                if paragraph.text.strip():
                    if re.match(r'^Câu \d+', paragraph.text.strip()):  # Xác định câu hỏi bắt đầu bằng "Câu"
                        question_text = re.sub(r'^Câu \d+\.', '', paragraph.text).strip()
                        current_question = Question.objects.create(question_text=question_text,category=cat)
                        is_answer = False  # Sau đó, đoạn tiếp theo sẽ không phải là câu trả lời
                    elif re.match(r'^[A-Da-d]\.|^[A-Da-d]\)', paragraph.text.strip()):  # Xác định đáp án bắt đầu bằng "A.", "B.", "C.", "D.", "A)", hoặc "B)"
                        answer_text = paragraph.text[2:].strip()  # Lấy phần sau của đáp án
                        is_correct = False
                        #answer_text = paragraph.text

                        for run in paragraph.runs:
                            if run.bold:
                                is_correct = True
                                #answer_text = run.text[2:].strip()
                                #answer_text = run.text

                        Answer.objects.create(question=current_question, answer_text=answer_text, is_correct=is_correct)
            messages.success(request, 'Đã tạo câu hỏi thành công.')
            
            return JsonResponse({'success': True})  # Trả về phản hồi JSON
    else:
        form = UploadQuestionWordFileForm()
   
    return render(request, 'app/upload_word_file.html', {'form': form,'exam_id':cat.exam.id,'category_id':cat.id})

def upload_quiz_excel(request):
    return render(request, 'app/upload_quiz_excel.html')

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

                select_answer(user_id,course_id)

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
        
        return JsonResponse({"message": "Đáp án đã được lưu lại from server."})
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

def manage_question(request):    
    #quiz_questions = myquiz.questions.all()
    quiz_questions = Question.objects.all()
                    
    #selected_answers ={}
    answers = Answer.objects.all()

    context = {
        'quiz_questions': quiz_questions,  'answers': answers
    }                 
    return render(request, 'app/MagageQuestion.html', context)


def add_course_category(request, course_id):
    course = Course.objects.get(id=course_id)
    categories = Category.objects.all()
    category_question_counts = {}
    for category in categories:
        course_category, created = Course_Category.objects.get_or_create(
            course=course,
            category=category,
            defaults={'numberofquestion': 0}
        )
        category_question_counts[category.category_name] = course_category.numberofquestion
    if request.method == 'POST':
        for category in categories:
            quantity_key = f'numberofquestion_{category.category_name}'
            # Sử dụng .get() để tránh KeyError và cung cấp giá trị mặc định là "0"
            quantity_value = request.POST.get(quantity_key, "0")

            # Sử dụng try-except để xử lý trường hợp quantity_value không phải là số
            try:
                quantity_value = int(quantity_value)
                if quantity_value >= 0:
                    course_category, created = Course_Category.objects.get_or_create(
                        course=course,
                        category=category,
                        defaults={'numberofquestion': quantity_value}
                    )
                    if not created:
                        course_category.numberofquestion = quantity_value
                        course_category.save()
            except ValueError:
                # Xử lý lỗi nếu quantity_value không phải là số
                # Ví dụ: thông báo lỗi cho người dùng hoặc ghi log
                print(f"Giá trị nhập cho {category.category_name} không phải là số hợp lệ.")
                
        return HttpResponse('Đã cập nhật thành công')

    else:
        form = CourseCategoryForm()

    context = {'course': course, 'categories': categories, 'category_question_counts': category_question_counts}
    return render(request, 'app/add_course_category.html', context)


def get_course_info(request, course_id):
    if request.user.is_authenticated:
        if request.user.is_staff:
            course = Course.objects.get(id=course_id)
            data = {
                'course_name': course.course_name,
                'numberofquestion': course.numberofquestion,
                'status': course.status,
                'timeofquiz': course.timeofquiz,
            }
            return JsonResponse(data)
        else:
            return HttpResponse("Bạn không có quyền thực hiện chức năng này")
    else:
        return redirect("/login/")
    
def update_course(request, course_id):
    if request.user.is_authenticated:
        if request.user.is_staff:
            course = Course.objects.get(id=course_id)
            exam = course.exam
            if request.method == 'POST':
                form = CourseForm(request.POST, instance=course)
                print(form.errors)
                if form.is_valid():
                    form.instance.exam = exam
                    form.save()
                    data = {'success': True}
                else:
                    data = {'success': False, 'errors': form.errors}
                return JsonResponse(data)
        else:
            return HttpResponse("Bạn không có quyền thực hiện chức năng này")
    else:
        return redirect("/login/")




    
def manage_category(request, exam_id):
    if request.user.is_authenticated:
        if request.user.is_staff:
            exam = Exam.objects.get(id=exam_id)
            try:
                categorys = Category.objects.filter(exam__id = exam_id)
            except ValueError:
                categorys = None
            if request.method == 'POST':
                form = CategoryForm(request.POST)
                if form.is_valid():
                    # Thêm giá trị của exam vào form trước khi lưu
                    form.instance.exam = Exam.objects.get(id=exam_id)
                    form.save()
                    return redirect('manage_category', exam_id=exam_id)
            else:
                form = CategoryForm()

            context = {'categorys': categorys, 'form': form, 'exam': exam}
            return render(request, 'app/manage_category.html', context)
        else:
            return HttpResponse("Bạn không có quyền thực hiện chức năng này")
    else:
        return redirect("/login/")
    
def get_category_info(request, category_id):
    if request.user.is_authenticated:
        if request.user.is_staff:
            category = Category.objects.get(id=category)
            data = {
                'exam_name': category.category_name,
                'status': category.status,
            }
            return JsonResponse(data)
        else:
            return HttpResponse("Bạn không có quyền thực hiện chức năng này")
    else:
        return redirect("/login/")
    
def update_category(request, category_id):
    if request.user.is_authenticated:
        if request.user.is_staff:
            category = Category.objects.get(id=category_id)
            if request.method == 'POST':
                form = CategoryForm(request.POST, instance=category)
                if form.is_valid():
                    form.instance.exam = category.exam
                    form.save()
                    data = {'success': True}
                else:
                    data = {'success': False, 'errors': form.errors}
                return JsonResponse(data)
        else:
            return HttpResponse("Bạn không có quyền thực hiện chức năng này")
    else:
        return redirect("/login/")
    
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


def create_user(request):
     if request.user.is_authenticated:
        if request.user.is_staff:
            if request.method == 'POST' and request.FILES['excel_file']:
                excel_file = request.FILES['excel_file']

                try:
                    df = pd.read_excel(excel_file)

                    for _, row in df.iterrows():
                        # Tạo người dùng
                        user = User.objects.create_user(username=row['username'], password=row['password'])

                        # Tạo sinh viên
                        student = Student.objects.create(user=user, name=row['name'], email=row['email'], department = row['department'])

                    messages.success(request, 'Đã tạo người dùng và sinh viên thành công từ file Excel.')
                    return HttpResponse('Đã tạo người dùng thành công')  # Chuyển hướng đến trang thành công

                except Exception as e:
                    messages.error(request, f'Có lỗi xảy ra: {str(e)}')
                    return HttpResponse('Lỗi')  # Chuyển hướng đến trang lỗi

            return render(request, 'app/process_excel.html')

def handle_uploaded_file(file, course_id):   
    # Đọc dữ liệu từ file Excel bằng pandas
    df = pd.read_excel(file)

    # Lặp qua từng hàng trong DataFrame và tạo bản ghi mới trong bảng Course_Student
    for index, row in df.iterrows():
        username = row['username']  # Điều này phụ thuộc vào cột trong file Excel
        user = Student.objects.get(user__username=username)  # Thay đổi tùy thuộc vào cách bạn lưu thông tin người dùng

        # Tạo Course_Student mới
        Course_Student.objects.create(user=user, Course_id=course_id)

def add_user_to_course(request, course_id):
     if request.user.is_authenticated:
        if request.user.is_staff:
            if request.method == 'POST':
                form = ExcelUploadForm(request.POST, request.FILES)
                if form.is_valid():
                    excel_file = request.FILES['excel_file']
                    handle_uploaded_file(excel_file, course_id)
                    return HttpResponse('Thêm thành công')  # Chuyển hướng đến trang thành công hoặc trang khác
            else:
                form = ExcelUploadForm()
            course = Course.objects.get(id=course_id)
            return render(request, 'app/upload_excel.html', {'form': form, 'course_id': course_id,'course':course})
        
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

def member_course(request, courseid, additional_param=None):    
    if request.user.is_authenticated:
        if request.user.is_staff:
            course = Course.objects.get(id=courseid)
            students_in_course = Student.objects.filter(course_student__Course__id=courseid)            
            page = request.GET.get('page')
            search_name = request.GET.get('search_name')  # Thêm biến tìm kiếm
            search_department = request.GET.get('search_department')                         
            if students_in_course is not None:    
                if search_name:
                    students_in_course = students_in_course.filter(name__icontains=search_name)
                else:
                    search_name = ""
                if search_department:
                    students_in_course = students_in_course.filter(course_student__Course__course_name__icontains=search_department)
                else:
                    search_department = ""
               
                items_per_page = 3
                paginator = Paginator(students_in_course, items_per_page)

                try:
                    students_in_course = paginator.page(page)
                except PageNotAnInteger:
                    students_in_course = paginator.page(1)
                except EmptyPage:
                    students_in_course = paginator.page(paginator.num_pages)

                context = {
                    'students':students_in_course,
                    'course': course,
                    'additional_param': additional_param,  
                    'search_name': search_name,
                    'search_department': search_department,
                }
                return render(request, 'app/member_course.html', context)            
            else:
                return HttpResponse("Không có thi sinh trong nhóm này")
        else:
            return HttpResponse("Bạn không có quyền thực hiện chức năng này")
    else:
        return redirect("/login/")      

def delete_student_from_course(request, student_id, course_id):
    if request.user.is_authenticated:
        if request.user.is_staff:
            try:
               course_student = Course_Student.objects.get(user__user__username = student_id, Course__id = course_id)
               course_student.delete()
            except Course_Student.DoesNotExist:
                pass  # Nếu không tìm thấy, không làm gì cả

            return redirect('member_course', courseid=course_id)
        else:
            return HttpResponse("Bạn không có quyền thực hiện chức năng này")
    else:
        return redirect("/login/")    
    
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



def info(request):
    if request.user.is_authenticated:
        student = Student.objects.get(user=request.user)
        course = Course.objects.get(course_student__Course__status = True, course_student__user = student)
        course_name = course.course_name
        context ={
            'student':student,
            'course_name':course_name
        }
        return render(request,"app/info.html",context)
    else:
        return redirect("/login/")



def export_result_to_excel(request,exam_id):
    # Xử lý tra cứu (thay thế bằng mã của bạn)
    quizs = Quiz.objects.filter(course__exam__id = exam_id)

    # Tạo workbook và worksheet
    wb = openpyxl.Workbook()
    ws = wb.active

    # Ghi dòng tiêu đề
    header = ['Phòng/CCT', 'Tên', 'Nhóm', 'Kết quả','Xếp loại']
    ws.append(header)

    # Ghi dữ liệu
    for row in quizs:
        row_data = [
            str(row.user.department),
            str(row.user.name),
            str(row.course.course_name),
            row.Total_Correct_Answer,
            str(grading(row.Total_Correct_Answer,exam_id))
        ]
        ws.append(row_data)

    # Tạo HttpResponse
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=result.xlsx'
    wb.save(response)

    return response

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