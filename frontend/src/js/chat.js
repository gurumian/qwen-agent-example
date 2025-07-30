import { marked } from 'marked';
import { CONFIG, ConfigLoader } from './config.js';

// Initialize configuration
let currentConfig = CONFIG;

// Initialize the application with server config
async function initializeApp() {
    try {
        currentConfig = await ConfigLoader.loadServerConfig();
        console.log('✅ Loaded server configuration:', currentConfig.SERVER_CONFIG);
    } catch (error) {
        console.warn('⚠️ Using default configuration:', error);
    }
    
    // Initialize chat functionality after config is loaded
    initializeChat();
}

// Chat functionality
function initializeChat() {
    const API_URL = currentConfig.API_URL;
    const chatMessages = document.getElementById('chatMessages');
    const messageInput = document.getElementById('messageInput');
    const sendButton = document.getElementById('sendButton');
    const statusIndicator = document.getElementById('statusIndicator');

    let conversationHistory = [];
    let eventSource = null;
    let currentResponseDiv = null;

    function updateStatus(status, type = 'ready') {
        statusIndicator.textContent = status;
        statusIndicator.className = `status-indicator ${type}`;
        
        // Auto-scroll to bottom ONLY for thinking content
        if (type === 'thinking') {
            // Small delay to ensure content is updated
            setTimeout(() => {
                statusIndicator.scrollTop = statusIndicator.scrollHeight;
            }, currentConfig.UI.THINKING_SCROLL_DELAY);
        }
    }

    function addMessage(content, isUser = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${isUser ? 'user-message' : 'assistant-message'}`;
        
        if (isUser) {
            messageDiv.textContent = content;
        } else {
            // Parse markdown for assistant messages
            messageDiv.innerHTML = marked.parse(content);
        }
        
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        return messageDiv;
    }

    function addErrorMessage(error) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error';
        errorDiv.textContent = currentConfig.MESSAGES.ERROR_PREFIX + error;
        chatMessages.appendChild(errorDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function cleanResponseContent(content) {
        // Remove complete <think> tags and their content
        let cleaned = content.replace(/<think>[\s\S]*?<\/think>/g, '');
        // Also remove partial <think> content (for streaming)
        cleaned = cleaned.replace(/<think>[\s\S]*/g, '');
        return cleaned.trim();
    }

    function extractThinkContent(content) {
        console.log('🔍 Extracting think content from:', content.substring(0, 100) + '...');
        
        // Look for complete think blocks
        const thinkMatch = content.match(/<think>([\s\S]*?)<\/think>/);
        if (thinkMatch) {
            console.log('✅ Found complete think block:', thinkMatch[1].substring(0, 50) + '...');
            return thinkMatch[1].trim();
        }
        
        // Also look for partial think content (for streaming)
        const partialThinkMatch = content.match(/<think>([\s\S]*)/);
        if (partialThinkMatch) {
            console.log('✅ Found partial think block:', partialThinkMatch[1].substring(0, 50) + '...');
            return partialThinkMatch[1].trim();
        }
        
        console.log('❌ No think content found');
        return null;
    }

    async function sendMessage() {
        const message = messageInput.value.trim();
        if (!message) return;

        // Disable input and button
        messageInput.disabled = true;
        sendButton.disabled = true;
        messageInput.value = '';

        // Add user message to chat
        addMessage(message, true);

        // Show thinking status
        updateStatus(currentConfig.STATUS.THINKING_START, 'thinking');

        // Don't create response container yet - wait until we have clean content
        currentResponseDiv = null;

        try {
            // Prepare messages for API
            const messages = [];
            
            // Add conversation history
            for (const msg of conversationHistory) {
                messages.push({ role: msg.role, content: msg.content });
            }
            
            // Add current message
            messages.push({ role: 'user', content: message });

            // Start SSE connection
            await startSSEConnection(messages);

        } catch (error) {
            console.error('Error:', error);
            addErrorMessage(error.message);
            updateStatus(currentConfig.MESSAGES.ERROR_PREFIX + error.message, 'error');
        } finally {
            // Re-enable input and button
            messageInput.disabled = false;
            sendButton.disabled = false;
            messageInput.focus();
        }
    }

    async function startSSEConnection(messages) {
        // Close existing connection
        if (eventSource) {
            eventSource.close();
        }

        updateStatus(currentConfig.STATUS.CONNECTING, 'connecting');

        // Create URL with query parameters for SSE
        const params = new URLSearchParams({
            messages: JSON.stringify(messages),
            task_name: currentConfig.MESSAGES.DEFAULT_TASK_NAME,
            stream: 'true'
        });

        // Create EventSource for SSE
        eventSource = new EventSource(`${API_URL}${currentConfig.API_ENDPOINTS.CHAT_STREAM}?${params}`);

        let fullResponse = '';
        let thinkContent = '';

        eventSource.onopen = function(event) {
            updateStatus(currentConfig.STATUS.CONNECTED, 'ready');
        };

        eventSource.onmessage = function(event) {
            try {
                if (event.data === '[DONE]') {
                    // Streaming complete
                    
                    // Show final clean response
                    const finalCleanContent = cleanResponseContent(fullResponse);
                    if (finalCleanContent && finalCleanContent.trim() !== '') {
                        if (!currentResponseDiv) {
                            currentResponseDiv = addMessage('', false);
                        }
                        currentResponseDiv.innerHTML = marked.parse(finalCleanContent);
                        
                        // Ensure the final message is visible
                        setTimeout(() => {
                            chatMessages.scrollTop = chatMessages.scrollHeight;
                        }, currentConfig.UI.AUTO_SCROLL_DELAY);
                    }
                    
                    // Update conversation history
                    conversationHistory.push({ role: 'user', content: messageInput.value });
                    conversationHistory.push({ role: 'assistant', content: finalCleanContent });
                    
                    eventSource.close();
                    // Reset scroll position when switching to ready status
                    statusIndicator.scrollTop = 0;
                    updateStatus(currentConfig.STATUS.READY);
                    return;
                }

                const parsed = JSON.parse(event.data);
                // Handle array of messages (like in the curl output)
                const messageArray = Array.isArray(parsed) ? parsed : [parsed];
                
                for (const message of messageArray) {
                    if (message.content) {
                        // Use the latest complete content from this chunk
                        fullResponse = message.content;
                        
                        // Extract think content from the current chunk
                        const newThinkContent = extractThinkContent(fullResponse);
                        const cleanContent = cleanResponseContent(fullResponse);
                        
                        console.log('Processing message:', {
                            newThinkContent: newThinkContent ? newThinkContent.substring(0, 50) + '...' : null,
                            cleanContent: cleanContent ? cleanContent.substring(0, 50) + '...' : null,
                            hasResponseDiv: !!currentResponseDiv
                        });
                        
                        if (newThinkContent) {
                            // Show thinking content in status area
                            console.log('🟦 THINKING PHASE - Showing thinking in status');
                            thinkContent = newThinkContent;
                            updateStatus(`${currentConfig.MESSAGES.THINKING_PREFIX} ${thinkContent}`, 'thinking');
                        }
                        
                        if (cleanContent && cleanContent.trim() !== '') {
                            // Show response content in message balloon in real-time
                            console.log('🟩 RESPONSE PHASE - Updating response in real-time');
                            if (!currentResponseDiv) {
                                currentResponseDiv = addMessage('', false);
                            }
                            // Update content in real-time with streaming cursor
                            currentResponseDiv.innerHTML = marked.parse(cleanContent) + '<span class="streaming-cursor"></span>';
                            
                            // Ensure the new message is visible
                            setTimeout(() => {
                                chatMessages.scrollTop = chatMessages.scrollHeight;
                            }, currentConfig.UI.AUTO_SCROLL_DELAY);
                        }
                    }
                }
            } catch (e) {
                console.error('Error parsing SSE data:', e);
            }
        };

        eventSource.onerror = function(event) {
            console.error('SSE Error:', event);
            updateStatus(currentConfig.STATUS.CONNECTION_ERROR, 'error');
            eventSource.close();
        };
    }

    // Event listeners
    sendButton.addEventListener('click', sendMessage);
    messageInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });

    // Focus on input when page loads
    messageInput.focus();
}

// Initialize the application when the page loads
document.addEventListener('DOMContentLoaded', initializeApp); 