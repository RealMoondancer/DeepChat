let history = [];
let lastMsgId = -1;

// Function to add a new message to the chat box
function addMessage(message, isUser = true) {
    lastMsgId++;
    const chatBox = document.getElementById("chat-box");
    //chatBox.style.marginBottom = "20px"; // Activate marginBottom only after first message (looks shit otherwise)
    const messageDiv = document.createElement("div");
    messageDiv.classList.add(isUser ? "user-message" : "bot-message");
    messageDiv.innerHTML = `<p id="msg${lastMsgId}">${message}</p>`;
    chatBox.appendChild(messageDiv);
    chatBox.scrollTop = chatBox.scrollHeight; // Scroll to the latest message

    history[lastMsgId] = [message, isUser];

    return messageDiv;
}

// Function to handle the message submission
async function handleMessageSubmission() {
    const userInput = document.getElementById("user-input").value;
    const model = document.getElementById("modelSelect").value;
    if (userInput.trim() === "") return;

    addMessage(userInput.trim());
    document.getElementById("user-input").value = '';

    const response = await fetch("/request", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({prompt: userInput.trim(), model: model, history: history.slice(0, -1)})
    });

    const reader = response.body.getReader();
    let output = "";

    let botMsg = addMessage("", false);
    let id = lastMsgId;
    let message = botMsg.querySelector(`#msg${id}`);

    while (true) {
        const { done, value } = await reader.read();
        var text = new TextDecoder().decode(value);
        
        const regex = /^<<~(.)+?~>>$/g;
        const matches = text.match(regex);
        console.log(text);
        if (matches) {
            console.log("Found stop token");
            console.log("Stop reason: " + matches[0]);
            
        } else {
        message.textContent += text;
        //body.innerHTML = marked.parse(output);
        }
        var objDiv = document.getElementById("chat-box");
        objDiv.scrollTop = objDiv.scrollHeight;

        if (done) {
            history[id][0] = message.textContent;
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