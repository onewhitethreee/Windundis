document.addEventListener('DOMContentLoaded', () => {
    // --- STATE MANAGEMENT ---
    const state = {
        isOpen: false,
        metrics: null,
        goals: [],
        selectedGoalId: null,
    };

    // --- DOM ELEMENTS ---
    const elements = {
        container: document.getElementById('container'),
        modalOverlay: document.getElementById('modalOverlay'),
        sidebar: document.getElementById('sidebar'),
        messagesContainer: document.getElementById('messagesContainer'),
        inputField: document.getElementById('inputField'),
        sendBtn: document.getElementById('sendBtn'),
        openBtn: document.getElementById('openCopilotBtn'),
        headerStatus: document.getElementById('headerStatus'),
        goalsList: document.getElementById('goalsList'),
        incomeStat: document.getElementById('incomeStat'),
        expensesStat: document.getElementById('expensesStat'),
        balanceStat: document.getElementById('balanceStat'),
        // Modal elements
        createGoalModalContainer: document.getElementById('createGoalModalContainer'),
        createGoalBtn: document.getElementById('createGoalBtn'),
        closeGoalModalBtn: document.getElementById('closeGoalModalBtn'),
        cancelGoalBtn: document.getElementById('cancelGoalBtn'),
        createGoalSubmitBtn: document.getElementById('createGoalSubmitBtn'),
        goalForm: {
            title: document.getElementById('goalTitle'),
            description: document.getElementById('goalDescription'),
            target: document.getElementById('goalTarget'),
            current: document.getElementById('goalCurrent'),
            deadline: document.getElementById('goalDeadline'),
            priority: document.getElementById('goalPriority'),
            strategy: document.getElementById('goalStrategy'),
        }
    };

    // --- MOCK DATA ---
    const categoryData = {
        income: { 'Salario': 2500.00 },
        expenses: {
            'Comida | Supermercado': 45.50, 'Comida | Restaurante': 55.00, 'Comida | Bar/Café': 22.50,
            'Transporte | Combustible': 60.00, 'Servicios | Peluquería': 25.00, 'Servicios | Internet/Telefonía': 35.00,
            'Compras | Ropa': 89.99, 'Compras | Electrónica': 0.00, 'Ocio | Cine/Entretenimiento': 42.00,
            'Ocio | Viajes': 150.00, 'Banca | Comisión': 2.40
        }
    };

    // --- API & DATA FUNCTIONS ---
    async function loadFinancialData() {
        return new Promise(resolve => {
            setTimeout(() => {
                const mockData = {
                    analysis: { total_income: 2500.00, total_expenses: 540.38, balance: 1959.62 },
                };
                state.metrics = mockData;
                resolve(mockData);
            }, 1000);
        });
    }

    function generateGoals(data) {
        const { analysis } = data;
        const monthlyIncome = analysis.total_income;

        return [
            { id: 1, title: 'Fondo de Emergencia', target: monthlyIncome * 3, current: analysis.balance * 0.4, deadline: '6 meses', description: 'Ahorrar 3 meses de gastos para emergencias.', strategy: 'Ahorra 100€ mensuales automáticamente.', priority: 'high' },
            { id: 2, title: 'Reducir Gastos Viajes', target: 100, current: Math.max(0, 150 - 50), deadline: '1 mes', description: 'Reducir gasto en viajes de 150€ a 100€.', strategy: 'Compara precios 2 semanas antes de viajar.', priority: 'medium' },
            { id: 3, title: 'Objetivo Anual', target: monthlyIncome * 12 * 0.25, current: analysis.balance * 0.8, deadline: '1 año', description: 'Ahorrar el 25% de ingresos anuales.', strategy: 'Mantén automatización de 20% mensual.', priority: 'high' },
            { id: 4, title: 'Invertir en Fondos', target: 5000, current: 0, deadline: '6 meses', description: 'Alcanzar 5000€ para inversión inicial.', strategy: 'Transfiere 500€ de tu ahorro actual cada mes.', priority: 'medium' }
        ];
    }

    // --- RENDER FUNCTIONS ---
    function renderGoals() {
        const priorityOrder = { 'high': 3, 'medium': 2, 'low': 1 };
        const sortedGoals = [...state.goals].sort((a, b) => {
            if (priorityOrder[a.priority] !== priorityOrder[b.priority]) {
                return priorityOrder[b.priority] - priorityOrder[a.priority];
            }
            return (b.current / b.target) - (a.current / a.target);
        });

        elements.goalsList.innerHTML = sortedGoals.map(goal => {
            const progress = Math.min((goal.current / goal.target) * 100, 100);
            const priorityIcon = goal.priority === 'high' ? '🔴' : goal.priority === 'medium' ? '🟡' : '🟢';
            const isCompleted = progress >= 100;

            return `
                <div class="goal-card ${isCompleted ? 'completed' : ''} ${goal.id === state.selectedGoalId ? 'selected' : ''}" data-goal-id="${goal.id}">
                    <div class="goal-title">${priorityIcon} ${goal.title} ${isCompleted ? ' <span style="color: #48bb78; font-size: 10px;">✓</span>' : ''}</div>
                    <div class="goal-progress"><div class="goal-progress-bar" style="width: ${progress}%"></div></div>
                    <div class="goal-percent">${progress.toFixed(0)}% · ${goal.current.toFixed(0)}€ / ${goal.target.toFixed(0)}€</div>
                </div>
            `;
        }).join('');
    }

    function addMessage(role, content) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}`;
        messageDiv.innerHTML = `
            ${role === 'assistant' ? '<div class="message-icon"><i class="fas fa-lightbulb"></i></div>' : ''}
            <div class="message-bubble">${content}</div>
            ${role === 'user' ? '<div class="message-icon"><i class="fas fa-user"></i></div>' : ''}
        `;
        elements.messagesContainer.appendChild(messageDiv);
        elements.messagesContainer.scrollTop = elements.messagesContainer.scrollHeight;
    }

    // --- UI & EVENT HANDLERS ---
    function selectGoal(goalId) {
        state.selectedGoalId = goalId;
        renderGoals(); // Re-render to update the 'selected' class
        elements.messagesContainer.innerHTML = '';
        const goal = state.goals.find(g => g.id === goalId);
        if (goal) {
            showGoalDetails(goal);
        }
    }

    function handleSendMessage() {
        const userInput = elements.inputField.value.trim();
        if (!userInput) return;

        addMessage('user', escapeHtml(userInput));
        elements.inputField.value = '';
        elements.sendBtn.disabled = true;

        setTimeout(() => {
            let response = 'Selecciona una meta en la izquierda para obtener recomendaciones personalizadas.';
            if (state.selectedGoalId) {
                const goal = state.goals.find(g => g.id === state.selectedGoalId);
                response = getGoalResponse(userInput, goal);
            }
            addMessage('assistant', response);
            elements.sendBtn.disabled = false;
            elements.inputField.focus();
        }, 500);
    }

    function showGoalDetails(goal) {
        const remaining = goal.target - goal.current;
        const progress = (goal.current / goal.target) * 100;
        const message = `
            <div style="color: var(--color-text-primary); line-height: 1.8;">
                <strong>🎯 ${goal.title}</strong><br>
                <span style="font-size: 12px; color: var(--color-text-light);">Prioridad: ${goal.priority === 'high' ? '🔴 Alta' : '🟡 Media'}</span><br><br>
                <strong>Meta:</strong> ${goal.target.toFixed(2)}€<br>
                <strong>Progreso:</strong> ${goal.current.toFixed(2)}€ (${progress.toFixed(0)}%)<br>
                <strong>Falta:</strong> ${remaining > 0 ? remaining.toFixed(2) : 0}€<br>
                <strong>Plazo:</strong> ${goal.deadline}<br><br>
                <strong>📋 Descripción:</strong><br>${goal.description}<br><br>
                <strong>💡 Estrategia:</strong><br>${goal.strategy}
            </div>
        `;
        addMessage('assistant', message);
    }

    function openCopilot() {
        state.isOpen = true;
        elements.container.classList.add('show');
        elements.modalOverlay.classList.add('show');
        elements.openBtn.classList.remove('show');
        elements.inputField.focus();
    }

    function closeCopilot() {
        state.isOpen = false;
        elements.container.classList.remove('show');
        elements.modalOverlay.classList.remove('show');
        elements.openBtn.classList.add('show');
    }

    function openCreateGoalModal() {
        elements.createGoalModalContainer.classList.add('show');
        elements.goalForm.title.focus();
    }

    function closeCreateGoalModal() {
        elements.createGoalModalContainer.classList.remove('show');
        // Reset form
        Object.values(elements.goalForm).forEach(input => input.value = '');
        elements.goalForm.deadline.value = '6 meses';
        elements.goalForm.priority.value = 'medium';
    }

    function createNewGoal() {
        const { title, description, target, current, deadline, priority, strategy } = elements.goalForm;

        if (!title.value.trim()) { alert('Por favor, ingresa un título.'); return; }
        const targetValue = parseFloat(target.value);
        if (!targetValue || targetValue <= 0) { alert('La meta debe ser mayor a 0.'); return; }
        const currentValue = parseFloat(current.value) || 0;
        if (currentValue < 0) { alert('El ahorro actual no puede ser negativo.'); return; }
        if (currentValue > targetValue) { alert('El ahorro actual no puede ser mayor que la meta.'); return; }

        const newGoal = {
            id: Date.now(),
            title: title.value.trim(),
            target: targetValue,
            current: currentValue,
            deadline: deadline.value,
            description: description.value.trim() || `Meta personalizada: ${title.value.trim()}`,
            strategy: strategy.value.trim() || 'Define tu estrategia personalizada.',
            priority: priority.value
        };

        state.goals.push(newGoal);
        closeCreateGoalModal();
        selectGoal(newGoal.id);
        addMessage('assistant', `¡Perfecto! He creado tu nueva meta "${newGoal.title}".`);
    }

    // --- UTILITY FUNCTIONS ---
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    function getGoalResponse(userInput, goal) {
        const input = userInput.toLowerCase();
        // Simplified response logic from the original code
        if (input.includes('cómo') || input.includes('estrategia')) {
            return `Para lograr "${goal.title}": ${goal.strategy}.`;
        } else if (input.includes('cuánto') || input.includes('falta')) {
            const remaining = goal.target - goal.current;
            return `Te falta ${remaining.toFixed(2)}€ para completar "${goal.title}". ¡Sigue así!`;
        } else {
            return `Sobre "${goal.title}": ${goal.description}. Tu estrategia es: ${goal.strategy}. ¿Necesitas más detalles?`;
        }
    }

    function showBreakdown(type) {
        const data = categoryData[type];
        const title = type === 'income' ? 'Ingresos' : 'Gastos';
        const sign = type === 'income' ? '+' : '−';

        const breakdownHTML = Object.entries(data)
            .map(([cat, amount]) => `<div style="padding: 4px 0;">${cat}: <strong>${sign}${amount.toFixed(2)}€</strong></div>`)
            .join('');
        const total = Object.values(data).reduce((a, b) => a + b, 0);

        addMessage('assistant', `
            <div style="color: var(--color-text-primary); line-height: 1.6;">
                <strong>📊 Desglose de ${title}</strong><br><br>
                ${breakdownHTML}
                <div style="border-top: 1px solid #e2e8f0; margin-top: 8px; padding-top: 8px; font-weight: 700;">
                    Total: ${sign}${total.toFixed(2)}€
                </div>
            </div>
        `);
    }

    // --- INITIALIZATION ---
    function bindEventListeners() {
        elements.openBtn.addEventListener('click', openCopilot);
        elements.modalOverlay.addEventListener('click', closeCopilot);
        elements.container.addEventListener('click', e => e.stopPropagation());

        elements.sendBtn.addEventListener('click', handleSendMessage);
        elements.inputField.addEventListener('keypress', e => {
            if (e.key === 'Enter' && !elements.sendBtn.disabled) handleSendMessage();
        });

        // Event Delegation for dynamic elements
        elements.goalsList.addEventListener('click', e => {
            const goalCard = e.target.closest('.goal-card');
            if (goalCard) {
                const goalId = parseInt(goalCard.dataset.goalId, 10);
                selectGoal(goalId);
            }
        });

        elements.sidebar.addEventListener('click', e => {
            const statCard = e.target.closest('.stat-card');
            if (!statCard) return;
            const action = statCard.dataset.action;
            if (action === 'showIncome') showBreakdown('income');
            if (action === 'showExpenses') showBreakdown('expenses');
        });

        // Modal event listeners
        elements.createGoalBtn.addEventListener('click', openCreateGoalModal);
        elements.closeGoalModalBtn.addEventListener('click', closeCreateGoalModal);
        elements.cancelGoalBtn.addEventListener('click', closeCreateGoalModal);
        elements.createGoalSubmitBtn.addEventListener('click', createNewGoal);
        elements.createGoalModalContainer.addEventListener('click', e => {
            if (e.target === elements.createGoalModalContainer) closeCreateGoalModal();
        });
    }

    async function initialize() {
        elements.openBtn.classList.add('show');
        try {
            const data = await loadFinancialData();
            state.goals = generateGoals(data);

            elements.incomeStat.textContent = `+${data.analysis.total_income.toFixed(2)}€`;
            elements.expensesStat.textContent = `−${data.analysis.total_expenses.toFixed(2)}€`;
            elements.balanceStat.textContent = `${data.analysis.balance.toFixed(2)}€`;
            elements.balanceStat.classList.add('positive');

            elements.messagesContainer.innerHTML = `
                <div class="initial-message">
                    <div class="initial-message-icon" style="font-size: 64px;"><i class="fas fa-trophy"></i></div>
                    <p><strong>Bienvenido a tus Metas Financieras</strong><br>Selecciona una meta para ver detalles.</p>
                </div>
            `;

            elements.headerStatus.textContent = 'Listo';
            elements.inputField.disabled = false;
            elements.sendBtn.disabled = false;

            selectGoal(1); // Select the first goal by default
            bindEventListeners();

        } catch (error) {
            console.error('Initialization Error:', error);
            addMessage('assistant', 'Error al cargar los datos. Por favor, inténtalo más tarde.');
        }
    }

    initialize();
});
