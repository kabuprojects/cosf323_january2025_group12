from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = "your_secret_key"

# Dummy user database (Replace with actual DB later)
users = {
    "admin@example.com": {
        "name": "Admin User",
        "email": "admin@example.com",
        "password": generate_password_hash("admin123"),
        "role": "Admin"
    },
    "manager@example.com": {
        "name": "Evidence Manager",
        "email": "manager@example.com",
        "password": generate_password_hash("manager123"),
        "role": "Evidence Manager"
    }
}

# Dummy storage for uploaded evidence
evidence_files = []

# Storage for access requests
access_requests = []

def delete_user(email):
    if email in users:
        del users[email]  # Remove user from dictionary


def find_user_by_email(email):
    return users.get(email, None)
# Fetch all users (returns a list of users)
def get_all_users():
    return list(users.values())  # Convert dictionary values to a list

# Fetch all access requests
def get_access_requests():
    return access_requests  # Return list of access requests


@app.route("/")
def home():
    return render_template("home.html")
   # user registration route
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]
        role = request.form["role"]

   #check if email is already registered
        if email in users:
            flash("Email already registered!", "danger")
            return redirect(url_for("register"))

  #check if passwords match
        if password != confirm_password:
            flash("Passwords do not match!", "danger")
            return redirect(url_for("register"))

  #save user in the dummy database
        users[email] = {
            "name": name,
            "email": email,
            "password": generate_password_hash(password),
            "role": role
        }
        
        flash("Registration successful! You can now log in.", "success")
        return redirect(url_for("login"))
    
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = find_user_by_email(email)
        
         # Check if user exists and password is correct
        if user and check_password_hash(user["password"], password):
            session["user_email"] = user["email"]
            flash("Login successful!", "success")

            # ✅ Redirect Admin to Admin Dashboard
            if user["role"] == "Admin":
                return redirect(url_for("admin_dashboard"))

            return redirect(url_for("dashboard"))
  
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("user_email", None)
    flash("Logged out successfully.", "info")
    return redirect(url_for("login"))

@app.route("/dashboard")
def dashboard():
    if "user_email" not in session:
        flash("Please log in first.", "danger")
        return redirect(url_for("login"))

    user_email = session["user_email"]
    user = find_user_by_email(user_email)

    if not user:
        flash("User not found.", "danger")
        return redirect(url_for("login"))

    return render_template("dashboard.html", user=user, evidence_files=evidence_files)

@app.route("/update_profile", methods=["GET", "POST"])
def update_profile():
    if "user_email" not in session:
        flash("Please log in first.", "danger")
        return redirect(url_for("login"))

    user_email = session["user_email"]
    user = find_user_by_email(user_email)

    if not user:
        flash("User not found.", "danger")
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        user["name"] = request.form["name"]
        user["email"] = request.form["email"]
        new_password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if new_password:
            if new_password != confirm_password:
                flash("Passwords do not match!", "danger")
                return redirect(url_for("update_profile"))
            user["password"] = generate_password_hash(new_password)

        session["user_email"] = user["email"]
        flash("Profile updated successfully!", "success")
        return redirect(url_for("dashboard"))

    return render_template("update_profile.html", user=user)

@app.route("/upload_evidence", methods=["GET", "POST"])
def upload_evidence():
    if "user_email" not in session:
        flash("Please log in first.", "danger")
        return redirect(url_for("login"))

    user_email = session["user_email"]
    user = find_user_by_email(user_email)

    if not user or user["role"] not in ["Admin", "Evidence Manager"]:
        flash("You do not have permission to upload evidence.", "danger")
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        file_name = request.form.get("file_name", "").strip()
        file_description = request.form.get("file_description", "").strip()
        classification = request.form.get("classification", "").strip()

        if not file_name or not file_description:
            flash("All fields are required!", "danger")
            return redirect(url_for("upload_evidence"))

        evidence_files.append({
            "name": file_name,
            "description": file_description,
            "classification": classification,
            "uploaded_by": user["name"],
            "role": user["role"]  })

        flash("Evidence uploaded successfully!", "success")
        return redirect(url_for("dashboard"))

    return render_template("upload_evidence.html", user=user)

@app.route("/documents", methods=["GET"])
def documents():
    if "user_email" not in session:
        flash("Please log in first.", "danger")
        return redirect(url_for("login"))

    user_email = session["user_email"]
    user = find_user_by_email(user_email)

    search_query = request.args.get("search", "").lower()
    classification_filter = request.args.get("classification", "")

    # Filtering logic
    filtered_documents = []
    for doc in evidence_files:
        if search_query in doc["name"].lower() or search_query in doc["description"].lower():
            if classification_filter == "" or doc["classification"] == classification_filter:
                filtered_documents.append(doc)

    return render_template("documents.html", user=user, evidence_files=filtered_documents)

@app.route("/evidence_list")
def evidence_list():
    if "user_email" not in session:
        flash("Please log in first.", "danger")
        return redirect(url_for("login"))

    user_email = session["user_email"]
    user = find_user_by_email(user_email)

    return render_template("evidence_list.html", user=user, evidence_files=evidence_files)

@app.route("/change_password", methods=["GET", "POST"])
def change_password():
    if "user_email" not in session:
        flash("Please log in first.", "danger")
        return redirect(url_for("login"))

    user_email = session["user_email"]
    user = find_user_by_email(user_email)

    if not user:
        flash("User not found.", "danger")
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        current_password = request.form["current_password"]
        new_password = request.form["new_password"]
        confirm_password = request.form["confirm_password"]

        if not check_password_hash(user["password"], current_password):
            flash("Current password is incorrect!", "danger")
            return redirect(url_for("change_password"))

        if new_password != confirm_password:
            flash("New passwords do not match!", "danger")
            return redirect(url_for("change_password"))

        user["password"] = generate_password_hash(new_password)
        flash("Password updated successfully!", "success")
        return redirect(url_for("dashboard"))

    return render_template("change_password.html", user=user)

@app.route("/admin_dashboard")
def admin_dashboard():
    if "user_email" not in session:
        flash("Please log in first.", "danger")
        return redirect(url_for("login"))

    user_email = session["user_email"]  
    user = find_user_by_email(user_email)

    if not user or user["role"] != "Admin":
        flash("Unauthorized access.", "danger")
        return redirect(url_for("dashboard"))

    # Ensure `users` and `access_requests` are fetched properly
    users = get_all_users()  # Make sure this function is defined
    access_requests = get_access_requests()  # Fetch from database
    pending_requests = [req for req in access_requests if req["status"] == "Pending"]

    return render_template("admin_dashboard.html", users=users, access_requests=access_requests, pending_requests=pending_requests)

@app.route("/manage_users", methods=["GET", "POST"])
def view_manage_users():
    if "user_email" not in session or find_user_by_email(session["user_email"])["role"] != "Admin":
        flash("Unauthorized action.", "danger")
        return redirect(url_for("admin_dashboard"))

    # Fetch users from database (assuming you use a database)
    users = get_all_users()  # Define this function to fetch users

    if request.method == "POST":
        action = request.form.get("action")
        email = request.form.get("email")

        if action == "delete":
            user = find_user_by_email(email)
            if user:
                delete_user(email)  # Define a function to delete users
                flash(f"User {email} deleted successfully!", "success")
            else:
                flash("User not found.", "danger")
            return redirect(url_for("view_manage_users"))

    return render_template("manage_users.html", users=users)

@app.route("/process_request", methods=["POST"])
def process_request():
    if "user_email" not in session or find_user_by_email(session["user_email"])["role"] != "Admin":
        flash("Unauthorized action.", "danger")
        return redirect(url_for("admin_dashboard"))

    user_email = request.form.get("user_email")
    document_name = request.form.get("document_name")
    action = request.form.get("action")

    for req in access_requests:
        if req["user_email"] == user_email and req["document_name"] == document_name:
            req["status"] = "Approved" if action == "approve" else "Rejected"
            flash(f"Access {req['status'].lower()} for {req['document_name']}.", "info")
            break

    return redirect(url_for("admin_dashboard"))

@app.route("/access_requests")
def view_access_requests():
    if "user_email" not in session:
        flash("Please log in first.", "danger")
        return redirect(url_for("login"))
    
    user = find_user_by_email(session["user_email"])
    if not user or user["role"] != "Admin":
        flash("Unauthorized access.", "danger")
        return redirect(url_for("dashboard"))

    return render_template("access_requests.html", access_requests=access_requests)

@app.route("/security_logs")
def view_security_logs():
    if "user_email" not in session:
        flash("Please log in first.", "danger")
        return redirect(url_for("login"))

    user = find_user_by_email(session["user_email"])
    if not user or user["role"] != "Admin":
        flash("Unauthorized access.", "danger")
        return redirect(url_for("dashboard"))

    return render_template("security_logs.html")

@app.route("/settings")
def view_settings():
    if "user_email" not in session:
        flash("Please log in first.", "danger")
        return redirect(url_for("login"))

    user = find_user_by_email(session["user_email"])
    if not user or user["role"] != "Admin":
        flash("Unauthorized access.", "danger")
        return redirect(url_for("dashboard"))

    return render_template("settings.html")

@app.route("/request_access", methods=["GET", "POST"])
def request_access():
    if "user_email" not in session:
        flash("Please log in first.", "danger")
        return redirect(url_for("login"))

    user_email = session["user_email"]

    if request.method == "POST":
        document_id = request.form.get("document_id")
        reason = request.form.get("reason")

        # Save the request
        access_requests.append({
            "user_email": user_email,
            "document_id": document_id,
            "reason": reason,
            "status": "Pending"
        })

        flash("Access request submitted successfully.", "success")
        return redirect(url_for("dashboard"))

    return render_template("request_access.html", documents=evidence_files)

if __name__ == '__main__':
    print("\n✅ REGISTERED ROUTES:")
for rule in app.url_map.iter_rules():
    print(f"{rule.endpoint:20} {rule.methods} {rule.rule}")
print("\n")

app.run(debug=True)

    