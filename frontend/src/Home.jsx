// import React, { useEffect, useState, useRef } from 'react';
// import { marked } from 'marked';
// import './home.css';

// const Home = () => {
//     const [messages, setMessages] = useState([]);
//     const [inputValue, setInputValue] = useState('');
//     const [isLoading, setIsLoading] = useState(false);
//     const [chatId] = useState('main-chat');
//     const messagesEndRef = useRef(null);
//     const chatContainerRef = useRef(null);

//     useEffect(() => {
//         // Configure marked options with better formatting
//         marked.setOptions({
//             breaks: true,
//             gfm: true,
//             headerIds: false,
//             highlight: function(code, lang) {
//                 // Add syntax highlighting placeholder
//                 return `<pre class="code-block"><code class="language-${lang || 'text'}">${code}</code></pre>`;
//             }
//         });

//         // Load chat history from localStorage
//         loadChatHistory();
        
//         // Add welcome message if no history
//         if (messages.length === 0) {
//             const welcomeMessage = {
//                 type: 'bot',
//                 content: '👋 Welcome to the Construction Project Management Assistant! How can I help you today?',
//                 timestamp: new Date().toISOString()
//             };
//             setMessages([welcomeMessage]);
//         }
//     }, []);

//     useEffect(() => {
//         // Scroll to bottom when new messages are added
//         scrollToBottom();
//     }, [messages]);

//     const scrollToBottom = () => {
//         messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
//     };

//     const loadChatHistory = () => {
//         try {
//             const savedHistory = localStorage.getItem('chatHistory');
//             if (savedHistory) {
//                 setMessages(JSON.parse(savedHistory));
//             }
//         } catch (error) {
//             console.error('Error loading chat history:', error);
//         }
//     };

//     const saveChatHistory = (updatedMessages) => {
//         try {
//             localStorage.setItem('chatHistory', JSON.stringify(updatedMessages));
//         } catch (error) {
//             console.error('Error saving chat history:', error);
//         }
//     };

//     const sendMessage = async () => {
//         if (!inputValue.trim() || isLoading) return;

//         const userMessage = {
//             type: 'user',
//             content: inputValue,
//             timestamp: new Date().toISOString()
//         };

//         const updatedMessages = [...messages, userMessage];
//         setMessages(updatedMessages);
//         setInputValue('');
//         setIsLoading(true);

//         try {
//             const response = await fetch('http://127.0.0.1:5000/api/chat', {
//                 method: 'POST',
//                 headers: {
//                     'Content-Type': 'application/json',
//                 },
//                 body: JSON.stringify({
//                     message: inputValue,
//                     chat_id: chatId
//                 })
//             });

//             if (!response.ok) {
//                 throw new Error('Server error');
//             }

//             const data = await response.json();
            
//             const botMessage = {
//                 type: 'bot',
//                 content: data.message,
//                 timestamp: new Date().toISOString(),
//                 metadata: {
//                     success: data.success
//                 }
//             };

//             const finalMessages = [...updatedMessages, botMessage];
//             setMessages(finalMessages);
//             saveChatHistory(finalMessages);
//         } catch (error) {
//             console.error('Error:', error);
//             const errorMessage = {
//                 type: 'bot',
//                 content: 'Sorry, I encountered an error while processing your request. Please try again.',
//                 timestamp: new Date().toISOString(),
//                 isError: true
//             };
            
//             const finalMessages = [...updatedMessages, errorMessage];
//             setMessages(finalMessages);
//             saveChatHistory(finalMessages);
//         } finally {
//             setIsLoading(false);
//         }
//     };

//     const handleKeyPress = (e) => {
//         if (e.key === 'Enter' && !e.shiftKey) {
//             e.preventDefault();
//             sendMessage();
//         }
//     };

//     const clearChat = () => {
//         if (window.confirm('Are you sure you want to clear the chat history?')) {
//             const welcomeMessage = {
//                 type: 'bot',
//                 content: '👋 Welcome to the Construction Project Management Assistant! How can I help you today?',
//                 timestamp: new Date().toISOString()
//             };
//             setMessages([welcomeMessage]);
//             localStorage.removeItem('chatHistory');
//         }
//     };

//     const askQuestion = (question) => {
//         setInputValue(question);
//         setTimeout(() => sendMessage(), 100);
//     };

//     const formatContent = (content) => {
//         // Parse markdown
//         let html = marked.parse(content);
        
//         // Add progress bars for percentages
//         html = html.replace(/(\d+(\.\d+)?)%\s*(complete|progress|done)/gi, (match, percentage) => {
//             const numPercentage = parseFloat(percentage);
//             return `${match}
//                 <div class="progress-indicator">
//                     <div class="progress-bar" style="width: ${numPercentage}%"></div>
//                 </div>`;
//         });
        
//         // Enhance list formatting
//         html = html.replace(/<ul>/g, '<ul class="enhanced-list">');
//         html = html.replace(/<ol>/g, '<ol class="enhanced-list">');
        
//         // Enhance table formatting
//         html = html.replace(/<table>/g, '<div class="table-container"><table class="enhanced-table">');
//         html = html.replace(/<\/table>/g, '</table></div>');
        
//         return { __html: html };
//     };

//     const suggestionButtons = [
//         { text: 'Show me all active projects', icon: 'bi-list-check' },
//         { text: 'What is the status of JAIN-1B project?', icon: 'bi-info-circle' },
//         { text: 'Show me progress of ELMGROVE-1B', icon: 'bi-graph-up' },
//         { text: 'Show me the details of CABOT-1B project', icon: 'bi-file-earmark-text' },
//         { text: 'What selections are due this week?', icon: 'bi-calendar-check' },
//         { text: 'Show me pending walkthroughs', icon: 'bi-building-check' },
//         { text: 'What\'s the budget status for all projects?', icon: 'bi-currency-dollar' }
//     ];

//     return (
//         <div className="chat-app-container">
//             <div className="chat-container">
//                 <div className="chat-header">
//                     <div className="header-content">
//                         <div className="logo-section">
//                             <div className="logo-icon">
//                                 <i className="bi bi-building-fill"></i>
//                             </div>
//                             <div className="logo-text">
//                                 <h4>Construction Project Assistant</h4>
//                                 <span className="status-indicator">Online</span>
//                             </div>
//                         </div>
//                         <button 
//                             onClick={clearChat}
//                             className="clear-chat-btn"
//                             title="Clear Chat"
//                         >
//                             <i className="bi bi-trash3"></i>
//                         </button>
//                     </div>
//                 </div>

//                 <div className="chat-messages" ref={chatContainerRef}>
//                     {messages.map((message, index) => (
//                         <div key={index} className="message-wrapper">
//                             <div className={`message ${message.type === 'user' ? 'user-message' : 'bot-message'} ${message.isError ? 'error-message' : ''}`}>
//                                 {message.type === 'bot' && (
//                                     <div className="bot-avatar">
//                                         <i className="bi bi-robot"></i>
//                                     </div>
//                                 )}
//                                 <div className="message-content">
//                                     {message.type === 'user' ? (
//                                         <div className="message-text">{message.content}</div>
//                                     ) : (
//                                         <div 
//                                             className="message-text markdown-content"
//                                             dangerouslySetInnerHTML={formatContent(message.content)} 
//                                         />
//                                     )}
//                                     <div className="message-meta">
//                                         <span className="message-time">
//                                             {new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
//                                         </span>
//                                         {message.metadata?.success && (
//                                             <span className="success-indicator">
//                                                 <i className="bi bi-check-circle-fill"></i>
//                                             </span>
//                                         )}
//                                     </div>
//                                 </div>
//                                 {message.type === 'user' && (
//                                     <div className="user-avatar">
//                                         <i className="bi bi-person-fill"></i>
//                                     </div>
//                                 )}
//                             </div>
//                         </div>
//                     ))}
                    
//                     {isLoading && (
//                         <div className="message-wrapper">
//                             <div className="message bot-message">
//                                 <div className="bot-avatar">
//                                     <i className="bi bi-robot"></i>
//                                 </div>
//                                 <div className="message-content">
//                                     <div className="typing-indicator">
//                                         <span></span>
//                                         <span></span>
//                                         <span></span>
//                                     </div>
//                                 </div>
//                             </div>
//                         </div>
//                     )}
                    
//                     {/* Suggestion buttons */}
//                     {messages.length === 1 && (
//                         <div className="suggestions-container">
//                             <div className="suggestions-label">
//                                 <i className="bi bi-lightbulb"></i> Here are some questions you can ask:
//                             </div>
//                             <div className="suggestions-grid">
//                                 {suggestionButtons.map((suggestion, index) => (
//                                     <button
//                                         key={index}
//                                         className="suggestion-btn"
//                                         onClick={() => askQuestion(suggestion.text)}
//                                     >
//                                         <i className={suggestion.icon}></i>
//                                         <span>{suggestion.text}</span>
//                                     </button>
//                                 ))}
//                             </div>
//                         </div>
//                     )}
//                     <div ref={messagesEndRef} />
//                 </div>

//                 <div className="chat-input-container">
//                     <div className="input-wrapper">
//                         <input
//                             type="text"
//                             className="chat-input"
//                             placeholder="Type your message here..."
//                             value={inputValue}
//                             onChange={(e) => setInputValue(e.target.value)}
//                             onKeyDown={handleKeyPress}
//                             disabled={isLoading}
//                         />
//                         <button 
//                             className={`send-btn ${inputValue.trim() && !isLoading ? 'active' : ''}`}
//                             onClick={sendMessage}
//                             disabled={isLoading || !inputValue.trim()}
//                         >
//                             <i className="bi bi-send-fill"></i>
//                         </button>
//                     </div>
//                     <div className="input-footer">
//                         <span>Press Enter to send, Shift+Enter for new line</span>
//                     </div>
//                 </div>
//             </div>
//         </div>
//     );
// };

// export default Home;
import React, { useEffect, useState, useRef } from 'react';
import { marked } from 'marked';
import './home.css';

const Home = () => {
    const [messages, setMessages] = useState([]);
    const [inputValue, setInputValue] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [chatId] = useState('main-chat');
    const messagesEndRef = useRef(null);
    const chatContainerRef = useRef(null);

    useEffect(() => {
        // Configure marked options with better formatting
        marked.setOptions({
            breaks: true,
            gfm: true,
            headerIds: false,
            highlight: function(code, lang) {
                // Add syntax highlighting placeholder
                return `<pre class="code-block"><code class="language-${lang || 'text'}">${code}</code></pre>`;
            }
        });

        // Load chat history from localStorage
        loadChatHistory();
        
        // Add welcome message if no history
        if (messages.length === 0) {
            const welcomeMessage = {
                type: 'bot',
                content: '👋 Welcome to the Construction Project Management Assistant! How can I help you today?',
                timestamp: new Date().toISOString()
            };
            setMessages([welcomeMessage]);
        }
    }, []);

    useEffect(() => {
        // Scroll to bottom when new messages are added
        scrollToBottom();
    }, [messages]);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    const loadChatHistory = () => {
        try {
            const savedHistory = localStorage.getItem('chatHistory');
            if (savedHistory) {
                setMessages(JSON.parse(savedHistory));
            }
        } catch (error) {
            console.error('Error loading chat history:', error);
        }
    };

    const saveChatHistory = (updatedMessages) => {
        try {
            localStorage.setItem('chatHistory', JSON.stringify(updatedMessages));
        } catch (error) {
            console.error('Error saving chat history:', error);
        }
    };

    const sendMessage = async () => {
        if (!inputValue.trim() || isLoading) return;

        const userMessage = {
            type: 'user',
            content: inputValue,
            timestamp: new Date().toISOString()
        };

        const updatedMessages = [...messages, userMessage];
        setMessages(updatedMessages);
        setInputValue('');
        setIsLoading(true);

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: inputValue,
                    chat_id: chatId
                })
            });

            if (!response.ok) {
                throw new Error('Server error');
            }

            const data = await response.json();
            
            const botMessage = {
                type: 'bot',
                content: data.message,
                timestamp: new Date().toISOString(),
                metadata: {
                    success: data.success
                }
            };

            const finalMessages = [...updatedMessages, botMessage];
            setMessages(finalMessages);
            saveChatHistory(finalMessages);
        } catch (error) {
            console.error('Error:', error);
            const errorMessage = {
                type: 'bot',
                content: 'Sorry, I encountered an error while processing your request. Please try again.',
                timestamp: new Date().toISOString(),
                isError: true
            };
            
            const finalMessages = [...updatedMessages, errorMessage];
            setMessages(finalMessages);
            saveChatHistory(finalMessages);
        } finally {
            setIsLoading(false);
        }
    };

    const handleKeyPress = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    };

    const clearChat = () => {
        if (window.confirm('Are you sure you want to clear the chat history?')) {
            const welcomeMessage = {
                type: 'bot',
                content: '👋 Welcome to the Construction Project Management Assistant! How can I help you today?',
                timestamp: new Date().toISOString()
            };
            setMessages([welcomeMessage]);
            localStorage.removeItem('chatHistory');
        }
    };

    const askQuestion = (question) => {
        setInputValue(question);
        setTimeout(() => sendMessage(), 100);
    };

    const formatContent = (content) => {
        // Parse markdown
        let html = marked.parse(content);
        
        // Add progress bars for percentages
        html = html.replace(/(\d+(\.\d+)?)%\s*(complete|progress|done)/gi, (match, percentage) => {
            const numPercentage = parseFloat(percentage);
            return `${match}
                <div class="progress-indicator">
                    <div class="progress-bar" style="width: ${numPercentage}%"></div>
                </div>`;
        });
        
        // Enhance list formatting
        html = html.replace(/<ul>/g, '<ul class="enhanced-list">');
        html = html.replace(/<ol>/g, '<ol class="enhanced-list">');
        
        // Enhance table formatting
        html = html.replace(/<table>/g, '<div class="table-container"><table class="enhanced-table">');
        html = html.replace(/<\/table>/g, '</table></div>');
        
        return { __html: html };
    };

    const suggestionButtons = [
        { text: 'Show me all active projects', icon: 'bi-list-check' },
        { text: 'What is the status of JAIN-1B project?', icon: 'bi-info-circle' },
        { text: 'Show me progress of ELMGROVE-1B', icon: 'bi-graph-up' },
        { text: 'Show me the details of CABOT-1B project', icon: 'bi-file-earmark-text' },
        { text: 'What selections are due this week?', icon: 'bi-calendar-check' },
        { text: 'Show me pending walkthroughs', icon: 'bi-building-check' },
        { text: 'What\'s the budget status for all projects?', icon: 'bi-currency-dollar' }
    ];

    return (
        <div className="chat-app-container">
            <div className="chat-container">
                <div className="chat-header">
                    <div className="header-content">
                        <div className="logo-section">
                            <div className="logo-icon">
                                <i className="bi bi-building-fill"></i>
                            </div>
                            <div className="logo-text">
                                <h4>Construction Project Assistant</h4>
                                <span className="status-indicator">Online</span>
                            </div>
                        </div>
                        <div className="header-actions">
                            <button 
                                onClick={clearChat}
                                className="clear-chat-btn"
                                title="Clear Chat History"
                            >
                                <i className="bi bi-trash3-fill"></i>
                                <span>Clear Chat</span>
                            </button>
                        </div>
                    </div>
                </div>

                <div className="chat-messages" ref={chatContainerRef}>
                    {messages.map((message, index) => (
                        <div key={index} className="message-wrapper">
                            <div className={`message ${message.type === 'user' ? 'user-message' : 'bot-message'} ${message.isError ? 'error-message' : ''}`}>
                                {message.type === 'bot' && (
                                    <div className="bot-avatar">
                                        <i className="bi bi-robot"></i>
                                    </div>
                                )}
                                <div className="message-content">
                                    {message.type === 'user' ? (
                                        <div className="message-text">{message.content}</div>
                                    ) : (
                                        <div 
                                            className="message-text markdown-content"
                                            dangerouslySetInnerHTML={formatContent(message.content)} 
                                        />
                                    )}
                                    <div className="message-meta">
                                        <span className="message-time">
                                            {new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                        </span>
                                        {message.metadata?.success && (
                                            <span className="success-indicator">
                                                <i className="bi bi-check-circle-fill"></i>
                                            </span>
                                        )}
                                    </div>
                                </div>
                                {message.type === 'user' && (
                                    <div className="user-avatar">
                                        <i className="bi bi-person-fill"></i>
                                    </div>
                                )}
                            </div>
                        </div>
                    ))}
                    
                    {isLoading && (
                        <div className="message-wrapper">
                            <div className="message bot-message">
                                <div className="bot-avatar">
                                    <i className="bi bi-robot"></i>
                                </div>
                                <div className="message-content">
                                    <div className="typing-indicator">
                                        <span></span>
                                        <span></span>
                                        <span></span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    )}
                    
                    {/* Suggestion buttons */}
                    {messages.length === 1 && (
                        <div className="suggestions-container">
                            <div className="suggestions-label">
                                <i className="bi bi-lightbulb"></i> Here are some questions you can ask:
                            </div>
                            <div className="suggestions-grid">
                                {suggestionButtons.map((suggestion, index) => (
                                    <button
                                        key={index}
                                        className="suggestion-btn"
                                        onClick={() => askQuestion(suggestion.text)}
                                    >
                                        <i className={suggestion.icon}></i>
                                        <span>{suggestion.text}</span>
                                    </button>
                                ))}
                            </div>
                        </div>
                    )}
                    <div ref={messagesEndRef} />
                </div>

                <div className="chat-input-container">
                    <div className="input-wrapper">
                        <input
                            type="text"
                            className="chat-input"
                            placeholder="Type your message here..."
                            value={inputValue}
                            onChange={(e) => setInputValue(e.target.value)}
                            onKeyDown={handleKeyPress}
                            disabled={isLoading}
                        />
                        <button 
                            className={`send-btn ${inputValue.trim() && !isLoading ? 'active' : ''}`}
                            onClick={sendMessage}
                            disabled={isLoading || !inputValue.trim()}
                            title="Send message"
                        >
                            <div className="btn-icon-wrapper">
                                <i className="bi bi-send-fill"></i>
                            </div>
                            <span className="btn-text">Send</span>
                        </button>
                    </div>
                    <div className="input-footer">
                        <div className="shortcuts-hint">
                            <span><kbd>Enter</kbd> to send</span>
                            <span><kbd>Shift</kbd> + <kbd>Enter</kbd> for new line</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Home;