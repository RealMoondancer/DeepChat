const API_URL = "/request";

// Function to add a new message to the chat box
function addMessage(message, isUser = true) {
    const chatBox = document.getElementById("chat-box");
    //chatBox.style.marginBottom = "20px"; // Activate marginBottom only after first message (looks shit otherwise)
    const messageDiv = document.createElement("div");
    messageDiv.classList.add(isUser ? "user-message" : "bot-message");
    messageDiv.innerHTML = `<p id="messageText">${message}</p>`;
    chatBox.appendChild(messageDiv);
    chatBox.scrollTop = chatBox.scrollHeight; // Scroll to the latest message

    return messageDiv;
}

// Function to handle the message submission
async function handleMessageSubmission() {
    const userInput = document.getElementById("user-input").value;
    if (userInput.trim() === "") return;

    addMessage(userInput.trim());
    document.getElementById("user-input").value = '';

    const response = await fetch("/request", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({prompt: userInput.trim()})
    });

    const reader = response.body.getReader();
    let output = "";

    let message = (addMessage("", false)).querySelector("#messageText");

    while (true) {
        const { done, value } = await reader.read();
        
        message.textContent += new TextDecoder().decode(value);
        //body.innerHTML = marked.parse(output);

        var objDiv = document.getElementById("chat-box");
        objDiv.scrollTop = objDiv.scrollHeight;

        if (done) {
            return;
        }
    }
}

// Add event listener for the send button
document.getElementById("send-btn").addEventListener("click", handleMessageSubmission);

// Add event listener for the "Enter" key to submit the message
document.getElementById("user-input").addEventListener("keypress", (e) => {
    if (e.key === 'Enter') {
        handleMessageSubmission();
    }
});