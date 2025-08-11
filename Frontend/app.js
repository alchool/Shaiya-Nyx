const API_BASE = "http://localhost:8000"; // Backend FastAPI
let accessToken = null;

// LOGIN
document.getElementById("login-btn").addEventListener("click", async () => {
    const username = document.getElementById("username").value.trim();
    const password = document.getElementById("password").value.trim();

    const res = await fetch(`${API_BASE}/api/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password })
    });

    if (res.ok) {
        const data = await res.json();
        accessToken = data.access_token;
        document.getElementById("login-section").classList.add("hidden");
        document.getElementById("status-section").classList.remove("hidden");
        document.getElementById("donation-section").classList.remove("hidden");
        loadServerStatus();
    } else {
        document.getElementById("login-message").textContent = "Credenziali errate.";
    }
});

// STATO SERVER
async function loadServerStatus() {
    const res = await fetch(`${API_BASE}/api/status`, {
        headers: { "Authorization": `Bearer ${accessToken}` }
    });
    if (res.ok) {
        const status = await res.json();
        document.getElementById("server-status").textContent = JSON.stringify(status);
    }
}

// DONAZIONE
document.getElementById("donate-btn").addEventListener("click", async () => {
    const amount = parseFloat(document.getElementById("donation-amount").value);
    const res = await fetch(`${API_BASE}/donate/create`, {
        method: "POST",
        headers: {
            "Authorization": `Bearer ${accessToken}`,
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ amount_usd: amount })
    });

    if (res.ok) {
        const data = await res.json();
        window.location.href = data.redirect_url; // PayPal redirect
    }
});
