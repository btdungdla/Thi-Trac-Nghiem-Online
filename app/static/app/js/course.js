var updateBtns = document.getElementsByClassName('take-quiz')

for(i=0; updateBtns.length; i++)
{
    console.log(i)
    updateBtns[i].addEventListener('click',function(){
        var courseid = this.dataset.course
        var action = this.dataset.action
        courseid = 1
        //console.log(productid, "từ user:",user)
        if(user === "AnonymousUser")
        {
            console.log("a")
        }
        else
        {
            console.log("a")
            goToTakeQuiz1(courseid,action)
        }
    })
}

function goToTakeQuiz1(courseid,action) {
    // Tìm biểu mẫu POST
    const postForm = document.getElementById('postForm');
    
    // Thiết lập giá trị cho các trường dữ liệu ẩn
    if (postForm) {
        console.log(courseid)
        
        postForm.submit();
    } else {
        console.error('Không tìm thấy biểu mẫu POST.');
    }
}

function TakeQuiz(courseid,action)
{
    var url ="/take-quiz1/"
    fetch(url,{
        method: 'POST',
        headers: {
            'Content-Type':'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({'CourseId':courseid})
    })
    .then(response => response.text()) // Chuyển đổi nội dung thành văn bản HTML
    .then(html => {
        // Hiển thị trang web trong một phần tử HTML trên trang web hiện tại
        const container = document.getElementById('my-container');
        container.innerHTML = html;
    })
}

function goToResultCourse(courseid) {
    // Tìm biểu mẫu POST
    const postForm1 = document.getElementById('result_course_post');
    
    // Thiết lập giá trị cho các trường dữ liệu ẩn
    if (postForm1) {      
        postForm1.submit();
    } else {
        console.error('Không tìm thấy biểu mẫu POST.');
    }
}

function goToResultExam(examid) {
    // Tìm biểu mẫu POST
    const postForm1 = document.getElementById('result_exam_post');
    
    // Thiết lập giá trị cho các trường dữ liệu ẩn
    if (postForm1) {      
        postForm1.submit();
    } else {
        console.error('Không tìm thấy biểu mẫu POST.');
    }
}