document.addEventListener("DOMContentLoaded", () => {
    // Toggle dark mode
    document.getElementById("darkModeToggle").addEventListener("click", () => {
        document.body.classList.toggle("dark-mode");
    });
    

    // Edit user action
    document.querySelectorAll(".edit-btn").forEach(button => {
        button.addEventListener("click", () => {
            alert("Editing user: " + button.closest("tr").children[0].textContent);
        });
    });

    // Delete user action
    document.querySelectorAll(".delete-btn").forEach(button => {
        button.addEventListener("click", () => {
            if (confirm("Are you sure you want to delete this user?")) {
                button.closest("tr").remove();
                alert("user deleted")
            }
        });
    });
});
document.addEventListener("DOMContentLoaded", () => {
    const users = [
        { id: 1, name: "Alice Johnson", email: "alice@example.com", role: "Admin" },
        { id: 2, name: "Bob Smith", email: "bob@example.com", role: "Investigator" },
        { id: 3, name: "Charlie Brown", email: "charlie@example.com", role: "Forensic Analyst" }
    ];

    const userTableBody = document.getElementById("userTableBody");
    
    function renderUsers() {
        userTableBody.innerHTML = "";
        users.forEach(user => {
            const row = document.createElement("tr");
            row.innerHTML = `
                <td>${user.id}</td>
                <td>${user.name}</td>
                <td>${user.email}</td>
                <td>${user.role}</td>
                <td><button class="revoke-btn" data-id="${user.id}">Revoke Access</button></td>
            `;
            userTableBody.appendChild(row);
        });
    }

    userTableBody.addEventListener("click", (event) => {
        if (event.target.classList.contains("revoke-btn")) {
            const userId = parseInt(event.target.dataset.id);
            const index = users.findIndex(user => user.id === userId);
            if (index !== -1) {
                users.splice(index, 1);
                renderUsers();
                alert("User access revoked.");
            }
        }
    });

    renderUsers();
});
document.addEventListener("DOMContentLoaded", () => {
    const users = [
        { id: 1, name: "Alice Johnson", email: "alice@example.com", role: "Admin" },
        { id: 2, name: "Bob Smith", email: "bob@example.com", role: "Investigator" },
        { id: 3, name: "Charlie Brown", email: "charlie@example.com", role: "Forensic Analyst" }
    ];

    const requests = [
        { id: 101, user: "Bob Smith", document: "Case File 123", status: "Pending" },
        { id: 102, user: "Charlie Brown", document: "Evidence Report 456", status: "Approved" }
    ];

    const logs = [
        { id: 201, timestamp: "2025-03-09 12:00", user: "Alice Johnson", action: "Logged in" },
        { id: 202, timestamp: "2025-03-09 12:05", user: "Bob Smith", action: "Requested access to Case File 123" }
    ];

    function renderTable(data, tableBodyId) {
        const tableBody = document.getElementById(tableBodyId);
        if (!tableBody) return;
        tableBody.innerHTML = "";
        data.forEach(item => {
            const row = document.createElement("tr");
            row.innerHTML = Object.values(item).map(value => `<td>${value}</td>`).join("") +
                (tableBodyId === "userTableBody" ? `<td><button class='revoke-btn' data-id='${item.id}'>Revoke</button></td>` : "");
            tableBody.appendChild(row);
        });
    }

    document.addEventListener("click", (event) => {
        if (event.target.classList.contains("revoke-btn")) {
            const userId = parseInt(event.target.dataset.id);
            const index = users.findIndex(user => user.id === userId);
            if (index !== -1) {
                users.splice(index, 1);
                renderTable(users, "userTableBody");
                alert("User access revoked.");
            }
        }
    });

    document.getElementById("settingsForm")?.addEventListener("submit", (event) => {
        event.preventDefault();
        alert("Settings saved successfully.");
    });

    renderTable(users, "userTableBody");
    renderTable(requests, "requestTableBody");
    renderTable(logs, "logTableBody");
});
