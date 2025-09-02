// Modern Chat WebSocket Client
class ChatClient {
    constructor(websocketUrl, businessId, sessionId) {
        this.websocketUrl = websocketUrl;
        this.businessId = businessId;
        this.sessionId = sessionId;
        this.socket = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectInterval = 3000;
        this.isTyping = false;
        
        this.initializeElements();
        this.connect();
        this.setupEventListeners();
    }
    
    initializeElements() {
        this.messagesContainer = document.getElementById('chat-messages');
        this.messageInput = document.getElementById('message-input');
        this.sendButton = document.getElementById('send-button');
        this.connectionStatus = document.getElementById('connection-status');
    }
    
    connect() {
        try {
            this.socket = new WebSocket(this.websocketUrl);
            this.setupSocketEventListeners();
        } catch (error) {
            console.error('WebSocket connection failed:', error);
            this.handleConnectionError();
        }
    }
    
    setupSocketEventListeners() {
        this.socket.onopen = () => {
            console.log('WebSocket connected');
            this.updateConnectionStatus('Connected', true);
            this.reconnectAttempts = 0;
            this.enableInput();
            this.addWelcomeMessage();
        };
        
        this.socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleMessage(data);
        };
        
        this.socket.onclose = (event) => {
            console.log('WebSocket disconnected:', event.code, event.reason);
            this.updateConnectionStatus('Disconnected', false);
            this.disableInput();
            this.attemptReconnect();
        };
        
        this.socket.onerror = (error) => {
            console.error('WebSocket error:', error);
            this.handleConnectionError();
        };
    }
    
    setupEventListeners() {
        this.sendButton.addEventListener('click', () => {
            this.sendMessage();
        });
        
        this.messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        this.messageInput.addEventListener('input', () => {
            this.updateSendButtonState();
        });
        
        // Add typing indicator
        this.messageInput.addEventListener('focus', () => {
            this.messageInput.parentElement.classList.add('focused');
        });
        
        this.messageInput.addEventListener('blur', () => {
            this.messageInput.parentElement.classList.remove('focused');
        });
    }
    
    updateSendButtonState() {
        const hasText = this.messageInput.value.trim().length > 0;
        this.sendButton.classList.toggle('active', hasText);
    }
    
    sendMessage() {
        const message = this.messageInput.value.trim();
        if (!message || !this.socket || this.socket.readyState !== WebSocket.OPEN) {
            return;
        }
        
        const data = {
            message: message,
            type: 'user'
        };
        
        this.socket.send(JSON.stringify(data));
        this.messageInput.value = '';
        this.updateSendButtonState();
        this.disableInput();
    }
    
    handleMessage(data) {
        if (data.error) {
            this.displayMessage(data.error, 'system');
        } else {
            this.displayMessage(data.message, data.sender);
        }
        
        this.enableInput();
    }
    
    displayMessage(message, sender) {
        const messageElement = document.createElement('div');
        messageElement.className = `message ${sender}`;
        
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        
        // Add sender icon
        const senderIcon = document.createElement('i');
        if (sender === 'user') {
            senderIcon.className = 'fas fa-user';
        } else if (sender === 'assistant') {
            senderIcon.className = 'fas fa-robot';
        } else {
            senderIcon.className = 'fas fa-info-circle';
        }
        
        const messageText = document.createElement('span');
        messageText.textContent = message;
        
        messageContent.appendChild(senderIcon);
        messageContent.appendChild(messageText);
        messageElement.appendChild(messageContent);
        
        const messageTime = document.createElement('div');
        messageTime.className = 'message-time';
        messageTime.textContent = new Date().toLocaleTimeString([], { 
            hour: '2-digit', 
            minute: '2-digit' 
        });
        messageElement.appendChild(messageTime);
        
        this.messagesContainer.appendChild(messageElement);
        this.scrollToBottom();
    }
    
    addWelcomeMessage() {
        const welcomeMessage = "Hello! I'm here to help you with any questions about " + 
                             document.querySelector('.chat-header h2').textContent.replace('💬 ', '') + 
                             ". How can I assist you today?";
        this.displayMessage(welcomeMessage, 'assistant');
    }
    
    scrollToBottom() {
        this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
    }
    
    updateConnectionStatus(status, connected) {
        const icon = this.connectionStatus.querySelector('i');
        const text = this.connectionStatus.querySelector('span') || document.createElement('span');
        
        if (connected) {
            icon.className = 'fas fa-circle';
            icon.style.color = '#48bb78';
        } else {
            icon.className = 'fas fa-circle';
            icon.style.color = '#e53e3e';
        }
        
        text.textContent = status;
        if (!this.connectionStatus.querySelector('span')) {
            this.connectionStatus.appendChild(text);
        }
        
        this.connectionStatus.className = connected ? 'status connected' : 'status';
    }
    
    enableInput() {
        this.messageInput.disabled = false;
        this.sendButton.disabled = false;
        this.messageInput.focus();
        this.updateSendButtonState();
    }
    
    disableInput() {
        this.messageInput.disabled = true;
        this.sendButton.disabled = true;
        this.sendButton.classList.remove('active');
    }
    
    handleConnectionError() {
        this.updateConnectionStatus('Error', false);
        this.disableInput();
        this.attemptReconnect();
    }
    
    attemptReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            this.updateConnectionStatus(`Reconnecting (${this.reconnectAttempts}/${this.maxReconnectAttempts})`, false);
            
            setTimeout(() => {
                this.connect();
            }, this.reconnectInterval);
        } else {
            this.updateConnectionStatus('Connection Failed', false);
            this.displayMessage('Connection lost. Please refresh the page to reconnect.', 'system');
        }
    }
}

// Initialize chat client when page loads
document.addEventListener('DOMContentLoaded', () => {
    new ChatClient(websocketUrl, businessId, sessionId);
});