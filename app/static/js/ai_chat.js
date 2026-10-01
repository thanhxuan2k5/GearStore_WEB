// ==========================================
// GEARVN AI SALES ASSISTANT CHAT WIDGET
// ==========================================

const AIChat = {
    isOpen: false,

    toggle() {
        this.isOpen = !this.isOpen;
        const chatWindow = document.getElementById("aiChatWindow");
        if (chatWindow) {
            chatWindow.style.display = this.isOpen ? "flex" : "none";
            if (this.isOpen) {
                document.getElementById("aiChatInput")?.focus();
            }
        }
    },

    quickAsk(text) {
        const input = document.getElementById("aiChatInput");
        if (input) {
            input.value = text;
            this.send();
        }
    },

    async send() {
        const input = document.getElementById("aiChatInput");
        const body = document.getElementById("aiChatBody");
        if (!input || !body) return;

        const message = input.value.trim();
        if (!message) return;

        // Add user bubble
        this.appendMessage("user", message);
        input.value = "";

        // Add typing indicator
        const typingEl = document.createElement("div");
        typingEl.className = "chat-bubble ai";
        typingEl.id = "aiTypingIndicator";
        typingEl.innerHTML = `<em>Trợ lý AI đang tra cứu cấu hình & kho hàng...</em>`;
        body.appendChild(typingEl);
        body.scrollTop = body.scrollHeight;

        try {
            const res = await fetch("/api/v1/ai/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message: message })
            });
            const data = await res.json();
            
            // Remove typing
            typingEl.remove();

            // Format markdown reply
            let formattedReply = data.reply
                .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
                .replace(/\*(.*?)\*/g, "<em>$1</em>")
                .replace(/\n/g, "<br>");

            // Append AI response
            this.appendMessage("ai", formattedReply);

            // Render suggested questions chips
            if (data.suggested_questions && data.suggested_questions.length > 0) {
                const chipsBox = document.createElement("div");
                chipsBox.style.cssText = "display:flex;flex-wrap:wrap;gap:4px;margin-top:4px;";
                data.suggested_questions.slice(0, 3).forEach(q => {
                    const btn = document.createElement("button");
                    btn.className = "btn btn-outline";
                    btn.style.cssText = "font-size:11px;padding:4px 8px;border-radius:12px;background:#f1f5f9;";
                    btn.innerText = q;
                    btn.onclick = () => AIChat.quickAsk(q);
                    chipsBox.appendChild(btn);
                });
                body.appendChild(chipsBox);
            }

        } catch (err) {
            if (typingEl) typingEl.remove();
            this.appendMessage("ai", "Xin lỗi, đã xảy ra lỗi khi kết nối tới máy chủ AI. Bạn vui lòng thử lại sau giây lát.");
        }

        body.scrollTop = body.scrollHeight;
    },

    appendMessage(role, htmlContent) {
        const body = document.getElementById("aiChatBody");
        if (!body) return;

        const bubble = document.createElement("div");
        bubble.className = `chat-bubble ${role}`;
        bubble.innerHTML = htmlContent;
        body.appendChild(bubble);
        body.scrollTop = body.scrollHeight;
    }
};
