const API_BASE = '/api';

// Global variables
let mealForm, mealsList, editModal, editForm, deleteBtn, cancelEdit, refreshBtn;
let weeklyChart = null;
let currentEditIndex = null;
let allEntries = [];

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    console.log('Calorie Tracker initialized');
    
    // Get DOM elements
    mealForm = document.getElementById('meal-form');
    mealsList = document.getElementById('meals-list');
    editModal = document.getElementById('editModal');
    editForm = document.getElementById('edit-form');
    deleteBtn = document.getElementById('delete-meal');
    cancelEdit = document.getElementById('cancel-edit');
    refreshBtn = document.getElementById('refresh-btn');
    
    // Set today's date as default
    const todayInput = document.getElementById('date');
    const editDateInput = document.getElementById('edit-date');
    const today = new Date().toISOString().split('T')[0];
    
    if (todayInput) todayInput.value = today;
    if (editDateInput) editDateInput.value = today;
    
    // Event Listeners
    if (mealForm) mealForm.addEventListener('submit', addMeal);
    if (editForm) editForm.addEventListener('submit', updateMeal);
    if (deleteBtn) deleteBtn.addEventListener('click', deleteMeal);
    if (cancelEdit) cancelEdit.addEventListener('click', () => editModal.style.display = 'none');
    if (refreshBtn) refreshBtn.addEventListener('click', refreshAllData);
    
    const closeBtn = document.querySelector('.close');
    if (closeBtn) closeBtn.addEventListener('click', () => editModal.style.display = 'none');
    
    // Load initial data
    refreshAllData();
    
    // Auto-refresh every 30 seconds
    setInterval(refreshAllData, 30000);
    
    // Close modal when clicking outside
    window.onclick = function(event) {
        if (event.target === editModal) editModal.style.display = 'none';
    };
});

// ------------------ API ------------------

async function fetchAPI(endpoint, options = {}) {
    try {
        const response = await fetch(`${API_BASE}${endpoint}`, {
            headers: { 'Content-Type': 'application/json' },
            ...options
        });
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        showNotification('Error connecting to server', 'error');
        throw error;
    }
}

// ------------------ Data ------------------

async function refreshAllData() {
    await loadTodayData();
    await loadWeeklySummary();
    await loadMealsList();
    await loadAllEntries();
    updateQuickStats();
}

async function loadAllEntries() {
    try {
        allEntries = await fetchAPI('/entries');
        console.log(`Loaded ${allEntries.length} total entries`);
    } catch (error) { console.error(error); }
}

// ------------------ Meals ------------------

async function addMeal(e) {
    e.preventDefault();
    const meal = {
        food: document.getElementById('food-name').value.trim(),
        calories: parseInt(document.getElementById('calories').value),
        protein: parseInt(document.getElementById('protein').value),
        category: document.getElementById('category').value,
        date: document.getElementById('date').value
    };
    if (!meal.food || isNaN(meal.calories) || isNaN(meal.protein)) {
        showNotification('Please fill all fields correctly', 'error');
        return;
    }
    try {
        await fetchAPI('/entries', { method: 'POST', body: JSON.stringify(meal) });
        showNotification('Meal added successfully!', 'success');
        mealForm.reset();
        document.getElementById('date').value = new Date().toISOString().split('T')[0];
        await refreshAllData();
    } catch (error) { console.error(error); }
}

async function loadTodayData() {
    try {
        const summary = await fetchAPI('/summary/today');
        document.getElementById('today-calories').textContent = `${summary.total_calories} cal`;
        document.getElementById('today-protein').textContent = `${summary.total_protein}g`;
        updateProteinProgress(summary.total_protein, summary.protein_goal, summary.met_protein_goal);
    } catch (error) { console.error(error); }
}

function updateProteinProgress(current, goal, metGoal) {
    const progress = document.getElementById('protein-progress');
    const text = document.getElementById('protein-progress-text');
    const message = document.getElementById('protein-message');
    if (!progress || !text || !message) return;
    const percent = Math.min((current / goal) * 100, 100);
    progress.style.width = `${percent}%`;
    text.textContent = `${current}/${goal}g`;
    if (metGoal) {
        message.textContent = '🎉 Protein goal achieved!';
        message.className = 'goal-message goal-met';
    } else {
        message.textContent = `⚠️ Need ${goal - current}g more protein`;
        message.className = 'goal-message goal-not-met';
    }
}

async function loadMealsList() {
    try {
        const today = new Date().toISOString().split('T')[0];
        const meals = await fetchAPI(`/entries?date=${today}`);
        if (!mealsList) return;
        if (meals.length === 0) {
            mealsList.innerHTML = '<p class="empty-state">No meals logged today. Add your first meal!</p>';
            return;
        }
        mealsList.innerHTML = '';
        meals.forEach((meal, index) => {
            const mealElement = document.createElement('div');
            mealElement.className = 'meal-item';
            mealElement.innerHTML = `
                <div class="meal-info">
                    <h4>${meal.food}</h4>
                    <div class="meal-meta">
                        <span><i class="fas fa-fire"></i> ${meal.calories} cal</span>
                        <span><i class="fas fa-dumbbell"></i> ${meal.protein}g protein</span>
                    </div>
                    <span class="meal-category category-${meal.category.toLowerCase()}">
                        ${meal.category}
                    </span>
                </div>
                <div class="meal-actions">
                    <button class="btn btn-sm" onclick="editMeal(${index}, '${today}')">
                        <i class="fas fa-edit"></i> Edit
                    </button>
                </div>
            `;
            mealsList.appendChild(mealElement);
        });
    } catch (error) { console.error(error); }
}

// ------------------ Edit Meal ------------------

async function editMeal(localIndex, date) {
    try {
        const meals = await fetchAPI(`/entries?date=${date}`);
        const allMeals = await fetchAPI('/entries');
        const mealToEdit = meals[localIndex];
        currentEditIndex = allMeals.findIndex(m => m.date === mealToEdit.date && m.food === mealToEdit.food && m.calories === mealToEdit.calories);
        if (currentEditIndex === -1) { showNotification('Could not find meal', 'error'); return; }
        document.getElementById('edit-index').value = currentEditIndex;
        document.getElementById('edit-food').value = mealToEdit.food;
        document.getElementById('edit-calories').value = mealToEdit.calories;
        document.getElementById('edit-protein').value = mealToEdit.protein;
        document.getElementById('edit-category').value = mealToEdit.category;
        document.getElementById('edit-date').value = mealToEdit.date;
        editModal.style.display = 'block';
    } catch (error) { console.error(error); }
}

async function updateMeal(e) {
    e.preventDefault();
    const updated = {
        food: document.getElementById('edit-food').value.trim(),
        calories: parseInt(document.getElementById('edit-calories').value),
        protein: parseInt(document.getElementById('edit-protein').value),
        category: document.getElementById('edit-category').value,
        date: document.getElementById('edit-date').value
    };
    try {
        await fetchAPI(`/entries/${currentEditIndex}`, { method: 'PUT', body: JSON.stringify(updated) });
        showNotification('Meal updated successfully!', 'success');
        editModal.style.display = 'none';
        await refreshAllData();
    } catch (error) { console.error(error); }
}

async function deleteMeal() {
    if (!confirm('Are you sure?')) return;
    try {
        await fetchAPI(`/entries/${currentEditIndex}`, { method: 'DELETE' });
        showNotification('Meal deleted successfully!', 'success');
        editModal.style.display = 'none';
        await refreshAllData();
    } catch (error) { console.error(error); }
}

// ------------------ Weekly ------------------

async function loadWeeklySummary() {
    try {
        const weeklyData = await fetchAPI('/summary/week');
        updateWeeklyChart(weeklyData);
        updateWeeklyStats(weeklyData);
    } catch (error) { console.error(error); }
}

function updateWeeklyChart(data) {
    const ctx = document.getElementById('weeklyChart');
    if (!ctx) return;
    if (weeklyChart) weeklyChart.destroy();
    if (!data || data.length === 0) { ctx.parentElement.innerHTML = '<p class="empty-state">No data for the past week</p>'; return; }
    const labels = data.map(d => new Date(d.date).toLocaleDateString('en-US', { weekday: 'short' }));
    const caloriesData = data.map(d => d.calories);
    const proteinData = data.map(d => d.protein);
    weeklyChart = new Chart(ctx.getContext('2d'), {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                { label: 'Calories', data: caloriesData, backgroundColor: 'rgba(67, 97, 238, 0.7)', yAxisID: 'y' },
                { label: 'Protein (g)', data: proteinData, backgroundColor: 'rgba(76, 201, 240, 0.7)', type: 'line', yAxisID: 'y1' }
            ]
        },
        options: {
            responsive: true,
            scales: {
                y: { beginAtZero: true, position: 'left', title: { display: true, text: 'Calories' } },
                y1: { beginAtZero: true, position: 'right', title: { display: true, text: 'Protein (g)' }, grid: { drawOnChartArea: false } }
            },
            plugins: { legend: { position: 'top' } }
        }
    });
}

function updateWeeklyStats(data) {
    if (!data || data.length === 0) { 
        document.getElementById('weekly-avg-cal').textContent = '0';
        document.getElementById('weekly-avg-prot').textContent = '0g';
        document.getElementById('weekly-goal-days').textContent = '0/7';
        return; 
    }
    const totalCal = data.reduce((a,b)=>a+b.calories,0);
    const totalProt = data.reduce((a,b)=>a+b.protein,0);
    const goalDays = data.filter(d=>d.met_goal).length;
    document.getElementById('weekly-avg-cal').textContent = Math.round(totalCal/data.length);
    document.getElementById('weekly-avg-prot').textContent = Math.round(totalProt/data.length)+'g';
    document.getElementById('weekly-goal-days').textContent = `${goalDays}/${data.length}`;
}

// ------------------ Quick Stats ------------------

function updateQuickStats() {
    if (allEntries.length === 0) {
        document.getElementById('total-meals').textContent = '0';
        document.getElementById('avg-daily-cal').textContent = '0';
        document.getElementById('goal-rate').textContent = '0%';
        return;
    }
    const uniqueDays = [...new Set(allEntries.map(e=>e.date))];
    const dailyCalories = {};
    allEntries.forEach(e => dailyCalories[e.date] = (dailyCalories[e.date] || 0)+e.calories);
    const avgCal = Math.round(Object.values(dailyCalories).reduce((a,b)=>a+b,0)/uniqueDays.length);
    document.getElementById('total-meals').textContent = allEntries.length;
    document.getElementById('avg-daily-cal').textContent = avgCal;
    document.getElementById('goal-rate').textContent = 'N/A';
}

// ------------------ Notifications ------------------

function showNotification(message, type='info') {
    const existing = document.querySelector('.notification');
    if (existing) existing.remove();
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `<span>${message}</span><button onclick="this.parentElement.remove()">×</button>`;
    if (!document.querySelector('#notification-styles')) {
        const style = document.createElement('style');
        style.id = 'notification-styles';
        style.textContent = `
            .notification { position: fixed; top: 20px; right: 20px; padding: 15px 20px; border-radius: 8px; color: white; font-weight: 500; display: flex; justify-content: space-between; min-width: 300px; max-width: 400px; z-index: 10000; animation: slideIn 0.3s ease; box-shadow: 0 4px 12px rgba(0,0,0,0.15); }
            .notification-success { background: #28a745; }
            .notification-error { background: #dc3545; }
            .notification-info { background: #17a2b8; }
            .notification button { background: none; border: none; color: white; font-size: 1.5rem; cursor: pointer; margin-left: 15px; padding: 0; }
            @keyframes slideIn { from { transform: translateX(100%); opacity: 0; } to { transform: translateX(0); opacity: 1; } }
        `;
        document.head.appendChild(style);
    }
    document.body.appendChild(notification);
    setTimeout(()=>{ if(notification.parentElement) notification.remove(); },5000);
}

window.editMeal = editMeal;
