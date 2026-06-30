from extensions import db
from app import app
from models import User

with app.app_context():
    # Create tables if not exist
    db.create_all()

    # Add a test user
    test_user = User(username="admin", password="password123")
    db.session.add(test_user)
    db.session.commit()

    print("Test user created: admin / password123")
