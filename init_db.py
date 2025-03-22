from app import app, db
from models import User, Event

with app.app_context():
    db.create_all()
    
    # Create test user only if it doesn't exist
    if not User.query.filter_by(username='admin').first():
        user = User(username='admin')
        user.set_password('password')
        db.session.add(user)
        db.session.commit()
    print("Database initialized successfully!")