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
        aiSuggestBtn: document.getElementById('aiSuggestBtn'),
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

        const subgoalsCount = goal.subgoals ? goal.subgoals.length : 0;
        const subgoalsIndicator = subgoalsCount > 0 ? ` <span class="subgoals-indicator" title="${subgoalsCount} submetas">📋 ${subgoalsCount}</span>` : '';
        
        return `
            <div class="goal-card ${isCompleted ? 'completed' : ''} ${goal.id === state.selectedGoalId ? 'selected' : ''}" data-goal-id="${goal.id}">
                <div class="goal-title">${priorityIcon} ${goal.title} ${isCompleted ? ' <span style="color: #48bb78; font-size: 10px;">✓</span>' : ''}${chatIndicator}${subgoalsIndicator}</div>
                <div class="goal-progress"><div class="goal-progress-bar" style="width: ${progress}%"></div></div>
                <div class="goal-percent">${progress.toFixed(0)}% · ${goal.current.toFixed(0)}€ / ${goal.target.toFixed(0)}€</div>
                <div class="goal-actions">
                    <button class="add-subgoal-btn" data-goal-id="${goal.id}" title="Agregar submeta">
                        <i class="fas fa-plus"></i> Submeta
                    </button>
                </div>
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
            priority: priority.value,
            parentId: null, 
            subgoals: [] 
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
        } else if (input.includes('crear meta') || input.includes('nueva meta') || input.includes('sugerir')) {
            try {
                showAISuggestionsModal();
                return '🤖 Abriendo el generador de sugerencias de AI...';
            } catch (error) {
                console.error('Error opening AI suggestions modal:', error);
                return '❌ Error al abrir el generador de sugerencias. Por favor, inténtalo de nuevo.';
            }
        } else if (input.includes('submeta') || input.includes('sub meta')) {
            if (state.selectedGoalId) {
                addSubgoal(state.selectedGoalId);
                return '📋 Abriendo el creador de submetas...';
            } else {
                return '❌ Por favor, selecciona una meta primero para agregar una submeta.';
            }
        }
        
        return null; 
    }

    async function getAITaskSuggestions(userDescription) {
        try {
            const financialSituation = state.metrics ? {
                income: state.metrics.analysis.total_income,
                expenses: state.metrics.analysis.total_expenses,
                balance: state.metrics.analysis.balance
            } : null;

            const requestData = {
                description: userDescription,
                financial_situation: financialSituation
            };

            const response = await fetch('/api/ai/suggest-tasks', {
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
                return result.data.suggestions;
            } else {
                throw new Error(result.error || 'Error desconocido');
            }
        } catch (error) {
            console.error('Error getting AI task suggestions:', error);
            return `Basándome en tu descripción "${userDescription}", te sugiero crear metas específicas como: ahorro de emergencia, reducción de gastos, o inversión a largo plazo.`;
        }
    }

    async function createSmartGoal(goalType, context) {
        try {
            const financialData = state.metrics ? {
                income: state.metrics.analysis.total_income,
                expenses: state.metrics.analysis.total_expenses,
                balance: state.metrics.analysis.balance
            } : null;

            const requestData = {
                goal_type: goalType,
                context: context,
                financial_data: financialData
            };

            const response = await fetch('/api/ai/create-smart-goal', {
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
                return result.data.goal;
            } else {
                throw new Error(result.error || 'Error desconocido');
            }
        } catch (error) {
            console.error('Error creating smart goal:', error);
            return {
                title: `Meta de ${goalType}`,
                description: `Meta personalizada para ${goalType}`,
                target: 1000,
                deadline: "6 meses",
                priority: "medium",
                strategy: "Define tu estrategia personalizada."
            };
        }
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

    function showAISuggestionsModal() {
        console.log('Opening AI suggestions modal...');
        
        const existingModal = document.getElementById('aiSuggestionsModal');
        if (existingModal) {
            existingModal.remove();
        }
        
        const modal = document.createElement('div');
        modal.className = 'ai-suggestions-modal';
        modal.id = 'aiSuggestionsModal';
        
        modal.innerHTML = `
            <div class="ai-suggestions-content">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                    <h3 style="margin: 0; color: #2d3748;">🤖 Sugerencias de AI</h3>
                    <button class="close-modal-btn" id="closeAISuggestionsModalBtn">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <div style="margin-bottom: 20px;">
                    <label for="suggestionInput" style="display: block; margin-bottom: 8px; font-weight: 600; color: #4a5568;">
                        Describe lo que quieres lograr:
                    </label>
                    <textarea id="suggestionInput" placeholder="Ej: Quiero ahorrar para un viaje, reducir mis gastos mensuales, o invertir para mi jubilación..." 
                              style="width: 100%; padding: 12px; border: 1px solid #e2e8f0; border-radius: 8px; font-size: 14px; resize: vertical; min-height: 80px;"></textarea>
                </div>
                <div style="display: flex; gap: 12px; justify-content: flex-end;">
                    <button class="cancel-btn" id="cancelAISuggestionsBtn">Cancelar</button>
                    <button class="create-btn" id="generateSuggestionsBtn">
                        <i class="fas fa-magic"></i> Generar Sugerencias
                    </button>
                </div>
                <div id="suggestionsContainer" style="margin-top: 20px;"></div>
            </div>
        `;
        
        document.body.appendChild(modal);
        console.log('AI suggestions modal added to DOM');
        
        const closeBtn = document.getElementById('closeAISuggestionsModalBtn');
        const cancelBtn = document.getElementById('cancelAISuggestionsBtn');
        const generateBtn = document.getElementById('generateSuggestionsBtn');
        
        if (closeBtn) {
            closeBtn.addEventListener('click', closeAISuggestionsModal);
            console.log('Close button event listener added');
        }
        if (cancelBtn) {
            cancelBtn.addEventListener('click', closeAISuggestionsModal);
            console.log('Cancel button event listener added');
        }
        if (generateBtn) {
            generateBtn.addEventListener('click', generateSuggestions);
            console.log('Generate button event listener added');
        }
        
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                closeAISuggestionsModal();
            }
        });
        
        setTimeout(() => {
            const input = document.getElementById('suggestionInput');
            if (input) {
                input.focus();
                console.log('Input field focused');
            } else {
                console.warn('Input field not found');
            }
        }, 100);
    }

    function closeAISuggestionsModal() {
        console.log('Closing AI suggestions modal...');
        const modal = document.getElementById('aiSuggestionsModal');
        if (modal) {
            const closeBtn = document.getElementById('closeAISuggestionsModalBtn');
            const cancelBtn = document.getElementById('cancelAISuggestionsBtn');
            const generateBtn = document.getElementById('generateSuggestionsBtn');
            
            if (closeBtn) closeBtn.removeEventListener('click', closeAISuggestionsModal);
            if (cancelBtn) cancelBtn.removeEventListener('click', closeAISuggestionsModal);
            if (generateBtn) generateBtn.removeEventListener('click', generateSuggestions);
            
            modal.remove();
            console.log('AI suggestions modal removed from DOM');
        } else {
            console.warn('AI suggestions modal not found');
        }
    }

    async function generateSuggestions() {
        console.log('Generating AI suggestions...');
        const input = document.getElementById('suggestionInput');
        const container = document.getElementById('suggestionsContainer');
        const btn = document.getElementById('generateSuggestionsBtn');
        
        if (!input || !input.value.trim()) {
            alert('Por favor, describe lo que quieres lograr.');
            return;
        }
        
        btn.disabled = true;
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generando...';
        
        try {
            console.log('Getting AI task suggestions for:', input.value.trim());
            const suggestions = await getAITaskSuggestions(input.value.trim());
            console.log('AI suggestions received:', suggestions);
            
            container.innerHTML = `
                <div style="margin-bottom: 16px;">
                    <h4 style="color: #2d3748; margin-bottom: 12px;">💡 Sugerencias de AI:</h4>
                    <div style="background: #f7fafc; padding: 16px; border-radius: 8px; border-left: 4px solid #667eea;">
                        <div style="white-space: pre-wrap; line-height: 1.6; color: #4a5568;">${suggestions}</div>
                    </div>
                </div>
                <div style="margin-bottom: 16px;">
                    <h4 style="color: #2d3748; margin-bottom: 12px;">🚀 Crear Meta Inteligente:</h4>
                    <div style="display: flex; gap: 8px; margin-bottom: 12px;">
                        <input type="text" id="smartGoalTitle" placeholder="Título de la meta" 
                               style="flex: 1; padding: 8px; border: 1px solid #e2e8f0; border-radius: 6px; font-size: 14px;">
                        <input type="number" id="smartGoalTarget" placeholder="Meta (€)" 
                               style="width: 120px; padding: 8px; border: 1px solid #e2e8f0; border-radius: 6px; font-size: 14px;">
                    </div>
                    <div style="display: flex; gap: 8px; margin-bottom: 12px;">
                        <select id="smartGoalDeadline" style="flex: 1; padding: 8px; border: 1px solid #e2e8f0; border-radius: 6px; font-size: 14px;">
                            <option value="1 mes">1 mes</option>
                            <option value="3 meses">3 meses</option>
                            <option value="6 meses" selected>6 meses</option>
                            <option value="1 año">1 año</option>
                            <option value="2 años">2 años</option>
                        </select>
                        <select id="smartGoalPriority" style="flex: 1; padding: 8px; border: 1px solid #e2e8f0; border-radius: 6px; font-size: 14px;">
                            <option value="low">Baja</option>
                            <option value="medium" selected>Media</option>
                            <option value="high">Alta</option>
                        </select>
                    </div>
                    <textarea id="smartGoalDescription" placeholder="Descripción de la meta" 
                              style="width: 100%; padding: 8px; border: 1px solid #e2e8f0; border-radius: 6px; font-size: 14px; resize: vertical; min-height: 60px;"></textarea>
                </div>
                <div style="display: flex; gap: 12px; justify-content: flex-end;">
                    <button class="cancel-btn" id="closeAISuggestionsBtn">Cerrar</button>
                    <button class="create-btn" id="createSmartGoalBtn">
                        <i class="fas fa-plus"></i> Crear Meta
                    </button>
                </div>
            `;
            
            document.getElementById('closeAISuggestionsBtn').addEventListener('click', closeAISuggestionsModal);
            document.getElementById('createSmartGoalBtn').addEventListener('click', createSmartGoalFromSuggestion);
            
        } catch (error) {
            console.error('Error generating suggestions:', error);
            container.innerHTML = `
                <div style="color: #e53e3e; padding: 16px; background: #fed7d7; border-radius: 8px; margin-bottom: 16px;">
                    Error al generar sugerencias. Por favor, inténtalo de nuevo.
                </div>
            `;
        } finally {
            btn.disabled = false;
            btn.innerHTML = '<i class="fas fa-magic"></i> Generar Sugerencias';
        }
    }

    function createSmartGoalFromSuggestion() {
        console.log('Creating smart goal from suggestion...');
        
        const title = document.getElementById('smartGoalTitle').value.trim();
        const target = parseFloat(document.getElementById('smartGoalTarget').value) || 0;
        const deadline = document.getElementById('smartGoalDeadline').value;
        const priority = document.getElementById('smartGoalPriority').value;
        const description = document.getElementById('smartGoalDescription').value.trim();
        
        if (!title) {
            alert('Por favor, ingresa un título para la meta.');
            return;
        }
        
        if (target <= 0) {
            alert('Por favor, ingresa una meta monetaria válida.');
            return;
        }
        
        const newGoal = {
            id: Date.now(),
            title: title,
            description: description || `Meta creada con AI: ${title}`,
            target: target,
            current: 0,
            deadline: deadline,
            priority: priority,
            strategy: 'Estrategia personalizada basada en sugerencias de AI.',
            parentId: null, 
            subgoals: [] 
        };
        
        state.goals.push(newGoal);
        
        closeAISuggestionsModal();
        
        selectGoal(newGoal.id);
        
        addMessage('assistant', `¡Perfecto! He creado tu nueva meta "${title}" con una meta de ${target}€ para ${deadline}. ¡Ahora puedes empezar a trabajar en ella!`, true);
        
        renderGoals();
    }

    function addSubgoal(parentGoalId) {
        console.log('Adding subgoal for parent:', parentGoalId);
        
        const parentGoal = state.goals.find(g => g.id === parentGoalId);
        if (!parentGoal) {
            console.error('Parent goal not found:', parentGoalId);
            alert('Error: No se encontró la meta padre.');
            return;
        }
        
        const existingModal = document.getElementById('subgoalModal');
        if (existingModal) {
            existingModal.remove();
        }
        
        const modal = document.createElement('div');
        modal.className = 'subgoal-modal';
        modal.id = 'subgoalModal';
        
        modal.innerHTML = `
            <div class="subgoal-content">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                    <h3 style="margin: 0; color: #2d3748;">📋 Agregar Submeta</h3>
                    <button class="close-modal-btn" id="closeSubgoalModalBtn">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <form class="subgoal-form" id="subgoalForm">
                    <div class="subgoal-form-group">
                        <label for="subgoalTitle">Título de la submeta</label>
                        <input type="text" id="subgoalTitle" placeholder="Ej: Ahorrar para el vuelo" required>
                    </div>
                    <div class="subgoal-form-row">
                        <div class="subgoal-form-group">
                            <label for="subgoalTarget">Meta (€)</label>
                            <input type="number" id="subgoalTarget" placeholder="500" min="0" step="0.01" required>
                        </div>
                        <div class="subgoal-form-group">
                            <label for="subgoalDeadline">Plazo</label>
                            <select id="subgoalDeadline" required>
                                <option value="1 mes">1 mes</option>
                                <option value="2 meses">2 meses</option>
                                <option value="3 meses" selected>3 meses</option>
                                <option value="6 meses">6 meses</option>
                            </select>
                        </div>
                    </div>
                    <div class="subgoal-form-group">
                        <label for="subgoalDescription">Descripción</label>
                        <textarea id="subgoalDescription" placeholder="Describe esta submeta..." rows="3"></textarea>
                    </div>
                    <div style="display: flex; gap: 12px; justify-content: flex-end; margin-top: 20px;">
                        <button type="button" class="cancel-btn" id="cancelSubgoalBtn">Cancelar</button>
                        <button type="submit" class="create-btn">
                            <i class="fas fa-plus"></i> Crear Submeta
                        </button>
                    </div>
                </form>
            </div>
        `;
        
        document.body.appendChild(modal);
        console.log('Subgoal modal added to DOM');
        
        const closeBtn = document.getElementById('closeSubgoalModalBtn');
        const cancelBtn = document.getElementById('cancelSubgoalBtn');
        const form = document.getElementById('subgoalForm');
        
        if (closeBtn) {
            closeBtn.addEventListener('click', closeSubgoalModal);
            console.log('Close button event listener added');
        }
        if (cancelBtn) {
            cancelBtn.addEventListener('click', closeSubgoalModal);
            console.log('Cancel button event listener added');
        }
        if (form) {
            form.addEventListener('submit', (e) => {
                e.preventDefault();
                createSubgoal(parentGoalId);
            });
            console.log('Form event listener added');
        }
        
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                closeSubgoalModal();
            }
        });
        
        setTimeout(() => {
            const input = document.getElementById('subgoalTitle');
            if (input) {
                input.focus();
                console.log('Subgoal title input focused');
            } else {
                console.warn('Subgoal title input not found');
            }
        }, 100);
    }

    function closeSubgoalModal() {
        console.log('Closing subgoal modal...');
        const modal = document.getElementById('subgoalModal');
        if (modal) {
            modal.remove();
            console.log('Subgoal modal removed from DOM');
        } else {
            console.warn('Subgoal modal not found');
        }
    }

    function createSubgoal(parentGoalId) {
        console.log('Creating subgoal for parent:', parentGoalId);
        
  
        const titleInput = document.getElementById('subgoalTitle');
        const targetInput = document.getElementById('subgoalTarget');
        const deadlineInput = document.getElementById('subgoalDeadline');
        const descriptionInput = document.getElementById('subgoalDescription');
        
        if (!titleInput || !targetInput || !deadlineInput || !descriptionInput) {
            console.error('Form inputs not found');
            alert('Error: No se encontraron los campos del formulario.');
            return;
        }
        
        const title = titleInput.value.trim();
        const target = parseFloat(targetInput.value) || 0;
        const deadline = deadlineInput.value;
        const description = descriptionInput.value.trim();
        
        if (!title) {
            alert('Por favor, ingresa un título para la submeta.');
            return;
        }
        
        if (target <= 0) {
            alert('Por favor, ingresa una meta monetaria válida.');
            return;
        }
        
        const subgoal = {
            id: Date.now(),
            title: title,
            description: description || `Submeta: ${title}`,
            target: target,
            current: 0,
            deadline: deadline,
            priority: 'medium',
            strategy: 'Estrategia específica para esta submeta.',
            parentId: parentGoalId
        };
        
        const parentGoal = state.goals.find(g => g.id === parentGoalId);
        if (parentGoal) {
            if (!parentGoal.subgoals) {
                parentGoal.subgoals = [];
            }
            parentGoal.subgoals.push(subgoal);
            
            closeSubgoalModal();
            
            renderGoals();
            
            addMessage('assistant', `¡Perfecto! He creado la submeta "${title}" para tu meta "${parentGoal.title}".`, true);
        } else {
            alert('Error: No se encontró la meta padre.');
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

        // AI suggestions button
        if (elements.aiSuggestBtn) {
            elements.aiSuggestBtn.addEventListener('click', showAISuggestionsModal);
            console.log('AI suggest button event listener added');
        } else {
            console.warn('AI suggest button not found');
        }

        elements.goalsList.addEventListener('click', (e) => {
            if (e.target.closest('.add-subgoal-btn')) {
                const button = e.target.closest('.add-subgoal-btn');
                const goalId = parseInt(button.dataset.goalId);
                console.log('Subgoal button clicked for goal:', goalId);
                addSubgoal(goalId);
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
