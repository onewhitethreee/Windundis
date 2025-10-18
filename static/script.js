document.addEventListener('DOMContentLoaded', () => {
    // --- STATE MANAGEMENT ---
    const state = {
        isOpen: false,
        metrics: null,
        goals: [],
        selectedGoalId: null,
        chatHistory: {},
        initialized: false, 
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

    async function getAIResponse(userInput, goal) {
        try {
            const requestData = {
                question: userInput,
                goal: goal ? {
                    title: goal.title,
                    description: goal.description,
                    current: goal.current,
                    target: goal.target
                } : null
            };

            console.log('Sending AI request:', requestData);

            const response = await fetch('/api/ai/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestData)
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            console.log('AI response:', result);
            
            if (result.success) {
                return result.data.response;
            } else {
                throw new Error(result.error || 'Error desconocido');
            }
        } catch (error) {
            console.error('Error calling AI API:', error);
            if (goal) {
                return `Sobre tu meta "${goal.title}": ${goal.description}. Tu estrategia es: ${goal.strategy}. ¿Necesitas más detalles?`;
            } else {
                return 'Selecciona una meta en la izquierda para obtener recomendaciones personalizadas.';
            }
        }
    }

    async function getMotivationalMessage(goal) {
        try {
            const progress = (goal.current / goal.target) * 100;
            const requestData = {
                progress: progress,
                title: goal.title
            };

            const response = await fetch('/api/ai/motivation', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestData)
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            
            if (result.success) {
                return result.data.motivation;
            } else {
                throw new Error(result.error || 'Error desconocido');
            }
        } catch (error) {
            console.error('Error getting motivation:', error);
            const progress = (goal.current / goal.target) * 100;
            if (progress >= 100) {
                return `🎉 ¡Felicidades! Has completado tu meta "${goal.title}". ¡Eres increíble!`;
            } else if (progress >= 75) {
                return `💪 ¡Estás muy cerca! Has completado el ${progress.toFixed(0)}% de "${goal.title}". ¡Solo un poco más!`;
            } else if (progress >= 50) {
                return `🚀 ¡Excelente progreso! Has completado el ${progress.toFixed(0)}% de "${goal.title}". ¡Sigue así!`;
            } else {
                return `🌟 ¡Buen comienzo! Has completado el ${progress.toFixed(0)}% de "${goal.title}". ¡Cada paso cuenta!`;
            }
        }
    }

    async function getTaskSubtasks(task) {
        try {
            const requestData = {
                task: task
            };

            const response = await fetch('/api/ai/subtasks', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestData)
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            
            if (result.success) {
                return result.data.subtasks;
            } else {
                throw new Error(result.error || 'Error desconocido');
            }
        } catch (error) {
            console.error('Error getting subtasks:', error);
            return `
                <div style="color: var(--color-text-primary); line-height: 1.6;">
                    <strong>📋 Plan para "${task}":</strong><br><br>
                    1. <strong>Definir presupuesto:</strong> Establece cuánto necesitas ahorrar<br>
                    2. <strong>Crear timeline:</strong> Define fechas límite realistas<br>
                    3. <strong>Automatizar ahorros:</strong> Configura transferencias automáticas<br>
                    4. <strong>Monitorear progreso:</strong> Revisa semanalmente tu avance<br>
                    5. <strong>Ajustar estrategia:</strong> Modifica el plan según sea necesario<br><br>
                    <em>💡 Consejo: Empieza con pasos pequeños y celebra cada logro.</em>
                </div>
            `;
        }
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
            
            const chatCount = state.chatHistory[goal.id] ? state.chatHistory[goal.id].length : 0;
            const chatIndicator = chatCount > 0 ? ` <span class="chat-indicator" title="${chatCount} mensajes">💬 ${chatCount}</span>` : '';

            return `
                <div class="goal-card ${isCompleted ? 'completed' : ''} ${goal.id === state.selectedGoalId ? 'selected' : ''}" data-goal-id="${goal.id}">
                    <div class="goal-title">${priorityIcon} ${goal.title} ${isCompleted ? ' <span style="color: #48bb78; font-size: 10px;">✓</span>' : ''}${chatIndicator}</div>
                    <div class="goal-progress"><div class="goal-progress-bar" style="width: ${progress}%"></div></div>
                    <div class="goal-percent">${progress.toFixed(0)}% · ${goal.current.toFixed(0)}€ / ${goal.target.toFixed(0)}€</div>
                </div>
            `;
        }).join('');
    }

    function addMessage(role, content, saveToHistory = true) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}`;
        messageDiv.innerHTML = `
            ${role === 'assistant' ? '<div class="message-icon"><i class="fas fa-lightbulb"></i></div>' : ''}
            <div class="message-bubble">${content}</div>
            ${role === 'user' ? '<div class="message-icon"><i class="fas fa-user"></i></div>' : ''}
        `;
        elements.messagesContainer.appendChild(messageDiv);
        elements.messagesContainer.scrollTop = elements.messagesContainer.scrollHeight;
        
        if (saveToHistory && state.selectedGoalId) {
            if (!state.chatHistory[state.selectedGoalId]) {
                state.chatHistory[state.selectedGoalId] = [];
            }
            state.chatHistory[state.selectedGoalId].push({
                role: role,
                content: content,
                timestamp: new Date().toISOString()
            });
            
            saveChatHistoryToStorage();
            
            updateClearButtonVisibility();
        }
        
        return messageDiv; 
    }

    function restoreChatHistory(goalId) {
        elements.messagesContainer.innerHTML = '';
        
        if (state.chatHistory[goalId] && state.chatHistory[goalId].length > 0) {
            state.chatHistory[goalId].forEach(message => {
                addMessage(message.role, message.content, false); 
            });
        } else {
            const goal = state.goals.find(g => g.id === goalId);
            if (goal) {
                showGoalDetails(goal).catch(error => {
                    console.error('Error showing goal details:', error);
                });
            }
        }
    }

    // --- UI & EVENT HANDLERS ---
    function selectGoal(goalId) {
        state.selectedGoalId = goalId;
        renderGoals(); // Re-render to update the 'selected' class
        
        restoreChatHistory(goalId);
        
        updateClearButtonVisibility();
    }

    async function handleSendMessage() {
        const userInput = elements.inputField.value.trim();
        if (!userInput) return;

        addMessage('user', escapeHtml(userInput));
        elements.inputField.value = '';
        elements.sendBtn.disabled = true;

        const loadingMessage = addMessage('assistant', '<div class="loading-dots"><span></span><span></span><span></span> Procesando...</div>', false);

        try {
            let response;
            if (state.selectedGoalId) {
                const goal = state.goals.find(g => g.id === state.selectedGoalId);
                
                const specialResponse = handleSpecialCommands(userInput, goal);
                if (specialResponse) {
                    response = await specialResponse;
                } else {
                    response = await getAIResponse(userInput, goal);
                }
            } else {
                response = await getAIResponse(userInput, null);
            }
            
            loadingMessage.remove();
            addMessage('assistant', response);
        } catch (error) {
            console.error('Error getting AI response:', error);
            loadingMessage.remove();
            addMessage('assistant', 'Lo siento, no pude procesar tu consulta en este momento. Por favor, inténtalo de nuevo.', true); 
        } finally {
            elements.sendBtn.disabled = false;
            elements.inputField.focus();
        }
    }

    async function showGoalDetails(goal) {
        const remaining = goal.target - goal.current;
        const progress = (goal.current / goal.target) * 100;
        
        const basicInfo = `
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
        addMessage('assistant', basicInfo, false); 

        try {
            const motivation = await getMotivationalMessage(goal);
            addMessage('assistant', `
                <div style="color: var(--color-text-primary); line-height: 1.6; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 15px; border-radius: 12px; margin-top: 10px;">
                    <strong>💪 Mensaje Motivacional:</strong><br><br>
                    ${motivation}
                </div>
            `, true); 
        } catch (error) {
            console.error('Error getting motivation:', error);
        }
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
        addMessage('assistant', `¡Perfecto! He creado tu nueva meta "${newGoal.title}".`, true); 
    }

    // --- UTILITY FUNCTIONS ---
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    function handleSpecialCommands(userInput, goal) {
        const input = userInput.toLowerCase();
        
        if (input.includes('dividir') || input.includes('subtareas') || input.includes('pasos')) {
            return getTaskSubtasks(goal.title);
        } else if (input.includes('motivación') || input.includes('motivar') || input.includes('ánimo')) {
            return getMotivationalMessage(goal);
        } else if (input.includes('limpiar') || input.includes('borrar') || input.includes('clear')) {
            clearChatHistory(goal.id);
            return '✅ Chat history cleared for this goal.';
        } else if (input.includes('limpiar todo') || input.includes('borrar todo') || input.includes('clear all')) {
            clearChatHistory();
            return '✅ All chat history cleared.';
        } else if (input.includes('reiniciar') || input.includes('reset') || input.includes('restart')) {
            resetInitialization();
            return '✅ Initialization state reset. You can now reinitialize if needed.';
        }
        
        return null; 
    }

    function clearChatHistory(goalId = null) {
        if (goalId) {
            delete state.chatHistory[goalId];
            if (state.selectedGoalId === goalId) {
                const goal = state.goals.find(g => g.id === goalId);
                if (goal) {
                    elements.messagesContainer.innerHTML = '';
                    showGoalDetails(goal).catch(error => {
                        console.error('Error showing goal details:', error);
                    });
                }
            }
        } else {
            state.chatHistory = {};
            elements.messagesContainer.innerHTML = '';
            const goal = state.goals.find(g => g.id === state.selectedGoalId);
            if (goal) {
                showGoalDetails(goal).catch(error => {
                    console.error('Error showing goal details:', error);
                });
            }
        }
        renderGoals(); 
        updateClearButtonVisibility(); 
        saveChatHistoryToStorage(); 
    }

    function updateClearButtonVisibility() {
        const clearBtn = document.getElementById('clearChatBtn');
        const hasCurrentChat = state.selectedGoalId && state.chatHistory[state.selectedGoalId] && state.chatHistory[state.selectedGoalId].length > 0;
        const hasAnyChat = Object.keys(state.chatHistory).length > 0;
        
        if (hasCurrentChat || hasAnyChat) {
            clearBtn.style.display = 'block';
        } else {
            clearBtn.style.display = 'none';
        }
    }

    function saveChatHistoryToStorage() {
        try {
            localStorage.setItem('financialAssistant_chatHistory', JSON.stringify(state.chatHistory));
        } catch (error) {
            console.error('Error saving chat history to localStorage:', error);
        }
    }

    function loadChatHistoryFromStorage() {
        try {
            const saved = localStorage.getItem('financialAssistant_chatHistory');
            if (saved) {
                state.chatHistory = JSON.parse(saved);
            }
        } catch (error) {
            console.error('Error loading chat history from localStorage:', error);
            state.chatHistory = {};
        }
    }

    function resetInitialization() {
        state.initialized = false;
        console.log('Initialization state reset');
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
        `, true); 
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

        // Clear chat button
        document.getElementById('clearChatBtn').addEventListener('click', () => {
            if (state.selectedGoalId) {
                if (confirm('¿Estás seguro de que quieres limpiar el historial de chat para esta meta?')) {
                    clearChatHistory(state.selectedGoalId);
                }
            } else {
                if (confirm('¿Estás seguro de que quieres limpiar todo el historial de chat?')) {
                    clearChatHistory();
                }
            }
        });
    }

    async function initialize() {
        if (state.initialized) {
            console.log('Financial Assistant already initialized, skipping...');
            return;
        }
        
        console.log('Initializing Financial Assistant...');
        elements.openBtn.classList.add('show');
        
        loadChatHistoryFromStorage();
        
        try {
            console.log('Loading financial data...');
            const data = await loadFinancialData();
            state.goals = generateGoals(data);
            console.log('Goals generated:', state.goals.length);

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

            console.log('Binding event listeners...');
            bindEventListeners();
            
            console.log('Selecting first goal...');
            selectGoal(1); // Select the first goal by default
            
            updateClearButtonVisibility();
            
            state.initialized = true;
            
            console.log('Initialization complete!');

        } catch (error) {
            console.error('Initialization Error:', error);
            addMessage('assistant', 'Error al cargar los datos. Por favor, inténtalo más tarde.', false);
            state.initialized = false;
        }
    }

    initialize();
});
