// Frontend Configuration
export const CONFIG = {
    // API Configuration - dynamically determined
    get API_URL() {
        // Get the current host and port from the browser
        const protocol = window.location.protocol;
        const host = window.location.hostname;
        const port = window.location.port;
        
        // If we're serving from the same host, use the same port
        // Otherwise, default to the API port
        const apiPort = port ? port : '8002';
        
        return `${protocol}//${host}:${apiPort}`;
    },
    
    API_ENDPOINTS: {
        CHAT_STREAM: '/chat/stream',
        CHAT: '/chat'
    },
    
    // UI Configuration
    UI: {
        CHAT_HEIGHT: '400px',
        MAX_MESSAGE_WIDTH: '70%',
        AUTO_SCROLL_DELAY: 100,
        THINKING_SCROLL_DELAY: 10
    },
    
    // Message Configuration
    MESSAGES: {
        DEFAULT_TASK_NAME: 'General Chat',
        WELCOME_MESSAGE: 'Hello! I\'m your Qwen AI assistant. How can I help you today?',
        STREAMING_INFO: '💡 This uses Server-Sent Events (SSE) for real-time streaming!',
        THINKING_PREFIX: '🤔',
        ERROR_PREFIX: 'Error: '
    },
    
    // Status Messages
    STATUS: {
        READY: 'Ready',
        CONNECTING: 'Connecting...',
        CONNECTED: 'Connected - Streaming...',
        THINKING_START: '🤔 Starting to think...',
        CONNECTION_ERROR: 'Connection Error'
    },
    
    // Animation Configuration
    ANIMATION: {
        CURSOR_BLINK_DURATION: 1000,
        CURSOR_BLINK_OPACITY: [1, 0]
    }
};

// Enhanced configuration loader that can fetch from server
export class ConfigLoader {
    static async loadServerConfig() {
        try {
            const response = await fetch('/api/config');
            if (response.ok) {
                const serverConfig = await response.json();
                return {
                    ...CONFIG,
                    API_URL: serverConfig.api_url,
                    SERVER_CONFIG: serverConfig
                };
            }
        } catch (error) {
            console.warn('Could not load server config, using default:', error);
        }
        return CONFIG;
    }
    
    static getApiUrl() {
        return CONFIG.API_URL;
    }
} 