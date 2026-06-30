from flask import Flask, render_template, request, redirect, url_for, flash
from extensions import db
from models import User, Activity
from datetime import datetime
from sqlalchemy.exc import IntegrityError
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Register the app with SQLAlchemy
db.init_app(app)

# ---------------- LOGIN ----------------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid credentials", "error")
    return render_template("login.html")

# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():
    user = User.query.filter_by(username="admin").first()
    activities = Activity.query.filter_by(user_id=user.id).order_by(Activity.timestamp.desc()).all()
    users = User.query.all()  # fetch all users for user management

    # Simple risk calculation
    risk = "Low"
    late_activities = [a for a in activities if a.timestamp.hour >= 23 or a.timestamp.hour < 5]
    if len(late_activities) >= 2:
        risk = "High"
    elif len(late_activities) == 1:
        risk = "Medium"

    return render_template("dashboard.html", user=user, activities=activities, risk=risk, users=users)

# ---------------- CLEAR DATA ----------------
@app.route("/clear-data", methods=["POST"])
def clear_data():
    Activity.query.delete()
    User.query.filter(User.username != "admin").delete()
    db.session.commit()
    flash("All data cleared!", "success")
    return redirect(url_for("dashboard"))

# ---------------- LOAD SAMPLE DATA ----------------
@app.route("/load-data", methods=["POST"])
def load_data():
    user = User.query.filter_by(username="admin").first()
    if user:
        sample_activities = [
            Activity(user_id=user.id, action="Login", timestamp=datetime(2026, 5, 2, 9, 0)),
            Activity(user_id=user.id, action="File Access", timestamp=datetime(2026, 5, 2, 10, 30)),
            Activity(user_id=user.id, action="Email Sent", timestamp=datetime(2026, 5, 2, 11, 15)),
            Activity(user_id=user.id, action="Login", timestamp=datetime(2026, 5, 2, 23, 45)),  # suspicious late login
        ]
        db.session.add_all(sample_activities)
        db.session.commit()
        flash("Sample data loaded!", "success")
    return redirect(url_for("dashboard"))

# ---------------- ADD USER ----------------
@app.route("/add-user", methods=["POST"])
def add_user():
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "").strip()

    # Prevent empty submissions
    if not username or not password:
        flash("Username and password are required!", "error")
        return redirect(url_for("dashboard"))

    # Prevent duplicates
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        flash(f"User '{username}' already exists!", "error")
        return redirect(url_for("dashboard"))

    try:
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash(f"User {username} added successfully!", "success")
    except IntegrityError:
        db.session.rollback()
        flash("Database error: could not add user.", "error")

    return redirect(url_for("dashboard"))

# ---------------- DELETE USER ----------------
@app.route("/delete-user/<int:user_id>", methods=["POST"])
def delete_user(user_id):
    user = User.query.get(user_id)
    if user and user.username != "admin":  # protect admin
        db.session.delete(user)
        db.session.commit()
        flash(f"User {user.username} deleted!", "success")
    else:
        flash("Cannot delete admin user!", "error")
    return redirect(url_for("dashboard"))

# ---------------- RUN APP ----------------
if __name__ == "__main__":
    with app.app_context():
        if not os.path.exists("database.db"):
            db.create_all()
    app.run(debug=True)
