// SongFinder App JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Add any global functionality here

    // Handle messages display
    const messages = document.querySelectorAll('.message');
    messages.forEach(message => {
        setTimeout(() => {
            message.style.opacity = '0';
            setTimeout(() => message.remove(), 300);
        }, 5000);
    });

    // Add loading states to forms
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading...';
            }
        });
    });
});

// Utility functions
function showLoading(element) {
    element.innerHTML = '<div class="loading"><div class="spinner"></div><p>Loading...</p></div>';
}

function hideLoading(element) {
    element.innerHTML = '';
}

function showMessage(message, type = 'success') {
    const messagesDiv = document.querySelector('.messages') || document.createElement('div');
    messagesDiv.className = 'messages';

    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    messageDiv.textContent = message;

    messagesDiv.appendChild(messageDiv);

    if (!document.querySelector('.messages')) {
        const container = document.querySelector('.content') || document.body;
        container.insertBefore(messagesDiv, container.firstChild);
    }

    // Auto remove after 5 seconds
    setTimeout(() => {
        messageDiv.style.opacity = '0';
        setTimeout(() => messageDiv.remove(), 300);
    }, 5000);
}