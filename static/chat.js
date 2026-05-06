function scrollToBottom() {
    var chatDiv = document.getElementById('chatMessages');
    if (chatDiv) {
        chatDiv.scrollTop = chatDiv.scrollHeight;
    }
}

document.addEventListener('DOMContentLoaded', scrollToBottom);