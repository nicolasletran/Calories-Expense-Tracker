// Calorie Tracker - Fixed for API response format
const API_BASE = '/api';

// Global variables
let mealForm, mealsList, editModal, editForm, deleteBtn, cancelEdit, refreshBtn, clearBtn;
let aiPredictBtn, aiPredictionSection, aiResults, mealsCount, mealsTitle;
let weeklyChart = null;
let currentEditId = null;
let allEntries = [];
let currentViewDate = null;
let prevDayBtn, nextDayBtn, todayBtn, currentDateLabel, currentDateSpan;
let exportBtn, importBtn, importFile;

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    console.log('Calorie Tracker initialized');
    
    // Theme Toggle
    const themeToggleBtn = document.getElementById('theme-toggle-btn');
    const themeIcon = themeToggleBtn.querySelector('i');
    const themeText = themeToggleBtn.querySelector('span');

    // Check for saved theme or prefer-color-scheme
    const prefersDarkScheme = window.matchMedia('(prefers-color-scheme: dark)');
    const currentTheme = localStorage.getItem('theme') || 
        (prefersDarkScheme.matches ? 'dark' : 'light');

    // Apply theme on load
    if (currentTheme === 'light') {
        document.body.classList.add('light-mode');
        themeIcon.className = 'fas fa-sun';
        themeText.textContent = 'Light Mode';
    } else {
        themeIcon.className = 'fas fa-moon';
        themeText.textContent = 'Dark Mode';
    }

    // Theme toggle event
    themeToggleBtn.addEventListener('click', () => {
        if (document.body.classList.contains('light-mode')) {
            // Switch to dark mode
            document.body.classList.remove('light-mode');
            themeIcon.className = 'fas fa-moon';
            themeText.textContent = 'Dark Mode';
            localStorage.setItem('theme', 'dark');
        } else {
            // Switch to light mode
            document.body.classList.add('light-mode');
            themeIcon.className = 'fas fa-sun';
            themeText.textContent = 'Light Mode';
            localStorage.setItem('theme', 'light');
        }
        
        // Update chart colors if exists
        if (weeklyChart) {
            updateChartTheme();
        }
    });

    // Listen for system theme changes
    prefersDarkScheme.addEventListener('change', (e) => {
        if (!localStorage.getItem('theme')) {
            if (e.matches) {
                document.body.classList.remove('light-mode');
                themeIcon.className = 'fas fa-moon';
                themeText.textContent = 'Dark Mode';
            } else {
                document.body.classList.add('light-mode');
                themeIcon.className = 'fas fa-sun';
                themeText.textContent = 'Light Mode';
            }
        }
    });
    
    // Get DOM elements
    mealForm = document.getElementById('meal-form');
    mealsList = document.getElementById('meals-list');
    mealsTitle = document.getElementById('meals-title');
    editModal = document.getElementById('editModal');
    editForm = document.getElementById('edit-form');
    deleteBtn = document.getElementById('delete-meal');
    cancelEdit = document.getElementById('cancel-edit');
    refreshBtn = document.getElementById('refresh-btn');
    clearBtn = document.getElementById('clear-btn');
    aiPredictBtn = document.getElementById('ai-predict-btn');
    aiPredictionSection = document.getElementById('ai-prediction-section');
    aiResults = document.getElementById('ai-results');
    mealsCount = document.getElementById('meals-count');
    
    // Get date navigation elements
    prevDayBtn = document.getElementById('prev-day');
    nextDayBtn = document.getElementById('next-day');
    todayBtn = document.getElementById('today-btn');
    currentDateLabel = document.getElementById('current-date-label');
    currentDateSpan = document.getElementById('current-date');
    
    // Get export/import elements
    exportBtn = document.getElementById('export-btn');
    importBtn = document.getElementById('import-btn');
    importFile = document.getElementById('import-file');
    
    // Set today's date as default
    const todayInput = document.getElementById('date');
    const editDateInput = document.getElementById('edit-date');
    const today = new Date().toISOString().split('T')[0];
    
    if (todayInput) todayInput.value = today;
    if (editDateInput) editDateInput.value = today;
    
    // Set current view date
    currentViewDate = new Date();
    if (currentDateSpan) {
        updateDateDisplay();
    }
    
    // Event Listeners
    if (mealForm) mealForm.addEventListener('submit', addMeal);
    if (editForm) editForm.addEventListener('submit', updateMeal);
    if (deleteBtn) deleteBtn.addEventListener('click', deleteMeal);
    if (cancelEdit) cancelEdit.addEventListener('click', () => closeModal(editModal));
    if (refreshBtn) refreshBtn.addEventListener('click', refreshAllData);
    if (clearBtn) clearBtn.addEventListener('click', clearForm);
    if (aiPredictBtn) aiPredictBtn.addEventListener('click', predictNutrients);
    
    // Date navigation event listeners
    if (prevDayBtn) prevDayBtn.addEventListener('click', goToPreviousDay);
    if (nextDayBtn) nextDayBtn.addEventListener('click', goToNextDay);
    if (todayBtn) todayBtn.addEventListener('click', goToToday);
    
    // Export/Import event listeners
    if (exportBtn) exportBtn.addEventListener('click', exportData);
    if (importBtn) importBtn.addEventListener('click', () => importFile.click());
    if (importFile) importFile.addEventListener('change', handleFileImport);
    
    // Modal close buttons
    const closeBtns = document.querySelectorAll('.close, .close-health, .close-database, .close-help');
    closeBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const modal = this.closest('.modal');
            closeModal(modal);
        });
    });
    
    // Footer button event listeners
    document.getElementById('health-check')?.addEventListener('click', showHealthCheck);
    document.getElementById('database-info')?.addEventListener('click', showDatabaseInfo);
    document.getElementById('keyboard-help')?.addEventListener('click', showKeyboardHelp);
    
    // Auto-detect weight from food input with debouncing
    const foodNameInput = document.getElementById('food-name');
    if (foodNameInput) {
        let aiPredictDebounce;
        foodNameInput.addEventListener('input', function(e) {
            const foodText = e.target.value.trim();
            
            // Clear any existing timeout
            clearTimeout(aiPredictDebounce);
            
            // If food text is long enough, predict after delay
            if (foodText.length > 3) {
                aiPredictDebounce = setTimeout(() => {
                    // Only predict if value hasn't changed
                    if (foodText === this.value.trim()) {
                        // Auto-predict for common foods
                        const commonFoods = ['chicken', 'beef', 'pork', 'rice', 'egg', 'apple', 'banana'];
                        if (commonFoods.some(food => foodText.toLowerCase().includes(food))) {
                            predictNutrients();
                        }
                    }
                }, 1500); // 1.5 second debounce
            }
        });
        
        // Auto-focus on page load
        setTimeout(() => foodNameInput.focus(), 500);
    }
    
    // Real-time input validation
    const caloriesInput = document.getElementById('calories');
    const proteinInput = document.getElementById('protein');
    
    if (caloriesInput) {
        caloriesInput.addEventListener('input', validateCalories);
        caloriesInput.addEventListener('blur', validateCalories);
    }
    
    if (proteinInput) {
        proteinInput.addEventListener('input', validateProtein);
        proteinInput.addEventListener('blur', validateProtein);
    }
    
    // Load initial data
    refreshAllData();
    
    // Auto-refresh every 60 seconds
    setInterval(refreshAllData, 60000);
    
    // Fix layout issues
    fixLayoutIssues();
    
    // Close modals when clicking outside
    window.addEventListener('click', function(event) {
        if (event.target.classList.contains('modal')) {
            closeModal(event.target);
        }
    });
    
    // Keyboard shortcuts
    document.addEventListener('keydown', handleKeyboardShortcuts);
    
    console.log('Application initialization complete');
});

// ------------------ Helper Functions ------------------

function closeModal(modal) {
    if (modal) {
        modal.style.display = 'none';
    }
}

function openModal(modal) {
    if (modal) {
        modal.style.display = 'block';
    }
}

function isToday(date) {
    const today = new Date();
    return date.getDate() === today.getDate() &&
           date.getMonth() === today.getMonth() &&
           date.getFullYear() === today.getFullYear();
}

function isYesterday(date) {
    const yesterday = new Date();
    yesterday.setDate(yesterday.getDate() - 1);
    return date.getDate() === yesterday.getDate() &&
           date.getMonth() === yesterday.getMonth() &&
           date.getFullYear() === yesterday.getFullYear();
}

function formatDateDisplay(date) {
    if (isToday(date)) return 'Today';
    if (isYesterday(date)) return 'Yesterday';
    
    // Format as "Mon, Jan 15"
    return date.toLocaleDateString('en-US', { 
        weekday: 'short',
        month: 'short', 
        day: 'numeric' 
    });
}

function formatFullDate(date) {
    return date.toLocaleDateString('en-US', { 
        weekday: 'long',
        year: 'numeric',
        month: 'long', 
        day: 'numeric' 
    });
}

// ------------------ API Functions ------------------

async function fetchAPI(endpoint, options = {}) {
    try {
        const response = await fetch(`${API_BASE}${endpoint}`, {
            headers: { 'Content-Type': 'application/json' },
            ...options
        });
        
        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`HTTP ${response.status}: ${errorText || 'Unknown error'}`);
        }
        
        const data = await response.json();
        
        // Extract data based on endpoint
        switch(endpoint) {
            case '/entries':
                // Return entries array from response
                return Array.isArray(data) ? data : (data.entries || []);
                
            case '/summary/today':
                // Return today's summary object
                return data;
                
            case '/summary/week':
                // Return weekly summary array
                return Array.isArray(data) ? data : (data.summary || []);
                
            case '/analytics/common-foods':
                // Return common foods array
                return data.common_foods || [];
                
            case '/health':
                // Return health data
                return data;
                
            case '/export':
                // Return export data
                return data;
                
            case '/ai/predict':
                // Return AI prediction
                return data;
                
            case '/ai/status':
                // Return AI status
                return data;
                
            default:
                return data;
        }
    } catch (error) {
        console.error('API Error:', error);
        
        // Don't show notification for health checks or background updates
        if (!endpoint.includes('/health') && !endpoint.includes('/summary')) {
            showNotification(`Connection error: ${error.message}`, 'error');
        }
        
        throw error;
    }
}

// ------------------ Layout Fixes ------------------

function fixLayoutIssues() {
    // Ensure body doesn't overflow
    document.body.style.overflowX = 'hidden';
    
    // Check for elements causing overflow
    const container = document.querySelector('.container');
    if (container) {
        const containerWidth = container.offsetWidth;
        const bodyWidth = document.body.offsetWidth;
        
        if (containerWidth > bodyWidth) {
            container.style.maxWidth = '100%';
            container.style.padding = '15px';
        }
    }
    
    // Fix chart container width
    const chartContainers = document.querySelectorAll('.chart-container');
    chartContainers.forEach(container => {
        const parentWidth = container.parentElement.offsetWidth;
        if (container.offsetWidth > parentWidth - 40) {
            container.style.width = 'calc(100% - 40px)';
            container.style.margin = '20px auto';
        }
    });
}

// ------------------ Data Management ------------------

async function refreshAllData() {
    try {
        // Hide AI prediction section when refreshing
        if (aiPredictionSection) {
            aiPredictionSection.style.display = 'none';
        }
        
        await Promise.all([
            loadTodayData(),
            loadWeeklySummary(),
            loadMealsList(),
            loadAllEntries(),
            loadRecentDays()
        ]);
        
        updateQuickStats();
        loadCommonFoods();
        
        // Fix layout after loading data
        setTimeout(fixLayoutIssues, 100);
        
        console.log('Data refresh complete');
    } catch (error) {
        console.error('Error refreshing data:', error);
    }
}

async function loadAllEntries() {
    try {
        allEntries = await fetchAPI('/entries');
        console.log(`Loaded ${allEntries.length} total entries`);
        return allEntries;
    } catch (error) { 
        console.error('Error loading entries:', error);
        return [];
    }
}

// ------------------ Date Navigation ------------------

function updateDateDisplay() {
    if (!currentDateLabel || !currentDateSpan) return;
    
    const today = new Date();
    const todayStr = today.toISOString().split('T')[0];
    const viewDateStr = currentViewDate.toISOString().split('T')[0];
    
    // Update date strings
    currentDateSpan.textContent = viewDateStr;
    
    // Update label
    if (viewDateStr === todayStr) {
        currentDateLabel.textContent = 'Today';
        if (nextDayBtn) {
            nextDayBtn.disabled = true;
            nextDayBtn.style.opacity = '0.5';
            nextDayBtn.style.cursor = 'not-allowed';
        }
    } else {
        currentDateLabel.textContent = formatDateDisplay(currentViewDate);
        if (nextDayBtn) {
            nextDayBtn.disabled = false;
            nextDayBtn.style.opacity = '1';
            nextDayBtn.style.cursor = 'pointer';
            
            // Disable next day if it's in the future
            const tomorrow = new Date(today);
            tomorrow.setDate(tomorrow.getDate() + 1);
            const tomorrowStr = tomorrow.toISOString().split('T')[0];
            
            if (viewDateStr >= tomorrowStr) {
                nextDayBtn.disabled = true;
                nextDayBtn.style.opacity = '0.5';
                nextDayBtn.style.cursor = 'not-allowed';
            }
        }
    }
    
    // Update form date field to match view date
    const dateInput = document.getElementById('date');
    if (dateInput) {
        dateInput.value = viewDateStr;
    }
    
    // Update meals title
    if (mealsTitle) {
        if (viewDateStr === todayStr) {
            mealsTitle.textContent = "Today's Meals";
        } else {
            const formattedDate = formatFullDate(currentViewDate);
            mealsTitle.textContent = `Meals on ${formattedDate}`;
        }
    }
    
    // Load meals for this date
    loadMealsForDate(viewDateStr);
}

function goToPreviousDay() {
    currentViewDate.setDate(currentViewDate.getDate() - 1);
    updateDateDisplay();
}

function goToNextDay() {
    const today = new Date();
    const todayStr = today.toISOString().split('T')[0];
    const viewDateStr = currentViewDate.toISOString().split('T')[0];
    
    // Don't go beyond today
    if (viewDateStr >= todayStr) return;
    
    currentViewDate.setDate(currentViewDate.getDate() + 1);
    updateDateDisplay();
}

function goToToday() {
    currentViewDate = new Date();
    updateDateDisplay();
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// ------------------ Meal Management ------------------

async function addMeal(e) {
    e.preventDefault();
    
    const foodInput = document.getElementById('food-name');
    const caloriesInput = document.getElementById('calories');
    const proteinInput = document.getElementById('protein');
    const categoryInput = document.getElementById('category');
    const dateInput = document.getElementById('date');
    
    if (!foodInput || !caloriesInput || !proteinInput || !categoryInput || !dateInput) {
        showNotification('Form elements not found', 'error');
        return;
    }
    
    const meal = {
        food: foodInput.value.trim(),
        calories: parseInt(caloriesInput.value) || 0,
        protein: parseInt(proteinInput.value) || 0,
        category: categoryInput.value,
        date: dateInput.value
    };
    
    // Validate input
    const validationErrors = validateMealInput(meal);
    if (validationErrors.length > 0) {
        showNotification(validationErrors.join(', '), 'error');
        return;
    }
    
    try {
        await fetchAPI('/entries', { 
            method: 'POST', 
            body: JSON.stringify(meal) 
        });
        
        showNotification('Meal added successfully!', 'success');
        clearForm();
        
        // Reset focus to food input
        setTimeout(() => foodInput.focus(), 100);
        
        // Hide AI section after adding meal
        if (aiPredictionSection) aiPredictionSection.style.display = 'none';
        
        await refreshAllData();
    } catch (error) { 
        console.error('Error adding meal:', error);
        showNotification(`Failed to add meal: ${error.message}`, 'error');
    }
}

function clearForm() {
    const foodInput = document.getElementById('food-name');
    const caloriesInput = document.getElementById('calories');
    const proteinInput = document.getElementById('protein');
    const categoryInput = document.getElementById('category');
    const dateInput = document.getElementById('date');
    
    if (foodInput) foodInput.value = '';
    if (caloriesInput) caloriesInput.value = '';
    if (proteinInput) proteinInput.value = '';
    if (categoryInput) categoryInput.value = 'Breakfast';
    if (dateInput) dateInput.value = currentViewDate.toISOString().split('T')[0];
    
    // Hide AI prediction section
    if (aiPredictionSection) {
        aiPredictionSection.style.display = 'none';
    }
    
    // Clear validation messages
    clearValidationMessages();
    
    // Focus on food input
    setTimeout(() => {
        if (foodInput) foodInput.focus();
    }, 100);
}

function clearValidationMessages() {
    const validationMessages = document.querySelectorAll('.validation-message');
    validationMessages.forEach(msg => {
        msg.textContent = '';
        msg.className = 'validation-message';
    });
}

function validateCalories() {
    const input = document.getElementById('calories');
    const message = document.getElementById('calories-validation');
    
    if (!input || !message) return;
    
    const value = parseInt(input.value) || 0;
    
    if (value < 0) {
        message.textContent = 'Calories cannot be negative';
        message.className = 'validation-message error';
        return false;
    } else if (value > 10000) {
        message.textContent = 'Calories cannot exceed 10000';
        message.className = 'validation-message error';
        return false;
    } else if (value > 5000) {
        message.textContent = 'Warning: Very high calorie value';
        message.className = 'validation-message warning';
        return true;
    } else {
        message.textContent = '';
        message.className = 'validation-message';
        return true;
    }
}

function validateProtein() {
    const input = document.getElementById('protein');
    const message = document.getElementById('protein-validation');
    
    if (!input || !message) return;
    
    const value = parseInt(input.value) || 0;
    
    if (value < 0) {
        message.textContent = 'Protein cannot be negative';
        message.className = 'validation-message error';
        return false;
    } else if (value > 500) {
        message.textContent = 'Protein cannot exceed 500g';
        message.className = 'validation-message error';
        return false;
    } else if (value > 200) {
        message.textContent = 'Warning: Very high protein value';
        message.className = 'validation-message warning';
        return true;
    } else {
        message.textContent = '';
        message.className = 'validation-message';
        return true;
    }
}

function validateMealInput(meal) {
    const errors = [];
    
    if (!meal.food || meal.food.trim().length < 2) {
        errors.push('Food name must be at least 2 characters');
    }
    
    if (meal.calories < 0 || meal.calories > 10000) {
        errors.push('Calories must be between 0 and 10000');
    }
    
    if (meal.protein < 0 || meal.protein > 500) {
        errors.push('Protein must be between 0 and 500g');
    }
    
    if (!meal.date || !/^\d{4}-\d{2}-\d{2}$/.test(meal.date)) {
        errors.push('Date must be in YYYY-MM-DD format');
    }
    
    return errors;
}

async function loadTodayData() {
    try {
        const summary = await fetchAPI('/summary/today');
        const todayCalories = document.getElementById('today-calories');
        const todayProtein = document.getElementById('today-protein');
        
        if (todayCalories) todayCalories.textContent = summary.total_calories || 0;
        if (todayProtein) todayProtein.textContent = (summary.total_protein || 0) + 'g';
        
        updateProteinProgress(summary.total_protein || 0, summary.protein_goal || 140, summary.met_protein_goal || false);
    } catch (error) { 
        console.error('Error loading today data:', error);
    }
}

function updateProteinProgress(current, goal, metGoal) {
    const progress = document.getElementById('protein-progress');
    const text = document.getElementById('protein-progress-text');
    const message = document.getElementById('protein-message');
    const percentEl = document.getElementById('protein-percent');
    
    if (!progress || !text || !message || !percentEl) return;
    
    const percent = Math.min((current / goal) * 100, 100);
    progress.style.width = `${percent}%`;
    text.textContent = `${current}/${goal}g`;
    percentEl.textContent = `${Math.round(percent)}%`;
    
    if (metGoal) {
        message.innerHTML = '<i class="fas fa-trophy"></i> 🎉 Protein goal achieved! Keep it up!';
        message.className = 'goal-message goal-met';
    } else if (current > 0) {
        const remaining = goal - current;
        message.innerHTML = `<i class="fas fa-running"></i> Need ${remaining}g more protein to reach goal`;
        message.className = 'goal-message goal-not-met';
    } else {
        message.innerHTML = '<i class="fas fa-utensils"></i> Start logging meals to track your protein progress';
        message.className = 'goal-message goal-not-met';
    }
}

async function loadMealsForDate(dateStr) {
    try {
        const response = await fetchAPI(`/entries?date=${dateStr}`);
        // response should be an array from fetchAPI function
        displayMealsForDate(response, dateStr);
        
        // Also update today's summary if viewing today
        const today = new Date().toISOString().split('T')[0];
        if (dateStr === today) {
            await loadTodayData();
        }
    } catch (error) { 
        console.error(`Error loading meals for date ${dateStr}:`, error);
    }
}

function displayMealsForDate(meals, dateStr) {
    if (!mealsList) return;
    
    // Ensure meals is an array
    if (!Array.isArray(meals)) {
        console.error('displayMealsForDate: meals is not an array:', meals);
        meals = [];
    }
    
    if (meals.length === 0) {
        let message, description;
        
        if (isToday(new Date(dateStr))) {
            message = "No meals yet";
            description = "Add your first meal to get started!";
        } else if (isYesterday(new Date(dateStr))) {
            message = "No meals yesterday";
            description = "No meals were logged on this day.";
        } else {
            const dateObj = new Date(dateStr);
            const formattedDate = formatFullDate(dateObj);
            message = `No meals on ${formattedDate}`;
            description = "No meals were logged on this day.";
        }
        
        mealsList.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-utensils"></i>
                <h3>${message}</h3>
                <p>${description}</p>
            </div>
        `;
        
        // Update meals count
        if (mealsCount) {
            mealsCount.textContent = '0 meals';
        }
        return;
    }
    
    // Calculate totals for this date
    const totalCalories = meals.reduce((sum, meal) => sum + (meal.calories || 0), 0);
    const totalProtein = meals.reduce((sum, meal) => sum + (meal.protein || 0), 0);
    
    // Create HTML for meals
    let mealsHTML = `
        <div class="date-header">
            <div class="date-totals">
                <span><i class="fas fa-fire"></i> ${totalCalories} cal</span>
                <span><i class="fas fa-dumbbell"></i> ${totalProtein}g protein</span>
            </div>
        </div>
    `;
    
    // Add meals
    meals.forEach((meal, index) => {
        const mealElement = `
            <div class="meal-item" data-id="${meal.id || index}">
                <div class="meal-info">
                    <h4>${meal.food}</h4>
                    <div class="meal-meta">
                        <span><i class="fas fa-fire"></i> ${meal.calories} cal</span>
                        <span><i class="fas fa-dumbbell"></i> ${meal.protein}g protein</span>
                        <span class="meal-time">${meal.category}</span>
                    </div>
                    <span class="meal-category category-${meal.category.toLowerCase()}">
                        ${meal.category}
                    </span>
                </div>
                <div class="meal-actions">
                    <button class="btn btn-sm btn-edit" onclick="editMeal('${meal.id || index}', '${dateStr}')">
                        <i class="fas fa-edit"></i> Edit
                    </button>
                </div>
            </div>
        `;
        mealsHTML += mealElement;
    });
    
    mealsList.innerHTML = mealsHTML;
    
    // Update meals count
    if (mealsCount) {
        mealsCount.textContent = `${meals.length} meal${meals.length !== 1 ? 's' : ''}`;
    }
}

async function loadMealsList() {
    if (!currentViewDate) {
        currentViewDate = new Date();
    }
    const dateStr = currentViewDate.toISOString().split('T')[0];
    await loadMealsForDate(dateStr);
}

// ------------------ AI Functions ------------------

async function predictNutrients() {
    const foodInput = document.getElementById('food-name');
    const categoryInput = document.getElementById('category');
    
    if (!foodInput) {
        showNotification('Food input not found', 'error');
        return;
    }
    
    const food = foodInput.value.trim();
    const category = categoryInput ? categoryInput.value : null;
    
    if (!food) {
        showNotification('Please enter a food name first', 'error');
        return;
    }
    
    // Show loading state
    if (aiPredictionSection) {
        aiPredictionSection.style.display = 'block';
    }
    
    if (aiResults) {
        aiResults.innerHTML = `
            <div class="ai-loading">
                <i class="fas fa-spinner fa-spin"></i> Analyzing "${food}"...
            </div>
        `;
    }
    
    try {
        const response = await fetchAPI('/ai/predict', {
            method: 'POST',
            body: JSON.stringify({ 
                food: food,
                category: category 
            })
        });
        
        if (response.success !== false) {
            const pred = response.prediction;
            const similar = response.similar_foods || [];
            
            // Update form fields with AI prediction
            const caloriesInput = document.getElementById('calories');
            const proteinInput = document.getElementById('protein');
            
            if (caloriesInput) caloriesInput.value = pred.calories;
            if (proteinInput) proteinInput.value = pred.protein;
            
            // Update confidence badge
            const confidenceBadge = document.getElementById('ai-confidence');
            if (confidenceBadge) {
                confidenceBadge.textContent = pred.confidence === 'high' ? 'High Confidence' : 
                                            pred.confidence === 'medium' ? 'Medium Confidence' : 'Low Confidence';
                
                if (pred.confidence === 'high') {
                    confidenceBadge.style.background = 'rgba(76, 201, 164, 0.2)';
                    confidenceBadge.style.color = 'var(--success)';
                } else if (pred.confidence === 'medium') {
                    confidenceBadge.style.background = 'rgba(255, 183, 77, 0.2)';
                    confidenceBadge.style.color = 'var(--warning)';
                } else {
                    confidenceBadge.style.background = 'rgba(255, 107, 107, 0.2)';
                    confidenceBadge.style.color = 'var(--danger)';
                }
            }
            
            // Show AI results
            if (aiResults) {
                let similarHTML = '';
                
                if (similar && similar.length > 0) {
                    similarHTML = `
                        <div class="similar-foods">
                            <div class="similar-header">
                                <i class="fas fa-lightbulb"></i>
                                <span>Similar foods in database:</span>
                            </div>
                            ${similar.map(food => `
                                <div class="similar-food-item">
                                    <span class="similar-food-name">${food.name}</span>
                                    <span class="similar-food-stats">
                                        ${food.calories_per_100g} cal • ${food.protein_per_100g}g protein
                                    </span>
                                </div>
                            `).join('')}
                        </div>
                    `;
                }
                
                aiResults.innerHTML = `
                    <div class="prediction-grid">
                        <div class="prediction-item">
                            <span class="prediction-label">Calories:</span>
                            <span class="prediction-value">${pred.calories} cal</span>
                        </div>
                        <div class="prediction-item">
                            <span class="prediction-label">Protein:</span>
                            <span class="prediction-value">${pred.protein}g</span>
                        </div>
                        <div class="prediction-item">
                            <span class="prediction-label">Quantity:</span>
                            <span class="prediction-value">${pred.quantity_g}g</span>
                        </div>
                        <div class="prediction-item">
                            <span class="prediction-label">Confidence:</span>
                            <span class="prediction-value confidence-${pred.confidence}">
                                ${pred.confidence.charAt(0).toUpperCase() + pred.confidence.slice(1)}
                            </span>
                        </div>
                    </div>
                    ${similarHTML}
                `;
            }
            
            // Validate the new values
            validateCalories();
            validateProtein();
            
            showNotification(`AI predicted ${pred.calories} calories and ${pred.protein}g protein`, 'success');
        } else {
            showNotification('AI prediction failed: ' + (response.error || 'Unknown error'), 'error');
        }
    } catch (error) {
        console.error('AI Prediction error:', error);
        if (aiResults) {
            aiResults.innerHTML = `
                <div class="ai-error">
                    <i class="fas fa-exclamation-triangle"></i>
                    <div class="error-content">
                        <h4>Unable to predict</h4>
                        <p>Please enter nutrient values manually.</p>
                        <small>Try being more specific (e.g., "Grilled Chicken 200g")</small>
                    </div>
                </div>
            `;
        }
        showNotification('Failed to get AI prediction. Check your connection.', 'error');
    }
}

// ------------------ Edit Meal ------------------

async function editMeal(entryId, date) {
    try {
        const meals = await fetchAPI(`/entries?date=${date}`);
        const mealToEdit = meals.find(m => m.id === entryId);
        
        if (!mealToEdit) { 
            showNotification('Could not find meal', 'error'); 
            return; 
        }
        
        currentEditId = mealToEdit.id || entryId;
        
        const editIndexInput = document.getElementById('edit-index');
        const editIdInput = document.getElementById('edit-id');
        const editFoodInput = document.getElementById('edit-food');
        const editCaloriesInput = document.getElementById('edit-calories');
        const editProteinInput = document.getElementById('edit-protein');
        const editCategoryInput = document.getElementById('edit-category');
        const editDateInput = document.getElementById('edit-date');
        
        if (editIndexInput) editIndexInput.value = entryId;
        if (editIdInput) editIdInput.value = currentEditId;
        if (editFoodInput) editFoodInput.value = mealToEdit.food;
        if (editCaloriesInput) editCaloriesInput.value = mealToEdit.calories;
        if (editProteinInput) editProteinInput.value = mealToEdit.protein;
        if (editCategoryInput) editCategoryInput.value = mealToEdit.category;
        if (editDateInput) editDateInput.value = mealToEdit.date;
        
        openModal(editModal);
    } catch (error) { 
        console.error('Error loading meal for editing:', error);
        showNotification('Failed to load meal for editing', 'error');
    }
}

async function updateMeal(e) {
    e.preventDefault();
    
    const editFoodInput = document.getElementById('edit-food');
    const editCaloriesInput = document.getElementById('edit-calories');
    const editProteinInput = document.getElementById('edit-protein');
    const editCategoryInput = document.getElementById('edit-category');
    const editDateInput = document.getElementById('edit-date');
    
    if (!editFoodInput || !editCaloriesInput || !editProteinInput || !editCategoryInput || !editDateInput) {
        showNotification('Edit form elements not found', 'error');
        return;
    }
    
    const updated = {
        food: editFoodInput.value.trim(),
        calories: parseInt(editCaloriesInput.value) || 0,
        protein: parseInt(editProteinInput.value) || 0,
        category: editCategoryInput.value,
        date: editDateInput.value,
        id: currentEditId
    };
    
    // Validate input
    const validationErrors = validateMealInput(updated);
    if (validationErrors.length > 0) {
        showNotification(validationErrors.join(', '), 'error');
        return;
    }
    
    try {
        await fetchAPI(`/entries/${currentEditId}`, { 
            method: 'PUT', 
            body: JSON.stringify(updated) 
        });
        
        showNotification('Meal updated successfully!', 'success');
        closeModal(editModal);
        await refreshAllData();
    } catch (error) { 
        console.error('Error updating meal:', error);
        showNotification(`Failed to update meal: ${error.message}`, 'error');
    }
}

async function deleteMeal() {
    if (!confirm('Are you sure you want to delete this meal? This action cannot be undone.')) return;
    
    try {
        await fetchAPI(`/entries/${currentEditId}`, { method: 'DELETE' });
        showNotification('Meal deleted successfully!', 'success');
        closeModal(editModal);
        await refreshAllData();
    } catch (error) { 
        console.error('Error deleting meal:', error);
        showNotification(`Failed to delete meal: ${error.message}`, 'error');
    }
}

// ------------------ Weekly Summary ------------------

async function loadWeeklySummary() {
    try {
        const weeklyData = await fetchAPI('/summary/week');
        updateWeeklyChart(weeklyData);
        updateWeeklyStats(weeklyData);
        updateTrendIndicator(weeklyData);
    } catch (error) { 
        console.error('Error loading weekly summary:', error);
    }
}

function updateTrendIndicator(data) {
    const trendIndicator = document.getElementById('trend-indicator');
    if (!trendIndicator || !data || data.length < 2) return;
    
    const recentDays = data.slice(-3);
    if (recentDays.length < 2) return;
    
    const avgProtein1 = recentDays[0].protein;
    const avgProtein2 = recentDays[recentDays.length - 1].protein;
    
    const diff = avgProtein2 - avgProtein1;
    const percentChange = avgProtein1 > 0 ? Math.round((diff / avgProtein1) * 100) : 0;
    
    const trendIcon = trendIndicator.querySelector('i');
    const trendText = trendIndicator.querySelector('span');
    
    if (percentChange > 5) {
        trendIcon.className = 'fas fa-arrow-up';
        trendText.textContent = `+${percentChange}%`;
        trendIndicator.style.background = 'rgba(76, 201, 164, 0.2)';
        trendIndicator.style.color = 'var(--success)';
    } else if (percentChange < -5) {
        trendIcon.className = 'fas fa-arrow-down';
        trendText.textContent = `${percentChange}%`;
        trendIndicator.style.background = 'rgba(255, 107, 107, 0.2)';
        trendIndicator.style.color = 'var(--danger)';
    } else {
        trendIcon.className = 'fas fa-minus';
        trendText.textContent = `${percentChange}%`;
        trendIndicator.style.background = 'rgba(160, 160, 208, 0.2)';
        trendIndicator.style.color = 'var(--text-secondary)';
    }
}

function updateChartTheme() {
    if (!weeklyChart) return;
    
    const isLightMode = document.body.classList.contains('light-mode');
    const gridColor = isLightMode ? 'rgba(0, 0, 0, 0.1)' : 'rgba(255, 255, 255, 0.1)';
    const textColor = isLightMode ? '#1a1a2e' : '#f0f0ff';
    
    weeklyChart.options.scales.x.grid.color = gridColor;
    weeklyChart.options.scales.x.ticks.color = textColor;
    weeklyChart.options.scales.y.grid.color = gridColor;
    weeklyChart.options.scales.y.ticks.color = textColor;
    weeklyChart.options.scales.y1.grid.color = gridColor;
    weeklyChart.options.scales.y1.ticks.color = textColor;
    weeklyChart.options.plugins.legend.labels.color = textColor;
    
    weeklyChart.update();
}

function updateWeeklyChart(data) {
    const ctx = document.getElementById('weeklyChart');
    if (!ctx) return;
    
    // Destroy existing chart if it exists
    if (weeklyChart) {
        weeklyChart.destroy();
    }
    
    // Ensure data is an array
    if (!Array.isArray(data)) {
        console.error('updateWeeklyChart: data is not an array:', data);
        data = [];
    }
    
    if (!data || data.length === 0) { 
        ctx.parentElement.innerHTML = `
            <div class="empty-state" style="padding: 40px 20px;">
                <i class="fas fa-chart-bar"></i>
                <h3>No weekly data</h3>
                <p>Log meals for 7 days to see your progress</p>
            </div>
        `; 
        return; 
    }
    
    const labels = data.map(d => {
        const date = new Date(d.date);
        return date.toLocaleDateString('en-US', { weekday: 'short' });
    });
    
    const caloriesData = data.map(d => d.calories);
    const proteinData = data.map(d => d.protein);
    
    const isLightMode = document.body.classList.contains('light-mode');
    const gridColor = isLightMode ? 'rgba(0, 0, 0, 0.1)' : 'rgba(255, 255, 255, 0.1)';
    const textColor = isLightMode ? '#1a1a2e' : '#f0f0ff';
    
    weeklyChart = new Chart(ctx.getContext('2d'), {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                { 
                    label: 'Calories', 
                    data: caloriesData, 
                    backgroundColor: 'rgba(108, 99, 255, 0.7)',
                    borderColor: 'rgba(108, 99, 255, 1)',
                    borderWidth: 1,
                    borderRadius: 6,
                    yAxisID: 'y' 
                },
                { 
                    label: 'Protein (g)', 
                    data: proteinData, 
                    backgroundColor: 'rgba(76, 201, 164, 0.7)',
                    borderColor: 'rgba(76, 201, 164, 1)',
                    borderWidth: 2,
                    type: 'line', 
                    yAxisID: 'y1',
                    tension: 0.4,
                    fill: false
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false,
            },
            scales: {
                y: { 
                    beginAtZero: true, 
                    position: 'left', 
                    title: { 
                        display: true, 
                        text: 'Calories',
                        color: textColor
                    },
                    grid: {
                        color: gridColor
                    },
                    ticks: {
                        color: textColor,
                        callback: function(value) {
                            return value.toLocaleString();
                        }
                    }
                },
                y1: { 
                    beginAtZero: true, 
                    position: 'right', 
                    title: { 
                        display: true, 
                        text: 'Protein (g)',
                        color: textColor
                    }, 
                    grid: { 
                        drawOnChartArea: false 
                    },
                    ticks: {
                        color: textColor
                    }
                },
                x: {
                    grid: {
                        color: gridColor
                    },
                    ticks: {
                        color: textColor
                    }
                }
            },
            plugins: { 
                legend: { 
                    position: 'top',
                    labels: {
                        color: textColor,
                        font: {
                            size: 12
                        }
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(26, 26, 46, 0.9)',
                    titleColor: '#fff',
                    bodyColor: '#fff',
                    borderColor: 'rgba(108, 99, 255, 0.5)',
                    borderWidth: 1,
                    cornerRadius: 8,
                    displayColors: true,
                    callbacks: {
                        label: function(context) {
                            let label = context.dataset.label || '';
                            if (label) {
                                label += ': ';
                            }
                            if (context.parsed.y !== null) {
                                label += context.parsed.y.toLocaleString();
                                if (context.dataset.label === 'Protein (g)') {
                                    label += 'g';
                                }
                            }
                            return label;
                        }
                    }
                }
            }
        }
    });
}

function updateWeeklyStats(data) {
    const avgCalEl = document.getElementById('weekly-avg-cal');
    const avgProtEl = document.getElementById('weekly-avg-prot');
    const goalDaysEl = document.getElementById('weekly-goal-days');
    
    if (!avgCalEl || !avgProtEl || !goalDaysEl) return;
    
    if (!Array.isArray(data) || data.length === 0) { 
        avgCalEl.textContent = '0';
        avgProtEl.textContent = '0g';
        goalDaysEl.textContent = '0/7';
        return; 
    }
    
    const totalCal = data.reduce((a,b) => a + b.calories, 0);
    const totalProt = data.reduce((a,b) => a + b.protein, 0);
    const goalDays = data.filter(d => d.met_goal).length;
    
    avgCalEl.textContent = Math.round(totalCal / data.length).toLocaleString();
    avgProtEl.textContent = Math.round(totalProt / data.length) + 'g';
    goalDaysEl.textContent = `${goalDays}/${data.length}`;
}

// ------------------ Recent Days ------------------

async function loadRecentDays() {
    try {
        const entries = await fetchAPI('/entries');
        
        // Ensure entries is an array
        if (!Array.isArray(entries)) {
            console.error('loadRecentDays: entries is not an array:', entries);
            return;
        }
        
        const days = {};
        
        // Group entries by date
        entries.forEach(entry => {
            if (!days[entry.date]) {
                days[entry.date] = {
                    meals: 0,
                    calories: 0,
                    protein: 0
                };
            }
            days[entry.date].meals++;
            days[entry.date].calories += entry.calories;
            days[entry.date].protein += entry.protein;
        });
        
        // Sort dates (most recent first)
        const sortedDates = Object.keys(days).sort((a, b) => b.localeCompare(a));
        
        // Display recent days (last 5 days with data)
        const recentDaysList = document.getElementById('recent-days-list');
        if (!recentDaysList) return;
        
        recentDaysList.innerHTML = '';
        
        const today = new Date().toISOString().split('T')[0];
        const currentViewDateStr = currentViewDate.toISOString().split('T')[0];
        
        sortedDates.slice(0, 5).forEach(date => {
            const dayData = days[date];
            const dateObj = new Date(date);
            const dayName = formatDateDisplay(dateObj);
            
            const isActive = date === currentViewDateStr;
            
            const dayItem = document.createElement('div');
            dayItem.className = `recent-day-item ${isActive ? 'active' : ''}`;
            dayItem.innerHTML = `
                <div class="day-indicator">
                    <div class="day-dot ${date === today ? 'today' : ''}"></div>
                </div>
                <div class="recent-day-info">
                    <div class="recent-day-name">${dayName}</div>
                    <div class="recent-day-date">${date}</div>
                </div>
                <div class="recent-day-stats">
                    <div class="day-calories">${dayData.calories.toLocaleString()} cal</div>
                    <div class="day-protein">${dayData.protein}g protein</div>
                </div>
                <i class="fas fa-chevron-right day-arrow"></i>
            `;
            
            // Make it clickable to view that day
            dayItem.addEventListener('click', () => {
                currentViewDate = new Date(date);
                updateDateDisplay();
                window.scrollTo({ top: 0, behavior: 'smooth' });
            });
            
            recentDaysList.appendChild(dayItem);
        });
        
        if (sortedDates.length === 0) {
            recentDaysList.innerHTML = `
                <div class="empty-state" style="padding: 40px 20px;">
                    <i class="fas fa-history"></i>
                    <h3>No recent days</h3>
                    <p>Log meals to see your history here</p>
                </div>
            `;
        }
    } catch (error) { 
        console.error('Error loading recent days:', error);
    }
}

// ------------------ Quick Stats & Common Foods ------------------

function updateQuickStats() {
    const totalMealsEl = document.getElementById('total-meals');
    const avgDailyCalEl = document.getElementById('avg-daily-cal');
    const goalRateEl = document.getElementById('goal-rate');
    
    if (!totalMealsEl || !avgDailyCalEl || !goalRateEl) return;
    
    if (!Array.isArray(allEntries) || allEntries.length === 0) {
        totalMealsEl.textContent = '0';
        avgDailyCalEl.textContent = '0';
        goalRateEl.textContent = '0%';
        return;
    }
    
    const uniqueDays = [...new Set(allEntries.map(e => e.date))];
    const dailyCalories = {};
    
    allEntries.forEach(e => {
        dailyCalories[e.date] = (dailyCalories[e.date] || 0) + e.calories;
    });
    
    const avgCal = Math.round(Object.values(dailyCalories).reduce((a, b) => a + b, 0) / uniqueDays.length);
    const goalRate = uniqueDays.length > 0 ? Math.round((uniqueDays.length / 7) * 100) : 0;
    
    totalMealsEl.textContent = allEntries.length.toLocaleString();
    avgDailyCalEl.textContent = avgCal.toLocaleString();
    goalRateEl.textContent = `${goalRate}%`;
    
    // Update trend indicators
    updateStatTrends();
}

function updateStatTrends() {
    const trendElements = document.querySelectorAll('.stat-trend');
    if (trendElements.length === 0 || !Array.isArray(allEntries) || allEntries.length < 2) return;
    
    // Simple trend calculation based on last 7 days
    const dates = [...new Set(allEntries.map(e => e.date))].sort().slice(-7);
    const dailyStats = dates.map(date => {
        const dayEntries = allEntries.filter(e => e.date === date);
        return {
            calories: dayEntries.reduce((sum, e) => sum + e.calories, 0),
            protein: dayEntries.reduce((sum, e) => sum + e.protein, 0),
            meals: dayEntries.length
        };
    });
    
    if (dailyStats.length < 2) return;
    
    const recentAvg = dailyStats.slice(-3).reduce((sum, day) => sum + day.calories, 0) / 3;
    const olderAvg = dailyStats.slice(0, 3).reduce((sum, day) => sum + day.calories, 0) / 3;
    
    const calorieTrend = olderAvg > 0 ? ((recentAvg - olderAvg) / olderAvg) * 100 : 0;
    
    trendElements.forEach((trend, index) => {
        if (index === 1) { // Avg Calories trend
            if (calorieTrend > 5) {
                trend.className = 'stat-trend up';
                trend.innerHTML = '<i class="fas fa-arrow-up"></i> <span>+' + Math.round(calorieTrend) + '%</span>';
            } else if (calorieTrend < -5) {
                trend.className = 'stat-trend down';
                trend.innerHTML = '<i class="fas fa-arrow-down"></i> <span>' + Math.round(calorieTrend) + '%</span>';
            } else {
                trend.className = 'stat-trend neutral';
                trend.innerHTML = '<i class="fas fa-minus"></i> <span>' + Math.round(calorieTrend) + '%</span>';
            }
        }
    });
}

async function loadCommonFoods() {
    try {
        const commonFoods = await fetchAPI('/analytics/common-foods');
        const commonFoodsContainer = document.getElementById('common-foods');
        
        if (!commonFoodsContainer) return;
        
        if (commonFoods.length > 0) {
            let html = '<div class="common-foods-header"><i class="fas fa-star"></i> Most Common Foods</div>';
            
            commonFoods.slice(0, 3).forEach(food => {
                const percentage = Math.round((food.count / allEntries.length) * 100);
                html += `
                    <div class="common-food-item">
                        <span class="common-food-name">${food.food}</span>
                        <div class="common-food-bar">
                            <div class="common-food-progress" style="width: ${percentage}%"></div>
                        </div>
                        <span class="common-food-count">${food.count} (${percentage}%)</span>
                    </div>
                `;
            });
            
            commonFoodsContainer.innerHTML = html;
        } else {
            commonFoodsContainer.innerHTML = '';
        }
    } catch (error) {
        console.error('Failed to load common foods:', error);
        // Don't show error notification for this non-critical feature
    }
}

// ------------------ Export/Import ------------------

async function exportData() {
    try {
        showNotification('Preparing export...', 'info');
        
        const response = await fetchAPI('/export');
        const dataStr = JSON.stringify(response, null, 2);
        const blob = new Blob([dataStr], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        
        const today = new Date().toISOString().split('T')[0];
        const a = document.createElement('a');
        a.href = url;
        a.download = `nutritrack-export-${today}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        showNotification('Data exported successfully!', 'success');
    } catch (error) {
        console.error('Export error:', error);
        showNotification('Failed to export data: ' + error.message, 'error');
    }
}

async function handleFileImport(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    // Reset file input
    event.target.value = '';
    
    try {
        showNotification('Importing data...', 'info');
        
        const text = await file.text();
        const data = JSON.parse(text);
        
        if (!data.entries || !Array.isArray(data.entries)) {
            showNotification('Invalid file format. Expected JSON with entries array.', 'error');
            return;
        }
        
        // Validate entries before importing
        const validEntries = data.entries.filter(entry => 
            entry.food && 
            typeof entry.calories === 'number' && 
            typeof entry.protein === 'number' &&
            entry.date
        );
        
        if (validEntries.length === 0) {
            showNotification('No valid entries found in file', 'error');
            return;
        }
        
        // Confirm import
        if (!confirm(`Import ${validEntries.length} meals from ${new Date(data.export_date || Date.now()).toLocaleDateString()}?`)) {
            return;
        }
        
        // Upload each entry
        let successCount = 0;
        let errorCount = 0;
        
        for (const entry of validEntries) {
            try {
                await fetchAPI('/entries', {
                    method: 'POST',
                    body: JSON.stringify(entry)
                });
                successCount++;
            } catch (error) {
                console.error('Failed to import entry:', entry, error);
                errorCount++;
            }
        }
        
        if (successCount > 0) {
            showNotification(`Successfully imported ${successCount} of ${validEntries.length} entries`, 'success');
            await refreshAllData();
        } else {
            showNotification('Failed to import any entries', 'error');
        }
        
        if (errorCount > 0) {
            console.warn(`${errorCount} entries failed to import`);
        }
    } catch (error) {
        console.error('Import error:', error);
        showNotification('Failed to import data: ' + error.message, 'error');
    }
}

// ------------------ Modal Functions ------------------

async function showHealthCheck() {
    try {
        openModal(healthModal);
        
        const healthStatus = document.getElementById('health-status');
        healthStatus.innerHTML = `
            <div class="health-loading">
                <i class="fas fa-spinner fa-spin"></i> Checking system health...
            </div>
        `;
        
        const response = await fetchAPI('/health');
        
        healthStatus.innerHTML = `
            <div class="health-status-card">
                <div class="health-status-header">
                    <i class="fas fa-check-circle" style="color: #4cc9a4;"></i>
                    <h3>System Status: Healthy</h3>
                </div>
                <div class="health-details">
                    <div class="health-item">
                        <span class="health-label">API Status:</span>
                        <span class="health-value healthy">Operational</span>
                    </div>
                    <div class="health-item">
                        <span class="health-label">AI Features:</span>
                        <span class="health-value ${response.ai_enabled ? 'healthy' : 'warning'}">
                            ${response.ai_enabled ? 'Enabled' : 'Disabled'}
                        </span>
                    </div>
                    <div class="health-item">
                        <span class="health-label">Total Entries:</span>
                        <span class="health-value">${response.entries_count || 0}</span>
                    </div>
                    <div class="health-item">
                        <span class="health-label">Last Check:</span>
                        <span class="health-value">${new Date(response.timestamp).toLocaleTimeString()}</span>
                    </div>
                </div>
            </div>
        `;
    } catch (error) {
        console.error('Health check error:', error);
        const healthStatus = document.getElementById('health-status');
        healthStatus.innerHTML = `
            <div class="health-status-card error">
                <div class="health-status-header">
                    <i class="fas fa-exclamation-triangle" style="color: #ff6b6b;"></i>
                    <h3>System Status: Unhealthy</h3>
                </div>
                <div class="health-details">
                    <div class="health-item">
                        <span class="health-label">Error:</span>
                        <span class="health-value error">${error.message}</span>
                    </div>
                    <div class="health-item">
                        <span class="health-label">Recommendation:</span>
                        <span class="health-value">Check server connection and restart if needed</span>
                    </div>
                </div>
            </div>
        `;
    }
}

async function showDatabaseInfo() {
    try {
        openModal(databaseModal);
        
        const dbInfo = document.getElementById('database-info-content');
        dbInfo.innerHTML = `
            <div class="info-loading">
                <i class="fas fa-spinner fa-spin"></i> Loading database information...
            </div>
        `;
        
        const response = await fetchAPI('/ai/status');
        
        dbInfo.innerHTML = `
            <div class="database-info-card">
                <div class="db-info-header">
                    <i class="fas fa-database"></i>
                    <h3>Food Database</h3>
                </div>
                <div class="db-details">
                    <div class="db-item">
                        <span class="db-label">Total Foods:</span>
                        <span class="db-value">${response.foods_in_database || 0}</span>
                    </div>
                    <div class="db-item">
                        <span class="db-label">AI Status:</span>
                        <span class="db-value ${response.enabled ? 'healthy' : 'warning'}">
                            ${response.enabled ? 'Active' : 'Disabled'}
                        </span>
                    </div>
                </div>
                <div class="db-tips">
                    <h4><i class="fas fa-lightbulb"></i> Tips</h4>
                    <p>The AI can predict nutrients for 200+ foods including Vietnamese dishes.</p>
                    <p>Include weight in descriptions for better accuracy (e.g., "chicken 200g").</p>
                </div>
            </div>
        `;
    } catch (error) {
        console.error('Database info error:', error);
        const dbInfo = document.getElementById('database-info-content');
        dbInfo.innerHTML = `
            <div class="database-info-card error">
                <div class="db-info-header">
                    <i class="fas fa-exclamation-triangle"></i>
                    <h3>Database Unavailable</h3>
                </div>
                <p>Unable to load database information. The AI predictor may be disabled.</p>
            </div>
        `;
    }
}

function showKeyboardHelp() {
    openModal(helpModal);
}

// ------------------ Notifications ------------------

function showNotification(message, type = 'info') {
    // Remove existing notifications
    const existing = document.querySelector('.notification');
    if (existing) existing.remove();
    
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    
    // Set icon based on type
    let icon = 'fas fa-info-circle';
    if (type === 'success') icon = 'fas fa-check-circle';
    if (type === 'error') icon = 'fas fa-exclamation-triangle';
    if (type === 'warning') icon = 'fas fa-exclamation-circle';
    
    notification.innerHTML = `
        <div class="notification-content">
            <i class="${icon}"></i>
            <span>${message}</span>
        </div>
        <button class="notification-close" onclick="this.parentElement.remove()">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    // Add to document
    document.body.appendChild(notification);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (notification.parentElement) {
            notification.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => {
                if (notification.parentElement) notification.remove();
            }, 300);
        }
    }, 5000);
}

// ------------------ Keyboard Shortcuts ------------------

function handleKeyboardShortcuts(e) {
    // Ctrl+E or Cmd+E to export
    if ((e.ctrlKey || e.metaKey) && e.key === 'e') {
        e.preventDefault();
        exportData();
    }
    
    // Escape to close any open modal
    if (e.key === 'Escape') {
        const openModal = document.querySelector('.modal[style*="display: block"]');
        if (openModal) {
            closeModal(openModal);
        }
    }
    
    // Focus search when pressing slash (if not in input)
    if (e.key === '/' && !['INPUT', 'TEXTAREA'].includes(e.target.tagName)) {
        e.preventDefault();
        const foodInput = document.getElementById('food-name');
        if (foodInput) {
            foodInput.focus();
        }
    }
}

// Make functions globally available
window.editMeal = editMeal;
window.predictNutrients = predictNutrients;
window.exportData = exportData;
window.showNotification = showNotification;