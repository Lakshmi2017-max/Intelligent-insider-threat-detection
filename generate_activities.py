import time
import random
from datetime import datetime, timedelta
from extensions import db
from app import app
from models import User, Activity

actions = ["Login", "File Access", "Email Sent", "File Download", "Password Change"]

def random_timestamp():
    # 30% chance of suspicious late-night activity (between 11 PM and 3 AM)
    if random.random() < 0.3:
        hour = random.choice([23, 0, 1, 2, 3])
    else:
        hour = random.randint(8, 20)  # normal working hours
    return datetime.now().replace(hour=hour, minute=random.randint(0,59), second=random.randint(0,59))

with app.app_context():
    user = User.query.filter_by(username="admin").first()
    if not user:
        print("No admin user found. Please create one first.")
    else:
        print("Generating random activities for admin... Press CTRL+C to stop.")
        try:
            while True:
                action = random.choice(actions)
                timestamp = random_timestamp()
                activity = Activity(user_id=user.id, action=action, timestamp=timestamp)
                db.session.add(activity)
                db.session.commit()
                print(f"Added activity: {action} at {timestamp}")
                time.sleep(5)  # wait 5 seconds before adding the next activity
        except KeyboardInterrupt:
            print("Stopped activity generation.")
