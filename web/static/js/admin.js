let categories = [];

document.addEventListener('DOMContentLoaded', loadAdminCategories);

async function loadAdminCategories() {
    try {
        const response = await fetch('/api/admin/categories');
        const data = await response.json();
        
        categories = data.categories;
        renderAdminCategories();
    } catch (error) {
        console.error('Ошибка:', error);
        document.getElementById('categories-admin-list').innerHTML = 
            '<p class="error">Ошибка загрузки категорий</p>';
    }
}

function renderAdminCategories() {
    const container = document.getElementById('categories-admin-list');
    
    if (categories.length === 0) {
        container.innerHTML = '<p>Категорий пока нет. Создайте первую!</p>';
        return;
    }
    
    let html = '';
    categories.forEach(cat => {
        html += `
            <div class="category-card">
                <h3>${cat.name}</h3>
                <div class="category-info">
                    <span class="questions-count">📝 Вопросов: ${cat.questions_count}</span>
                    <span class="status">${cat.is_finished ? '✅ Завершена' : '🔄 Активна'}</span>
                </div>
                <div class="admin-card-actions">
                    <button class="btn btn-small" onclick="editCategory('${cat.name}')">Редактировать</button>
                    <button class="btn btn-small" onclick="manageQuestions('${cat.name}')">Вопросы</button>
                    <button class="btn btn-small btn-danger" onclick="deleteCategory('${cat.name}')">Удалить</button>
                </div>
            </div>
        `;
    });
    
    container.innerHTML = html;
}

function showCreateCategoryModal() {
    document.getElementById('modal-title').textContent = 'Создать категорию';
    document.getElementById('category-original-name').value = '';
    document.getElementById('category-name').value = '';
    document.getElementById('modal-overlay').style.display = 'flex';
}

function editCategory(name) {
    document.getElementById('modal-title').textContent = 'Редактировать категорию';
    document.getElementById('category-original-name').value = name;
    document.getElementById('category-name').value = name;
    document.getElementById('modal-overlay').style.display = 'flex';
}

function closeModal() {
    document.getElementById('modal-overlay').style.display = 'none';
}

async function saveCategory(event) {
    event.preventDefault();
    
    const originalName = document.getElementById('category-original-name').value;
    const newName = document.getElementById('category-name').value.trim();
    
    if (!newName) {
        alert('Введите название категории');
        return;
    }
    
    try {
        let response;
        if (originalName) {
            response = await fetch(`/api/admin/category/${encodeURIComponent(originalName)}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name: newName })
            });
        } else {
            response = await fetch('/api/admin/category', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name: newName })
            });
        }
        
        const data = await response.json();
        
        if (response.ok) {
            closeModal();
            loadAdminCategories();
            alert(data.message);
        } else {
            alert(data.error || 'Ошибка сохранения');
        }
    } catch (error) {
        console.error('Ошибка:', error);
        alert('Ошибка сохранения категории');
    }
}

async function deleteCategory(name) {
    if (!confirm(`Удалить категорию "${name}"? Это действие нельзя отменить.`)) {
        return;
    }
    
    try {
        const response = await fetch(`/api/admin/category/${encodeURIComponent(name)}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (response.ok) {
            loadAdminCategories();
            alert(data.message);
        } else {
            alert(data.error || 'Ошибка удаления');
        }
    } catch (error) {
        console.error('Ошибка:', error);
        alert('Ошибка удаления категории');
    }
}

async function manageQuestions(name) {
    document.getElementById('question-modal-title').textContent = `Вопросы: ${name}`;
    document.getElementById('question-category-name').value = name;
    
    try {
        const response = await fetch(`/api/category/${encodeURIComponent(name)}`);
        const data = await response.json();
        
        if (response.ok) {
            renderQuestionsList(data.questions, name);
            document.getElementById('question-modal-overlay').style.display = 'flex';
        } else {
            alert(data.error || 'Ошибка загрузки вопросов');
        }
    } catch (error) {
        console.error('Ошибка:', error);
        alert('Ошибка загрузки вопросов');
    }
}

function renderQuestionsList(questions, categoryName) {
    const container = document.getElementById('questions-list');
    
    if (questions.length === 0) {
        container.innerHTML = '<p>Вопросов пока нет. Добавьте первый!</p>';
        return;
    }
    
    let html = '<h3>Список вопросов</h3>';
    questions.forEach((q, idx) => {
        html += `
            <div class="question-item">
                <div class="question-text">
                    <strong>${idx + 1}.</strong> ${q.content}
                    <span class="question-meta">
                        ${q.correct ? '✅ Да' : '❌ Нет'} | ${q.points} баллов
                    </span>
                </div>
                <button class="btn btn-small btn-danger" onclick="deleteQuestion('${categoryName}', ${q.id})">Удалить</button>
            </div>
        `;
    });
    
    container.innerHTML = html;
}

function closeQuestionModal() {
    document.getElementById('question-modal-overlay').style.display = 'none';
    document.getElementById('question-form').reset();
}

async function addQuestion(event) {
    event.preventDefault();
    
    const categoryName = document.getElementById('question-category-name').value;
    const content = document.getElementById('question-content').value.trim();
    const correctCheckbox = document.getElementById('question-correct');
    const correct = correctCheckbox.checked ? true : false;
    const points = parseInt(document.getElementById('question-points').value) || 5;
    
    if (!content) {
        alert('Введите текст вопроса');
        return;
    }
    
    try {
        const response = await fetch(`/api/admin/category/${encodeURIComponent(categoryName)}/questions`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ content, correct, points })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            document.getElementById('question-form').reset();
            manageQuestions(categoryName);
            loadAdminCategories();
            alert(data.message);
        } else {
            alert(data.error || 'Ошибка добавления вопроса');
        }
    } catch (error) {
        console.error('Ошибка:', error);
        alert('Ошибка добавления вопроса');
    }
}

async function deleteQuestion(categoryName, questionId) {
    if (!confirm('Удалить этот вопрос?')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/admin/category/${encodeURIComponent(categoryName)}/questions/${questionId}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (response.ok) {
            manageQuestions(categoryName);
            loadAdminCategories();
            alert(data.message);
        } else {
            alert(data.error || 'Ошибка удаления вопроса');
        }
    } catch (error) {
        console.error('Ошибка:', error);
        alert('Ошибка удаления вопроса');
    }
}