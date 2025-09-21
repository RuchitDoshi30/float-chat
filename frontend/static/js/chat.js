// 🌊 OceanChat - JavaScript Functionality

class OceanChat {
    constructor() {
        this.initializeEventListeners();
        this.messageId = 0;
        this.isTyping = false;
    }

    initializeEventListeners() {
        // Chat input events
        document.getElementById('chatInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // Quick action buttons
        document.querySelectorAll('.quick-action-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const action = e.currentTarget.dataset.action;
                this.handleQuickAction(action);
            });
        });

        // Navigation buttons
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.switchPage(e.currentTarget.dataset.page);
            });
        });
    }

    async sendMessage() {
        const input = document.getElementById('chatInput');
        const message = input.value.trim();
        
        if (!message || this.isTyping) return;

        // Clear input and disable send button
        input.value = '';
        this.toggleSendButton(false);
        
        // Add user message
        this.addMessage('user', message);
        
        // Show typing indicator
        this.showTypingIndicator();
        
        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: message })
            });

            const data = await response.json();
            
            // Hide typing indicator
            this.hideTypingIndicator();
            
            if (data.error) {
                this.addMessage('assistant', `❌ Error: ${data.error}`, null, data.timestamp);
            } else {
                // Add assistant response with charts and stats
                this.addMessage('assistant', data.response, {
                    charts: data.charts,
                    stats: data.stats
                }, data.timestamp);
            }
            
        } catch (error) {
            this.hideTypingIndicator();
            this.addMessage('assistant', `❌ Connection error: ${error.message}`, null, new Date().toLocaleTimeString());
        }
        
        // Re-enable send button
        this.toggleSendButton(true);
    }

    async handleQuickAction(action) {
        if (this.isTyping) return;

        // Show loading for the clicked button
        const button = document.querySelector(`[data-action="${action}"]`);
        const originalContent = button.innerHTML;
        button.innerHTML = '<i class="fas fa-spinner fa-spin"></i><span>Processing...</span>';
        button.disabled = true;

        // Add action message
        const actionMessages = {
            'temperature': '🌡️ Analyzing temperature data...',
            'map': '🗺️ Generating interactive map...',
            'metrics': '📊 Calculating data metrics...',
            'dashboard': '📈 Building full dashboard...',
            'salinity': '🧂 Analyzing salinity patterns...',
            'charts': '📋 Creating advanced charts...',
            'global': '🌍 Analyzing global patterns...',
            'status': '⚡ Checking system status...'
        };

        this.addMessage('user', actionMessages[action] || 'Processing request...');
        this.showTypingIndicator();

        try {
            const response = await fetch('/api/quick-action', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ action: action })
            });

            const data = await response.json();
            
            this.hideTypingIndicator();
            
            if (data.error) {
                this.addMessage('assistant', `❌ Error: ${data.error}`, null, data.timestamp);
            } else {
                this.addMessage('assistant', data.response, {
                    charts: data.charts,
                    stats: data.stats
                }, data.timestamp);
            }
            
        } catch (error) {
            this.hideTypingIndicator();
            this.addMessage('assistant', `❌ Connection error: ${error.message}`, null, new Date().toLocaleTimeString());
        }

        // Hide button after use instead of restoring it
        button.style.display = 'none';
    }

    addMessage(role, content, extras = null, timestamp = null) {
        this.messageId++;
        const messagesContainer = document.getElementById('chatMessages');
        
        const messageElement = document.createElement('div');
        messageElement.className = `message ${role}-message`;
        messageElement.setAttribute('data-message-id', this.messageId);

        const avatar = role === 'user' ? '👤' : '🌊';
        const senderName = role === 'user' ? 'You' : 'OceanChat Assistant';
        const messageTime = timestamp || new Date().toLocaleTimeString();

        let messageHTML = `
            <div class="message-avatar">${avatar}</div>
            <div class="message-content">
                <div class="message-header">
                    <span class="sender-name">${senderName}</span>
                    <span class="message-time">${messageTime}</span>
                </div>
                <div class="message-text">${content}</div>
        `;

        // Add stats if available
        if (extras && extras.stats) {
            messageHTML += this.createStatsHTML(extras.stats);
        }

        // Add charts if available
        if (extras && extras.charts) {
            messageHTML += this.createChartsHTML(extras.charts);
        }

        messageHTML += `
            </div>
        `;

        messageElement.innerHTML = messageHTML;
        messagesContainer.appendChild(messageElement);

        // Render charts after DOM insertion
        if (extras && extras.charts) {
            setTimeout(() => {
                this.renderCharts(extras.charts, this.messageId);
            }, 100);
        }

        // Scroll to bottom
        this.scrollToBottom();
    }

    createStatsHTML(stats) {
        if (!stats) return '';

        return `
            <div class="message-stats">
                <div class="stat-item">
                    <div class="stat-value">${stats.avg_temperature || 'N/A'}</div>
                    <div class="stat-label">Avg Temperature</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">${stats.avg_salinity || 'N/A'}</div>
                    <div class="stat-label">Avg Salinity</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">${stats.max_depth || 'N/A'}</div>
                    <div class="stat-label">Max Depth</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">${stats.data_points || 0}</div>
                    <div class="stat-label">Data Points</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">${stats.platforms || 0}</div>
                    <div class="stat-label">Platforms</div>
                </div>
            </div>
        `;
    }

    createChartsHTML(charts) {
        if (!charts || charts.length === 0) return '';

        let chartsHTML = '';
        charts.forEach((chart, index) => {
            chartsHTML += `
                <div class="chart-container">
                    <div class="chart-title">${chart.title}</div>
                    <div id="chart-${this.messageId}-${index}" style="width: 100%; height: 400px;"></div>
                </div>
            `;
        });

        return chartsHTML;
    }

    renderCharts(charts, messageId) {
        charts.forEach((chart, index) => {
            const chartElement = document.getElementById(`chart-${messageId}-${index}`);
            if (chartElement && chart.data) {
                try {
                    const plotData = JSON.parse(chart.data);
                    Plotly.newPlot(chartElement, plotData.data, plotData.layout, {
                        responsive: true,
                        displayModeBar: true,
                        modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d'],
                        displaylogo: false
                    });
                } catch (error) {
                    console.error('Error rendering chart:', error);
                    chartElement.innerHTML = '<p style="color: #f56565; text-align: center; padding: 2rem;">Error loading chart</p>';
                }
            }
        });
    }

    showTypingIndicator() {
        this.isTyping = true;
        const indicator = document.getElementById('typingIndicator');
        indicator.style.display = 'flex';
        this.scrollToBottom();
    }

    hideTypingIndicator() {
        this.isTyping = false;
        const indicator = document.getElementById('typingIndicator');
        indicator.style.display = 'none';
    }

    toggleSendButton(enabled) {
        const sendButton = document.getElementById('sendButton');
        sendButton.disabled = !enabled;
        
        if (enabled) {
            sendButton.innerHTML = '<i class="fas fa-paper-plane"></i>';
        } else {
            sendButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
        }
    }

    scrollToBottom() {
        const messagesContainer = document.getElementById('chatMessages');
        setTimeout(() => {
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }, 100);
    }

    switchPage(page) {
        // Update active nav button
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-page="${page}"]`).classList.add('active');

        // For now, just show different content based on page
        // In a real app, you would load different components
        console.log(`Switching to page: ${page}`);
    }

    async refreshStatus() {
        try {
            const response = await fetch('/api/system-status');
            const status = await response.json();
            
            // Update status display
            document.getElementById('backend-status').textContent = status.backend_status;
            document.getElementById('response-time').textContent = status.api_response_time;
            document.getElementById('data-sources').textContent = status.data_sources;
            
            // Show success message
            this.addMessage('assistant', '✅ System status refreshed successfully!', { stats: status }, new Date().toLocaleTimeString());
            
        } catch (error) {
            this.addMessage('assistant', `❌ Failed to refresh status: ${error.message}`, null, new Date().toLocaleTimeString());
        }
    }

    clearChat() {
        const messagesContainer = document.getElementById('chatMessages');
        
        // Keep only the welcome message
        const welcomeMessage = messagesContainer.querySelector('.welcome-message').parentElement;
        messagesContainer.innerHTML = '';
        messagesContainer.appendChild(welcomeMessage);
        
        this.messageId = 0;
        
        // Add confirmation message
        setTimeout(() => {
            this.addMessage('assistant', '🧹 Chat cleared! How can I help you today?', null, new Date().toLocaleTimeString());
        }, 500);
    }

    showLoading() {
        document.getElementById('loadingOverlay').style.display = 'flex';
    }

    hideLoading() {
        document.getElementById('loadingOverlay').style.display = 'none';
    }
}

// Global functions for HTML onclick events
function sendMessage() {
    window.oceanChat.sendMessage();
}

function clearChat() {
    if (confirm('Are you sure you want to clear the chat?')) {
        window.oceanChat.clearChat();
    }
}

function refreshStatus() {
    window.oceanChat.refreshStatus();
}

// Profile switching functions
function showProfileSelector() {
    document.getElementById('profileSelector').style.display = 'block';
}

function hideProfileSelector() {
    document.getElementById('profileSelector').style.display = 'none';
}

async function switchProfile(profileId) {
    try {
        const response = await fetch('/api/profiles/switch', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ profile: profileId })
        });

        const data = await response.json();
        
        if (data.success) {
            // Update UI immediately
            const profileInfo = data.profile_info;
            
            // Update profile display
            document.querySelector('.profile-icon').textContent = profileInfo.icon;
            document.querySelector('.profile-name').textContent = profileInfo.name;
            document.querySelector('.profile-desc').textContent = profileInfo.description;
            
            // Update active selection
            document.querySelectorAll('.profile-option').forEach(option => {
                option.classList.remove('active');
            });
            document.querySelector(`[onclick="switchProfile('${profileId}')"]`).classList.add('active');
            
            // Add chat message about profile switch
            window.oceanChat.addMessage('assistant', 
                `🔄 Profile switched to ${profileInfo.name}! Your interface is now optimized for ${profileInfo.description.toLowerCase()}.`, 
                null, 
                new Date().toLocaleTimeString()
            );
            
            // Hide selector
            hideProfileSelector();
            
        } else {
            console.error('Profile switch failed:', data.error);
            window.oceanChat.addMessage('assistant', 
                `❌ Failed to switch profile: ${data.error}`, 
                null, 
                new Date().toLocaleTimeString()
            );
        }
        
    } catch (error) {
        console.error('Profile switch error:', error);
        window.oceanChat.addMessage('assistant', 
            `❌ Connection error while switching profile: ${error.message}`, 
            null, 
            new Date().toLocaleTimeString()
        );
    }
}

// Initialize the chat application
document.addEventListener('DOMContentLoaded', function() {
    window.oceanChat = new OceanChat();
    console.log('🌊 OceanChat initialized successfully!');
    
    // Auto-focus on chat input
    document.getElementById('chatInput').focus();
});