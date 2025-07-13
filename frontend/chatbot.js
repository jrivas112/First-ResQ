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
  
  // Send user query and profile separately (don't combine them at frontend)
  const requestBody = {
    message: userMessage,  // Pure user query only
    mode: "chat",
    sessionId: profile.id,  // Use profile ID as session ID for conversation history
    attachments: [],
    reset: false
  };
  
  // Add profile context only if not guest
  if (profile.id !== 'guest') {
    requestBody.profile = {
      age: age || "N/A",
      gender: sex || "N/A", 
      blood_group: blood_group || "N/A",
      pre_existing_conditions: pre_cond || "None"
    };
  }

// Send to backend
  try {
    const response = await fetch(endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(requestBody)
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

// Clear conversation history
async function clearConversation() {
  try {
    const profile = window.profileManager?.getCurrentProfile() || { id: 'guest', name: 'Guest' };
    
    if (!confirm(`Are you sure you want to clear the conversation history for ${profile.name}?`)) {
      return;
    }

    const response = await fetch("http://localhost:8000/clear-conversation", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ sessionId: profile.id })
    });
    
    const result = await response.json();
    
    if (result.status === "success") {
      // Clear the chat box visual history
      document.getElementById("chat-box").innerHTML = "";
      
      const profileInfo = profile.id === "guest" ? "Guest session" : `Profile: ${profile.name}`;
      // Show confirmation message
      document.getElementById("chat-box").innerHTML += 
        `<div class="bubble bot system-message">
          <strong>🧹 Conversation Cleared (${profileInfo})</strong><br>
          Your conversation history has been reset. You can start fresh!
        </div>`;
    }
  } catch (err) {
    console.error("Error clearing conversation:", err);
    document.getElementById("chat-box").innerHTML += 
      `<div class="bubble bot system-message">
        <strong>❌ Error:</strong> Could not clear conversation history.
      </div>`;
  }
}

// Get conversation summary
async function getConversationSummary() {
  try {
    const profile = window.profileManager?.getCurrentProfile() || { id: 'guest', name: 'Guest' };
    
    const response = await fetch(`http://localhost:8000/conversation-summary?sessionId=${profile.id}`);
    const summary = await response.json();
    
    if (summary.status === "success" && summary.total_exchanges > 0) {
      const chatBox = document.getElementById("chat-box");
      const profileInfo = summary.profile_id === "guest" ? "Guest" : `Profile: ${summary.profile_id}`;
      chatBox.innerHTML += 
        `<div class="bubble bot system-message">
          <strong>💬 Conversation Summary (${profileInfo}):</strong><br>
          • Total questions: ${summary.total_exchanges}<br>
          • Recent topics: ${summary.recent_topics.join(", ")}<br>
          • Context enabled: ${summary.context_enabled ? "✅ Yes" : "❌ No"}
        </div>`;
      chatBox.scrollTop = chatBox.scrollHeight;
    } else {
      const chatBox = document.getElementById("chat-box");
      const profile = window.profileManager?.getCurrentProfile() || { name: 'Guest' };
      chatBox.innerHTML += 
        `<div class="bubble bot system-message">
          <strong>💬 Conversation Summary (${profile.name}):</strong><br>
          No conversation history yet. Start by asking a first aid question!
        </div>`;
      chatBox.scrollTop = chatBox.scrollHeight;
    }
  } catch (err) {
    console.error("Error getting conversation summary:", err);
    document.getElementById("chat-box").innerHTML += 
      `<div class="bubble bot system-message">
        <strong>❌ Error:</strong> Could not get conversation summary.
      </div>`;
  }
}

// Add keyboard shortcut for clearing conversation
document.addEventListener("keydown", function(event) {
  // Ctrl+Shift+C to clear conversation
  if (event.ctrlKey && event.shiftKey && event.key === "C") {
    clearConversation();
  }
});