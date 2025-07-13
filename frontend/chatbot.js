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
  

  input.value = "";
  input.focus();
  const profile = window.profileManager
    ? window.profileManager.getCurrentProfile()
    : { id: 'guest', name: 'Guest', age: '', sex:'', blood_group: '', pre_cond: '' };

  // Display user message;
  chatBox.innerHTML += `<div class='bubble user'><strong>${profile.name}:</strong> ${userMessage}</div>`;


  // Choose endpoint based on toggle
  const endpoint = ragOnlyMode ? "http://localhost:8000/ask-rag-only" : "http://localhost:8000/ask";
  const aiMode = ragOnlyMode ? "RAG Only" : "Enhanced AI";
  
  const { age,  sex, blood_group, pre_cond } = profile;

  const contextString =
    `Information:\n` +
    `- Age: ${age || "N/A"|| "NA"}\n` +
    `- Gender: ${sex || "N/A" || "NA"}\n`+
    `- Blood Group: ${blood_group || "N/A"|| "NA"}\n` +
    `- Pre-existing Conditions: ${pre_cond || "None"}\n` +
    `Please consider these details when answering the following question:`;
  const combinedMessage = `${contextString} ${userMessage}`;
// Send to backend
  try {
    const response = await fetch(endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
         message: combinedMessage, 
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