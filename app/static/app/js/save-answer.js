
document.addEventListener("DOMContentLoaded", function() {
    const saveButton = document.getElementById("save-button");
    const selectedAnswers = {};
    const quizId = document.getElementById("quizid").value;
    const scoreElement = document.getElementById("score");
    

    // Lấy dữ liệu đáp án đã chọn (sử dụng JavaScript để lấy giá trị radio button đã chọn)
    function updateSelectedAnswers() {
        const questions = document.querySelectorAll(".question");
        questions.forEach(question => {
            const questionId = question.getAttribute("data-question-id");
            const selectedAnswer = question.querySelector('input[type="radio"]:checked');
            if (selectedAnswer) {
                selectedAnswers[questionId] = selectedAnswer.value;
            }
        });
    }

    //Lưu tạm
    saveButton.addEventListener("click", function() {
        // Lấy dữ liệu đáp án đã chọn (sử dụng JavaScript để lấy giá trị radio button đã chọn)        
         // Gọi hàm để cập nhật selectedAnswers
         updateSelectedAnswers();
         
        console.log(quizId)
         // Gửi dữ liệu đáp án đã chọn bằng Ajax về server
         fetch("/save_answers/?quiz_id=" + quizId, {    
             method: "POST",
             headers: {
                 "X-CSRFToken": getCookie("csrftoken"),
                 "Content-Type": "application/json",
             },
             //body: JSON.stringify({ selectedAnswers,quiz_id:quizId}),
             body: JSON.stringify(selectedAnswers),
         })
         .then(response => {
             if (response.ok) {                
                return response.json();
             } else {
                 alert("Có lỗi xảy ra khi lưu đáp án 1.");
             }
         })
         .then(data => {
            const message = data.message;
            alert(message);
        })
         .catch(error => {
             console.error(error);
             alert(error);
         });                                                 
    });

    // Nộp bài
    const submitButton = document.getElementById("submit-button");
    submitButton.addEventListener("click", function() {
        updateSelectedAnswers();
        if(HetThoiGian==false)
        {
            var confirmSubmission = confirm("Bạn có muốn nộp bài không?");
        }
        else
        {
            var confirmSubmission = true;
        }
        if (confirmSubmission) {
        
            fetch("/submit_quiz/?quiz_id=" + quizId, {
                method: "POST",
                headers: {
                    "X-CSRFToken": getCookie("csrftoken"),
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(selectedAnswers),
            })
            .then(response => {
                if (response.ok) {
                    return response.json();
                } else {
                    throw new Error("Có lỗi xảy ra khi nộp bài 1.");
                }
            })
            .then(data => {
                const message = data.message;
                const score = data.score;
                const totalquestion = data.totalquestion;
                var scoreElement = document.getElementById("score");
                var scoreElement1 = document.getElementById("score1");
                alert("Bạn đã trả lời đúng " + score)
                // Thêm nội dung vào thẻ h6
                scoreElement1.style.display="block"
                scoreElement.innerHTML =  score + "/"+ totalquestion;    
                if(score >= totalquestion/2)
                    scoreElement.style.color="green";
                else
                    scoreElement.style.color="red";           
                alert(message);

                //scoreElement.textContent = data.score;
                // Vô hiệu hóa nút "Lưu" và "Nộp bài"
                saveButton.disabled = true;
                submitButton.disabled = true;
                saveButton.style.display="none"
                submitButton.style.display="none"
            })
            .catch(error => {
                console.error(error);
                alert("Có lỗi xảy ra khi nộp bài 2.");
            });
            DaNopBai = true;
        }
    });  
});


