function updateUserPoints(newPoints) {
    const pointsElement = document.getElementById('user-points');
    if (pointsElement) {
        const oldPoints = parseInt(pointsElement.innerText);
        pointsElement.innerText = newPoints;
        
        if (newPoints > oldPoints) {
            pointsElement.style.color = '#4caf50';
            pointsElement.style.transform = 'scale(1.3)';
            setTimeout(() => {
                pointsElement.style.color = '';
                pointsElement.style.transform = '';
            }, 500);
        }
    }
    sessionData.points = newPoints;
}

async function loadCategories() {
    try {
        const response = await fetch('/api/categories');
        const data = await response.json();
        
        const container = document.getElementById('categories-list');
        
        if (data.categories.length === 0) {
            container.innerHTML = '<p>Категорий не найдено</p>';
            return;
        }
        
        let html = '';
        data.categories.forEach(cat => {
            const statusClass = cat.is_finished ? 'finished' : 'active';
            const statusText = cat.is_finished ? '✅ Завершена' : '🔄 Активна';
            
            html += `
                <div class="category-card ${statusClass}" onclick="selectCategory('${cat.name}')">
                    <h3>${cat.name}</h3>
                    <div class="category-info">
                        <span class="status">${statusText}</span>
                        <span class="questions-count">📝 Вопросов: ${cat.questions_count}</span>
                        <span class="points">🏆 Баллы: ${cat.points}</span>
                    </div>
                </div>
            `;
        });
        
        container.innerHTML = html;
        
    } catch (error) {
        console.error('Ошибка:', error);
        document.getElementById('categories-list').innerHTML = 
            '<p class="error">Ошибка загрузки категорий</p>';
    }
}

function selectCategory(name) {
    window.location.href = `/category/${encodeURIComponent(name)}`;
}

document.addEventListener('DOMContentLoaded', loadCategories);