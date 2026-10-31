const emailList = document.getElementById("emailList");
const message = document.getElementById("message");

async function loadEmails() {
    message.textContent = "";
    emailList.innerHTML = '<p class="empty">Loading emails...</p>';

    try {
        const response = await fetch("/api/emails/list");

        if (!response.ok) {
            throw new Error("Could not load emails.");
        }

        const emails = await response.json();

        if (emails.length === 0) {
            emailList.innerHTML =
                '<p class="empty">No emails found. Connect Gmail and sync your emails.</p>';
            return;
        }

        emailList.innerHTML = emails.map(email => `
            <article class="email">
                <h3>${escapeHtml(email.subject || "No subject")}</h3>
                <p><strong>From:</strong> ${escapeHtml(email.sender || "Unknown")}</p>
                <p>${escapeHtml(email.body || "")}</p>
                <div class="email-actions">
                    <button class="generate"
                        onclick="generatePdf(${email.id}, this)">
                        Generate PDF
                    </button>
                    <span class="status"></span>
                </div>
            </article>
        `).join("");

    } catch (error) {
        emailList.innerHTML = "";
        message.textContent = error.message;
    }
}

async function generatePdf(emailId, button) {
    const status = button.parentElement.querySelector(".status");

    button.disabled = true;
    button.textContent = "Generating...";
    status.textContent = "";

    try {
        const response = await fetch(`/api/estimates/${emailId}/pdf`);

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || "PDF generation failed.");
        }

        const pdfBlob = await response.blob();
        const industry = response.headers.get("X-Quotation-Industry") || "Unknown";
        const filename = response.headers.get("X-Quotation-Number") || "quotation";

        const url = URL.createObjectURL(pdfBlob);
        const download = document.createElement("a");

        download.href = url;
        download.download = `${filename}.pdf`;
        download.className = "download";
        download.textContent = "Download PDF";

        button.replaceWith(download);
        status.textContent = `${industry.toUpperCase()} quotation ready`;

    } catch (error) {
        button.disabled = false;
        button.textContent = "Generate PDF";
        status.textContent = error.message;
        status.style.color = "#b42318";
    }
}

function escapeHtml(value) {
    return String(value).replace(/[&<>"']/g, char => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;"
    })[char]);
}

document.getElementById("refreshBtn").addEventListener("click", loadEmails);

document.getElementById("connectBtn").addEventListener("click", async () => {
    try {
        const response = await fetch("/api/gmail/status");

        if (!response.ok) {
            throw new Error("Gmail integration is not configured yet.");
        }

        const data = await response.json();

        if (data.connected) {
            const syncResponse = await fetch("/api/gmail/sync", {
                method: "POST"
            });

            if (!syncResponse.ok) {
                throw new Error("Gmail sync failed.");
            }

            await loadEmails();
            message.textContent = "Gmail emails synced.";
        } else {
            window.location.href = "/api/gmail/connect";
        }
    } catch (error) {
        message.textContent = error.message;
    }
});

loadEmails();