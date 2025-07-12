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
  chatBox.innerHTML += `<div class="bubble user"><strong>You:</strong> ${userMessage}</div>`;

  // Use local AI endpoint only
  const endpoint = "http://localhost:8000/ask";

  // Send to backend
  try {
    const response = await fetch(endpoint, {
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

    // Show confidence and method info if available (local AI)
    let methodInfo = "";
    if (result?.confidence) {
      methodInfo += ` <small>(Confidence: ${(result.confidence * 100).toFixed(1)}%)</small>`;
    }
    if (result?.method) {
      const methodLabels = {
        "rag_plus_ollama": "🤖 AI + Knowledge Base",
        "ollama_only": "🤖 AI Reasoning",
        "rag_only": "📚 Knowledge Base Only",
        "fallback": "🆘 General Advice"
      };
      methodInfo += ` <small>[${methodLabels[result.method] || result.method}]</small>`;
    }

    chatBox.innerHTML += `<div class="bubble bot">
      <strong>QHelper AI:</strong> ${botReply}${methodInfo}
    </div>`;
  } catch (err) {
    chatBox.innerHTML += `<div class="bubble bot">
      <strong>QHelper AI:</strong> Network error: ${err.message}
      <br><small><em>The local AI should work without internet. Please check if the backend is running.</em></small>
    </div>`;
  }

  input.value = "";
  chatBox.scrollTop = chatBox.scrollHeight;
}

function handleKey(event) {
    if (event.key === "Enter") {
        sendMessage();
    }
}

// Set status on page load
document.addEventListener("DOMContentLoaded", function() {
  const statusText = document.getElementById("status-text");
  if (statusText) {
    statusText.innerHTML = "🟢 Offline-First AI Assistant Ready";
  }
});