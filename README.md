# Event Management System (EMS)

A comprehensive, industry-level web-based Event Management System built with Python Flask for TYBSc Computer Science final year major projects.

## 🎯 Features

### User Features
- ✅ User Registration & Authentication
- ✅ Event Catalog with Search & Filtering
- ✅ One-Click Event Registration
- ✅ QR Code Ticket Generation & Download
- ✅ Personal Dashboard & Event Management
- ✅ Profile Management

### Admin Features
- ✅ Admin Dashboard with Statistics
- ✅ Complete Event Management (CRUD)
- ✅ Event Image Upload & Optimization
- ✅ User Management & Deletion
- ✅ Registration Oversight
- ✅ System Analytics

### Technical Features
- ✅ Modular Blueprint Architecture
- ✅ Application Factory Pattern
- ✅ SQLite (Development) & MySQL (Production) Support
- ✅ Secure Password Hashing (bcrypt)
- ✅ Session Management (Flask-Login)
- ✅ Responsive Bootstrap 5 UI
- ✅ QR Code Generation
- ✅ Image Processing (Pillow)

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| **Backend** | Python, Flask 3.0 |
| **Database** | SQLAlchemy ORM, SQLite/MySQL |
| **Frontend** | Jinja2, HTML5, CSS3, JavaScript, Bootstrap 5 |
| **Security** | Flask-Bcrypt, Flask-Login |
| **Extras** | python-qrcode, Pillow |

## 📁 Project Structure

```
EMS/
├── venv/                              # Virtual Environment
├── app/
│   ├── __init__.py                   # Application Factory
│   ├── models.py                     # SQLAlchemy Models
│   ├── utils.py                      # Helper Functions
│   ├── routes/
│   │   ├── auth.py                    # Authentication Routes
│   │   ├── user.py                    # User Routes
│   │   └── admin.py                   # Admin Routes
│   ├── templates/
│   │   ├── base.html                  # Base Layout
│   │   ├── auth/                      # Authentication Templates
│   │   ├── user/                      # User Templates
│   │   └── admin/                     # Admin Templates
│   └── static/
│       ├── css/style.css              # Custom Styles
│       ├── js/main.js                 # JavaScript
│       ├── uploads/                   # Event Images
│       └── qrcodes/                   # QR Codes
├── config.py                          # Configuration
├── run.py                             # Application Entry Point
├── seed_data.py                       # Database Seeder
├── requirements.txt                   # Dependencies
├── DOCUMENTATION.md                   # Complete Documentation
└── README.md                          # This File
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip
- Virtual Environment support

### Installation Steps

#### 1. Create Virtual Environment
```bash
cd "c:\Users\Ashish Yadav\Downloads\Ashish\EMS"
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux
```

#### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 3. Seed Database
```bash
python seed_data.py
```

You'll see output like:
```
==================================================
Database seeding completed successfully!
==================================================

Admins Created: 1
  - Username: admin
  - Password: admin123

Users Created: 8
Events Created: 6
Registrations Created: XX
...
```

#### 4. Run Application
```bash
python run.py
```

The application will be available at: **http://localhost:5000**

## 🔐 Default Credentials

### ⭐ Admin Login (Restricted Access)
- **URL:** http://localhost:5000/auth/admin-login
- **Email:** `AdminAR@gmail.com`
- **Password:** `AshishRajesh`
- **Access:** Private credentials for authorized use only
- **How to Access:** 
  - Admin login is hidden from the homepage for security
  - Press **`Ctrl+Shift+A`** on the homepage to reveal the Admin Portal card
  - Alternatively, navigate directly to: `http://localhost:5000/auth/admin-login`

### Sample User Logins
- **URL:** http://localhost:5000/auth/login
- **Emails:** john@example.com, jane@example.com, alice@example.com, etc.
- **Password:** `password123` (for all users)

## 📊 Database Configuration

### Development (SQLite)
Default configuration uses SQLite database located at `ems_dev.db`:
```python
SQLALCHEMY_DATABASE_URI = 'sqlite:///ems_dev.db'
```

### Production (MySQL)
Switch to MySQL by:

#### Step 1: Create Database
```bash
mysql -u root -p
CREATE DATABASE ems_production;
CREATE USER 'ems_user'@'localhost' IDENTIFIED BY 'secure_password';
GRANT ALL PRIVILEGES ON ems_production.* TO 'ems_user'@'localhost';
FLUSH PRIVILEGES;
```

#### Step 2: Create .env File
```env
FLASK_ENV=production
DATABASE_URL=mysql+pymysql://ems_user:secure_password@localhost/ems_production
SECRET_KEY=your-secret-key-here
```

#### Step 3: Run with Production Config
```bash
set FLASK_ENV=production  # Windows
export FLASK_ENV=production  # macOS/Linux
python run.py
```

## 📖 User Guide

### Homepage Features
- **Hero Section:** Welcome banner with system tagline
- **Features Grid:** Quick overview of system capabilities
- **System Overview:** Real-time statistics showing active events and users
- **Why Choose Our System:** Highlights of key features including speed, security, analytics, and QR code support
- **Login Section:** Quick access to user registration and login

### For Regular Users

1. **Register Account**
   - Navigate to `/auth/register`
   - Fill in name, email, phone, and password
   - Submit to create account

2. **Browse Events**
   - Go to `/user/events`
   - View all available events
   - Use search to filter by name or venue

3. **Register for Event**
   - Click on event card
   - View event details
   - Click "Register Now" button
   - Automatically generates QR code ticket

4. **Download Ticket**
   - Go to `/user/my-tickets`
   - Click "Download Ticket" for QR code
   - Use QR code for event entry

5. **Manage Profile**
   - Click on user menu (top right)
   - Select "Profile"
   - Update name and phone number

### For Administrators

1. **Admin Dashboard**
   - Login at `/auth/admin-login`
   - View statistics: Users, Events, Registrations
   - See recent activities

2. **Create Event**
   - Click "+ Create Event"
   - Fill in event details
   - Upload event poster image
   - Set capacity
   - Submit

3. **Manage Events**
   - View all events in table
   - Edit event details
   - Delete events (also removes registrations)
   - Search and filter events

4. **Manage Users**
   - View all registered users
   - See user registration count
   - Delete users
   - Search by name or email

5. **View Statistics**
   - Registration count by event
   - System-wide metrics
   - Conversion rates

## 🛡️ Security Features

- **Password Hashing:** bcrypt with salting
- **Session Management:** Flask-Login with secure cookies
- **CSRF Protection:** Built-in Flask protection
- **SQL Injection Prevention:** SQLAlchemy parameterized queries
- **Access Control:** Role-based decorators
- **Duplicate Prevention:** Unique constraints in database

## 📝 Important Notes

### File Uploads
- Event images are saved to `app/static/uploads/`
- QR codes are saved to `app/static/qrcodes/`
- Maximum file size: 16MB
- Accepted formats: PNG, JPG, JPEG, GIF

### Database Relationships
- Users have many Registrations
- Events have many Registrations
- Registrations have unique constraint on (user_id, event_id)

### Password Requirements
- Minimum 6 characters
- No special character requirements
- Hashed using Flask-Bcrypt

## 🔧 Configuration Details

### config.py
- **DevelopmentConfig:** SQLite, Debug=True
- **ProductionConfig:** MySQL, Debug=False
- **TestingConfig:** In-memory SQLite for testing

### app/__init__.py
Implements:
- Application Factory Pattern
- Blueprint registration
- Extension initialization
- Error handlers
- Database table creation

## 📚 Database Models

### User
```python
- id (Integer, Primary Key)
- name (String)
- email (String, Unique)
- phone (String)
- password_hash (String)
- created_at (DateTime)
- registrations (Relationship)
```

### Admin
```python
- id (Integer, Primary Key)
- username (String, Unique)
- password_hash (String)
- created_at (DateTime)
```

### Event
```python
- id (Integer, Primary Key)
- event_name (String)
- event_date (Date)
- event_time (Time)
- venue (String)
- description (Text)
- image_filename (String)
- capacity (Integer)
- created_at (DateTime)
- updated_at (DateTime)
- registrations (Relationship)
```

### Registration
```python
- id (Integer, Primary Key)
- user_id (Integer, Foreign Key)
- event_id (Integer, Foreign Key)
- registration_date (DateTime)
- qr_code_filename (String)
- Constraint: Unique(user_id, event_id)
```

## 🐛 Troubleshooting

### Virtual Environment Issues
```bash
# If activation fails
python -m venv --upgrade venv

# Verify activation
python -c "import sys; print(sys.prefix)"
```

### Database Issues
```bash
# Reset database (development only)
del ems_dev.db
python seed_data.py

# Check SQLite database
sqlite3 ems_dev.db ".tables"
```

### Port Already in Use
```bash
# Run on different port
python -c "from run import app; app.run(port=5001)"
```

### Image Upload Issues
```bash
# Ensure directories exist and are writable
mkdir -p app/static/uploads
mkdir -p app/static/qrcodes
chmod 755 app/static/uploads
chmod 755 app/static/qrcodes
```

## 📖 Complete Documentation

For detailed information about:
- System Architecture
- Entity-Relationship Diagrams
- Data Flow Diagrams
- API Documentation
- Future Enhancements

See **DOCUMENTATION.md** file.

## 📋 Sample Data

After running `seed_data.py`:

### Users (8 total)
- john@example.com
- jane@example.com
- alice@example.com
- bob@example.com
- carol@example.com
- david@example.com
- emma@example.com
- frank@example.com

**All users have password:** `password123`

### Events (6 total)
1. Python Workshop (10 days from today)
2. Web Development Bootcamp (17 days from today)
3. Data Science Seminar (24 days from today)
4. Cloud Computing Conference (31 days from today)
5. AI & Machine Learning Expo (38 days from today)
6. Cybersecurity Workshop (45 days from today)

## 🎨 UI/UX Features

- **Bootstrap 5:** Responsive design
- **Custom CSS:** Professional styling
- **Toast Notifications:** User feedback
- **Loading States:** Visual feedback
- **Pagination:** Efficient data display
- **Search & Filter:** Easy navigation
- **Modal Dialogs:** Confirmation actions

## 🔄 Workflow

### User Registration Flow
1. Register → 2. Verify email uniqueness → 3. Hash password → 4. Save to DB → 5. Redirect to login

### Event Registration Flow
1. Login → 2. Browse events → 3. Check capacity → 4. Verify no duplicates → 5. Create registration → 6. Generate QR → 7. Show ticket

### Admin Event Creation Flow
1. Login (admin) → 2. Create event → 3. Upload image → 4. Set capacity → 5. Save to DB → 6. Manage registrations

## 📊 Testing Scenarios

### Test User Registration
1. Go to `/auth/register`
2. Enter: Name: "Test User", Email: "test@test.com", Password: "test123"
3. Verify redirect to login page

### Test Event Registration
1. Login as user
2. Go to `/user/events`
3. Click event
4. Click "Register Now"
5. Verify appears in `/user/my-tickets`

### Test Admin Functions
1. Login as admin
2. Create event with image
3. Edit event details
4. Monitor registrations
5. View statistics

## 🚀 Deployment in Production

### Using Gunicorn
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

### Using Docker
```dockerfile
FROM python:3.11
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "run:app"]
```

### Environment Variables
```bash
FLASK_ENV=production
SECRET_KEY=your-secure-key
DATABASE_URL=mysql+pymysql://user:password@host/dbname
```

## 📞 Support & Maintenance

### Log Locations
- Application logs: Console output
- Error logs: Flask error handlers
- Database logs: MySQL logs

### Backup
```bash
# SQLite backup
cp ems_dev.db ems_dev.db.backup

# MySQL backup
mysqldump -u user -p ems_production > backup.sql
```

## 📄 License

This project is for educational purposes.

## 👥 Author

**Development Team**  
TYBSc Computer Science - Major Project  
Year: 2026

## 📅 Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | Feb 2026 | Initial Release |

---

**Built with ❤️ using Flask and Python**

For issues or questions, refer to DOCUMENTATION.md for detailed information.
#   U P D A T E S _ E M S  
 