"""
Seed Database with Sample Data
Run this script to populate the database with test data
"""

import os
from datetime import datetime, timedelta
from app import create_app
from app.models import db, User, Admin, Event
from config import DevelopmentConfig

# Create application context
app = create_app(DevelopmentConfig)

def seed_database():
    """Populate database with sample data"""
    
    with app.app_context():
        # Clear existing data
        print("Clearing existing data...")
        db.drop_all()
        db.create_all()
        
        # Create admin user
        print("Creating admin user...")
        admin = Admin(username='admin')
        admin.set_password('admin123')
        db.session.add(admin)
        
        # Create sample users
        print("Creating sample users...")
        users = []
        sample_users = [
            {'name': 'John Doe', 'email': 'john@example.com', 'phone': '9876543210'},
            {'name': 'Jane Smith', 'email': 'jane@example.com', 'phone': '9876543211'},
            {'name': 'Alice Johnson', 'email': 'alice@example.com', 'phone': '9876543212'},
            {'name': 'Bob Wilson', 'email': 'bob@example.com', 'phone': '9876543213'},
            {'name': 'Carol White', 'email': 'carol@example.com', 'phone': '9876543214'},
            {'name': 'David Brown', 'email': 'david@example.com', 'phone': '9876543215'},
            {'name': 'Emma Davis', 'email': 'emma@example.com', 'phone': '9876543216'},
            {'name': 'Frank Miller', 'email': 'frank@example.com', 'phone': '9876543217'},
        ]
        
        for user_data in sample_users:
            user = User(
                name=user_data['name'],
                email=user_data['email'],
                phone=user_data['phone']
            )
            user.set_password('password123')
            users.append(user)
            db.session.add(user)
        
        db.session.commit()
        
        # Create sample events
        print("Creating sample events...")
        events = []
        base_date = datetime.now().date()
        
        sample_events = [
            {
                'event_name': 'Python Workshop',
                'description': 'Learn advanced Python programming concepts including decorators, generators, and async programming.',
                'date_offset': 7,
                'time': '10:00',
                'venue': 'Tech Hub, Downtown',
                'capacity': 50
            },
            {
                'event_name': 'Web Development Bootcamp',
                'description': 'Comprehensive bootcamp covering HTML, CSS, JavaScript, Flask, and Database design.',
                'date_offset': 14,
                'time': '09:00',
                'venue': 'Innovation Center',
                'capacity': 30
            },
            {
                'event_name': 'Data Science Seminar',
                'description': 'Explore data analysis, visualization, and machine learning with real-world examples.',
                'date_offset': 21,
                'time': '14:00',
                'venue': 'University Auditorium',
                'capacity': 100
            },
            {
                'event_name': 'Cloud Computing Conference',
                'description': 'Deep dive into AWS, Azure, and Google Cloud Platform with hands-on labs.',
                'date_offset': 28,
                'time': '11:00',
                'venue': 'Convention Center',
                'capacity': 200
            },
            {
                'event_name': 'AI & Machine Learning Expo',
                'description': 'Discover the latest trends in artificial intelligence and machine learning technologies.',
                'date_offset': 35,
                'time': '10:30',
                'venue': 'Tech Park',
                'capacity': 150
            },
            {
                'event_name': 'Cybersecurity Workshop',
                'description': 'Essential security practices for protecting applications and data from threats.',
                'date_offset': 42,
                'time': '13:00',
                'venue': 'Security Institute',
                'capacity': 60
            },
        ]
        
        for event_data in sample_events:
            event_date = base_date + timedelta(days=event_data['date_offset'])
            event_time_str = event_data['time']
            event_time = datetime.strptime(event_time_str, '%H:%M').time()
            
            event = Event(
                event_name=event_data['event_name'],
                event_date=event_date,
                event_time=event_time,
                venue=event_data['venue'],
                description=event_data['description'],
                capacity=event_data['capacity']
            )
            events.append(event)
            db.session.add(event)
        
        db.session.commit()
        
        # Register users for events
        print("Creating sample registrations...")
        from app.models import Registration
        from app.utils import generate_qr_code
        
        for i, user in enumerate(users):
            # Register each user for 2-4 random events
            num_registrations = (i % 3) + 2
            for j in range(num_registrations):
                event_index = (i + j) % len(events)
                event = events[event_index]
                
                # Check if registration already exists
                existing = Registration.query.filter_by(
                    user_id=user.id,
                    event_id=event.id
                ).first()
                
                if not existing and len(event.registrations) < event.capacity:
                    registration = Registration(
                        user_id=user.id,
                        event_id=event.id,
                        registration_date=datetime.now() - timedelta(days=7-j)
                    )
                    db.session.add(registration)
        
        db.session.commit()
        
        # Generate QR codes for all registrations
        from app.models import Registration
        registrations = Registration.query.all()
        for registration in registrations:
            qr_filename = generate_qr_code(
                registration.id,
                registration.user.email,
                registration.event.event_name
            )
            registration.qr_code_filename = qr_filename
        
        db.session.commit()
        
        # Print summary
        print("\n" + "="*50)
        print("Database seeding completed successfully!")
        print("="*50)
        print(f"\nAdmins Created: 1")
        print(f"  - Username: admin")
        print(f"  - Password: admin123")
        print(f"\nUsers Created: {len(users)}")
        print(f"Events Created: {len(events)}")
        print(f"Registrations Created: {Registration.query.count()}")
        print("\n" + "="*50)
        print("\nDefault Admin Credentials:")
        print("  Username: admin")
        print("  Password: admin123")
        print("\nSample User Credentials (all users):")
        print("  Password: password123")
        print("  Emails: john@example.com, jane@example.com, alice@example.com, etc.")
        print("\n" + "="*50)


if __name__ == '__main__':
    seed_database()
