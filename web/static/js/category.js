let questions = [];
let currentQuestionIndex = 0;
let score = 0;

async function loadCategory() {
    try {
        const response = await fetch(`/api/category/${encodeURIComponent(categoryName)}`);
        const data = await response.json();
        
        if (data.error) {
            alert(data.error);
            window.location.href = '/';
            return;
        }
        
        questions = data.questions;
        document.getElementById('category-name').innerText = data.name;
        document.getElementById('question-counter').innerText = 
            `Вопрос 1 из ${data.total_questions}`;
        
        if (questions.length === 0) {
            document.getElementById('question-text').innerText = 'В этой категории нет вопросов';
            document.querySelector('.answers').style.display = 'none';
            return;
        }
        
        showQuestion(0);
        
    } catch (error) {
        console.error('Ошибка:', error);
        alert('Ошибка загрузки категории');
        window.location.href = '/';
    }
}

function showQuestion(index) {
    if (index < 0 || index >= questions.length) return;
    
    currentQuestionIndex = index;
    const question = questions[index];
    
    document.getElementById('question-text').innerText = question.content;
    document.getElementById('question-counter').innerText = 
        `Вопрос ${index + 1} из ${questions.length}`;
    
    document.getElementById('prev-btn').disabled = (index === 0);
    
    if (index === questions.length - 1) {
        document.getElementById('next-btn').style.display = 'none';
        document.getElementById('finish-btn').style.display = 'inline-block';
    } else {
        document.getElementById('next-btn').style.display = 'inline-block';
        document.getElementById('finish-btn').style.display = 'none';
    }
    
    document.getElementById('feedback').innerText = '';
    document.getElementById('feedback').className = 'feedback';
    
    document.getElementById('restart-btn').style.display = 'inline-block';
    
    const yesBtn = document.querySelector('.btn-yes');
    const noBtn = document.querySelector('.btn-no');
    
    if (question.is_resolved) {
        yesBtn.disabled = true;
        noBtn.disabled = true;
        document.getElementById('feedback').innerText = 'Вы уже ответили на этот вопрос';
        document.getElementById('feedback').className = 'feedback info';
    } else {
        yesBtn.disabled = false;
        noBtn.disabled = false;
    }
}

async function submitAnswer(answer) {
    const question = questions[currentQuestionIndex];
    
    try {
        const response = await fetch(`/api/category/${encodeURIComponent(categoryName)}/answer`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                question_id: currentQuestionIndex,
                answer: answer
            })
        });
        
        const data = await response.json();
        
        const feedback = document.getElementById('feedback');
        const pointsText = data.points > 0 ? ` (+${data.points} баллов)` : '';
        feedback.innerText = data.message + pointsText;
        feedback.className = `feedback ${data.correct ? 'correct' : 'incorrect'}`;
        
        if (data.correct) {
            score += data.points;
            document.getElementById('score').innerText = `Баллы: ${score}`;

            if (data.user_points !== undefined) {
                updateUserPoints(data.user_points);
            }
        }
        
        document.querySelector('.btn-yes').disabled = true;
        document.querySelector('.btn-no').disabled = true;
        
        setTimeout(() => {
            if (currentQuestionIndex < questions.length - 1) {
                nextQuestion();
            }
            document.querySelector('.btn-yes').disabled = false;
            document.querySelector('.btn-no').disabled = false;
        }, 1500);
        
    } catch (error) {
        console.error('Ошибка:', error);
        alert('Ошибка отправки ответа');
    }
}

function nextQuestion() {
    if (currentQuestionIndex < questions.length - 1) {
        showQuestion(currentQuestionIndex + 1);
    }
}

function prevQuestion() {
    if (currentQuestionIndex > 0) {
        showQuestion(currentQuestionIndex - 1);
    }
}

async function finishCategory() {
    if (!confirm('Завершить категорию?')) return;
    
    try {
        const response = await fetch(`/api/category/${encodeURIComponent(categoryName)}/finish`, {
            method: 'POST'
        });
        
        const data = await response.json();

        if (data.user_points !== undefined) {
            updateUserPoints(data.user_points);
        }

        const categoryPts = data.category_points || 0;
        const userPts = data.user_points || 0;
        
        alert(
            `Категория завершена!\n\n` +
            `Баллов в этой категории: ${categoryPts}\n` +
            `Всего баллов: ${userPts}`
        );
        
        window.location.href = '/';
        
    } catch (error) {
        console.error('Ошибка:', error);
        alert('Ошибка завершения категории');
    }
}

async function restartCategory() {
    if (!confirm('Начать категорию заново? Прогресс будет сброшен.')) return;
    
    try {
        const response = await fetch(`/api/category/${encodeURIComponent(categoryName)}/start`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.error) {
            alert(data.error);
            return;
        }
        
        alert('Категория начата заново!');
        window.location.reload();
        
    } catch (error) {
        console.error('Ошибка:', error);
        alert('Ошибка сброса категории');
    }
}

document.addEventListener('DOMContentLoaded', loadCategory);
