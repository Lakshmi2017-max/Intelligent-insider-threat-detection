from extensions import db
from app import app
from models import User, Activity
from datetime import datetime

with app.app_context():
    # Find the existing admin user
    user = User.query.filter_by(username="admin").first()
    if not user:
        print("No admin user found. Please create one first.")
    else:
        # Add sample activities
        activities = [
            Activity(user_id=user.id, action="Login", timestamp=datetime(2026, 5, 1, 23, 30)),  # late login
            Activity(user_id=user.id, action="File Access", timestamp=datetime(2026, 5, 2, 1, 15)),  # very late
            Activity(user_id=user.id, action="Email Sent", timestamp=datetime(2026, 5, 2, 9, 45)),
            Activity(user_id=user.id, action="Login", timestamp=datetime(2026, 5, 2, 22, 10)),  # late again
            Activity(user_id=user.id, action="File Download", timestamp=datetime(2026, 5, 2, 14, 20)),
        ]

        db.session.add_all(activities)
        db.session.commit()

        print("Sample activities added for admin user.")
