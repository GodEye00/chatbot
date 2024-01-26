document.addEventListener('DOMContentLoaded', () => {
    const socket = io();

    socket.on('connect', () => {
        console.log('Connected to the server.');
    });

    socket.on('chat', data => {
        const message = data.message;
        displayMessage('Lucy', message);
    });

    socket.on('typing_indicator', data => {
        const typingIndicator = document.getElementById('typingIndicator');
        if (data.status) {
            typingIndicator.style.display = 'flex';
        } else {
            typingIndicator.style.display = 'none';
        }
    });

    document.getElementById('sendButton').addEventListener('click', () => {
        console.log("send button clicked")
        sendMessage();
    });

    document.getElementById('sendFileButton').addEventListener('click', () => {
        sendFile();
    });

    document.getElementById('recordButton').addEventListener('click', () => {
        // Implement audio recording functionality here
    });

    function sendMessage() {
        const messageInput = document.getElementById('messageInput');
        const message = messageInput.value;
        socket.emit('message_from_client', { type: 'text', message: message });
        displayMessage('You', message);
        messageInput.value = '';
    }

    function sendFile() {
        const fileInput = document.getElementById('fileInput');
        const file = fileInput.files[0];
        if (file) {
            // Implement file sending functionality here
            displayMessage('You', `Sent file: ${file.name}`);
        }
    }

    function displayMessage(sender, message) {
        const chatWindow = document.getElementById('chatWindow');
        const messageDiv = document.createElement('div');
        messageDiv.textContent = `${sender}: ${message}`;
        chatWindow.appendChild(messageDiv);
    }
});
