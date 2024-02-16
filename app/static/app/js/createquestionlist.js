
document.addEventListener("DOMContentLoaded", function() {
    

    const questionList = document.querySelector(".question-list");

    // Tạo một mảng chứa trạng thái của câu hỏi (ban đầu tất cả chưa trả lời)
    const questionStatus = new Array(quizQuestions.length).fill(false);

    // Hàm cập nhật trạng thái của câu hỏi
    

    // Điều hướng đến câu hỏi khi người dùng chọn trả lời câu hỏi
    questionList.addEventListener("click", function(event) {
        const listItem = event.target;
        if (listItem.tagName === "LI") {
            const questionIndex = [...questionList.children].indexOf(listItem);
            // Chuyển đến câu hỏi tương ứng khi người dùng click vào số thứ tự câu hỏi
            // Điều hướng hoặc cuộn trang để thấy câu hỏi
        }
    });

    // Thêm danh sách số thứ tự câu hỏi vào `question-list`
    const rightContainer = document.querySelector(".question-list");

    for (let i = 0; i < quizQuestions.length; i++) {
        console.log(i)
        const questionItem = document.createElement("div");
        questionItem.classList.add("question-item");
        
        const questionNumber = document.createElement("span");
        questionNumber.textContent = (i + 1).toString(); // Số thứ tự câu hỏi

        // Đặt thuộc tính name và value
        questionItem.setAttribute("name", "questionid");
        questionItem.setAttribute("value", quizQuestions[i].id);

        questionItem.appendChild(questionNumber);
        rightContainer.appendChild(questionItem);

        // Kiểm tra trạng thái ban đầu, nếu đã trả lời, cập nhật màu nền
        if (questionStatus[i]) {
            questionItem.style.backgroundColor = "green";
        }
    }

     function updateQuestionStatus(questionIndex, answered) {
    alert(questionIndex)
    questionStatus[questionIndex] = answered;
    const listItem = questionList.children[questionIndex];
    if (answered) {
        listItem.style.backgroundColor = "green"; // Câu đã trả lời
    } else {
        listItem.style.backgroundColor = "white"; // Câu chưa trả lời
    }
  }

  quizQuestions.forEach(function(question) {
    var questionElement = document.querySelector('.question[data-question-id="' + question.id + '"]');
    var answerInputs = questionElement.querySelectorAll('input[type="radio"]');

    answerInputs.forEach(function(input) {
        input.addEventListener('change', function(event) {
            // Xử lý sự kiện khi người thi chọn đáp án
            updateQuestionStatus(questionid,true)
            // Ở đây, bạn có thể cập nhật trạng thái của câu hỏi
            // ví dụ: thay đổi màu nền của câu hỏi
            if (input.checked) {
                questionElement.style.backgroundColor = 'green'; // Đã chọn đáp án
            } else {
                questionElement.style.backgroundColor = 'white'; // Chưa chọn đáp án
            }
        });
    });
});
});


