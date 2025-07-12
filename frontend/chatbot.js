// Warn if profileManager isn’t available
document.addEventListener('DOMContentLoaded', () => {
  if (!window.profileManager) {
    console.warn('profileManager not found; defaulting to Guest profile');
  }
});

async function sendMessage() {
  const input = document.getElementById("user-input");
  const chatBox = document.getElementById("chat-box");
  const ragOnlyMode = document.getElementById("rag-only-mode")?.checked || false;

  const userMessage = input.value;
  if (!userMessage) return;

  const profile = window.profileManager
    ? window.profileManager.getCurrentProfile()
    : { id: 'guest', name: 'Guest', age: '', blood_group: '', pre_cond: '' };

  // Display user message;
  chatBox.innerHTML += `<div class='bubble user'><strong>${profile.name}:</strong> ${userMessage}</div>`;


  // Choose endpoint based on toggle
  const endpoint = ragOnlyMode ? "http://localhost:8000/ask-rag-only" : "http://localhost:8000/ask";
  const aiMode = ragOnlyMode ? "RAG Only" : "Enhanced AI";

  const { age, blood_group, pre_cond } = profile;
  const payload = { message: userMessage, mode: 'chat', sessionId: 'frontend-session', attachments: [], reset: false, profile: { age, blood_group, pre_cond } };

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
      <strong>QHelper AI (${aiMode}):</strong> ${botReply}${methodInfo}
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
  const ragToggle = document.getElementById("rag-only-mode");
  
  function updateStatus() {
    if (statusText) {
      if (ragToggle?.checked) {
        statusText.innerHTML = "� RAG-Only Mode - Knowledge Base Search";
      } else {
        statusText.innerHTML = "🟢 Enhanced AI Mode - RAG + LLM Reasoning";
      }
    }
  }
  
  // Set initial status
  updateStatus();
  
  // Update status when toggle changes
  if (ragToggle) {
    ragToggle.addEventListener("change", updateStatus);
  }
});