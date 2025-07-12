// function sendMessage() {
//   const input = document.getElementById("user-input");
//   const chatBox = document.getElementById("chat-box");

//   const userMessage = input.value;
//   if (!userMessage) return;

//   // Display user message
//   chatBox.innerHTML += `<div class="bubble user"><strong>You:</strong> ${userMessage}</div>`;

//   // Simulate bot response
//   const botReply = getBotReply(userMessage);
//   chatBox.innerHTML += `<div class="bubble bot"><strong>QHelper:</strong> ${botReply}</div>`;

//   input.value = "";
//   chatBox.scrollTop = chatBox.scrollHeight;
// }

// function getBotReply(message) {
//   // Placeholder logic – replace with real AI later
//   if (message.toLowerCase().includes("burn")) {
//     return "Cool the burn with water for 10 minutes and cover with a clean cloth.";
//   } else if (message.toLowerCase().includes("bleeding")) {
//     return "Apply pressure to the wound and elevate the area.";
//   } else {
//     return "I'm still learning! Try asking about burns or bleeding.";
//   }
// }

// function handleKey(event) {
//     if (event.key === "Enter") {
//         sendMessage();
//     }
// }

async function sendMessage() {
  const input = document.getElementById("user-input");
  const chatBox = document.getElementById("chat-box");

  const userMessage = input.value;
  if (!userMessage) return;

  // Display user message
  chatBox.innerHTML += `<p><strong>You:</strong> ${userMessage}</p>`;

  // Send to backend
  try {
    const response = await fetch("http://localhost:8000/ask", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        message: userMessage,
        mode: "chat",
        sessionId: "frontend-session",
        attachments: [],
        reset: false
      })
    });

    const result = await response.json();

    const botReply =
    result?.textResponse ||
    result?.message ||
    result?.response ||
    result?.error ||
  "No response received.";

    chatBox.innerHTML += `<p><strong>QHelper:</strong> ${botReply}</p>`;
  } catch (err) {
    chatBox.innerHTML += `<p><strong>QHelper:</strong> Something went wrong: ${err.message}</p>`;
  }

  input.value = "";
  chatBox.scrollTop = chatBox.scrollHeight;
}