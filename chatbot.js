function sendMessage() {
  const input = document.getElementById("user-input");
  const chatBox = document.getElementById("chat-box");

  const userMessage = input.value;
  if (!userMessage) return;

  // Display user message
  chatBox.innerHTML += `<p><strong>You:</strong> ${userMessage}</p>`;

  // Simulate bot response
  const botReply = getBotReply(userMessage);
  chatBox.innerHTML += `<p><strong>QHelper:</strong> ${botReply}</p>`;

  input.value = "";
  chatBox.scrollTop = chatBox.scrollHeight;
}

function getBotReply(message) {
  // Placeholder logic – replace with real AI later
  if (message.toLowerCase().includes("burn")) {
    return "Cool the burn with water for 10 minutes and cover with a clean cloth.";
  } else if (message.toLowerCase().includes("bleeding")) {
    return "Apply pressure to the wound and elevate the area.";
  } else {
    return "I'm still learning! Try asking about burns or bleeding.";
  }
}
