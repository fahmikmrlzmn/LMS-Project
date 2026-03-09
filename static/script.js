// Auto-scroll AI chat to the latest message
window.addEventListener('load', () => {
    const chatContainer = document.querySelector('.ai-chat');
    if (chatContainer) {
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }
});