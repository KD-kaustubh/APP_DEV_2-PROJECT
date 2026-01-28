# Vehicle Parking Management System

A comprehensive web application for managing parking lots, tracking vehicle reservations, and automating billing processes with real-time occupancy monitoring.

## 📋 Overview

This full-stack application provides a complete parking management solution with role-based access control (admin/user), automated reporting, and real-time parking spot availability tracking. The system handles vehicle reservations, calculates parking costs based on duration, processes payments, and generates monthly activity reports for users.

## ✨ Features

### User Features
- **User Authentication & Authorization**: Secure registration and login with role-based access control
- **Parking Spot Reservation**: Browse available parking lots and reserve spots in real-time
- **Vehicle Management**: Log vehicle details and track entry/exit times
- **Payment Processing**: Automated billing based on parking duration with payment status tracking
- **Activity Reports**: Receive monthly email reports with reservation history and spending analytics
- **Dashboard**: View reservation history, active bookings, and spending summaries

### Admin Features
- **Parking Lot Management**: Create, update, and delete parking lot locations
- **Real-time Monitoring**: Track parking occupancy across all lots
- **User Management**: View and manage registered users
- **Spot Management**: Configure and manage individual parking spots
- **Analytics**: Generate CSV reports with user activity and revenue data
- **Payment Oversight**: Monitor all transactions and payment statuses

### System Features
- **Real-time Availability**: Instant updates on parking spot status (Available/Occupied)
- **Automated Scheduling**: Celery-based background tasks for reminders and reports
- **Redis Caching**: Optimized API performance with intelligent caching
- **Email Notifications**: Automated monthly reports and daily reminders
- **RESTful API**: Well-structured API endpoints for all operations

## 🛠️ Technologies Used

### Backend
- **Python 3.x**: Core programming language
- **Flask**: Web framework for REST API development
- **Flask-RESTful**: RESTful API extension
- **Flask-Security-Too**: Authentication and authorization
- **SQLAlchemy**: ORM for database operations
- **Celery**: Asynchronous task queue for scheduled jobs
- **Redis**: Message broker and caching layer
- **SQLite**: Database for development

### Frontend
- **HTML5 & CSS3**: Structure and styling
- **JavaScript (ES6+)**: Client-side functionality
- **Vue.js Components**: Reactive UI components

### Additional Libraries
- **Flask-Caching**: Response caching for performance
- **Jinja2**: Template engine for email reports
- **Passlib & Bcrypt**: Password hashing and security

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- Redis server
- pip (Python package manager)

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/vehicle-parking-app.git
   cd vehicle-parking-app
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables** (optional)
   Create a `.env` file or configure in your environment:
   ```
   FLASK_APP=app.py
   FLASK_ENV=development
   SECRET_KEY=your-secret-key
   ```

5. **Initialize the database**
   ```bash
   python app.py
   ```
   The application will automatically create the database and default roles.

6. **Start Redis server**
   ```bash
   redis-server
   ```

## 🚀 Usage

### Running the Application

1. **Start the Flask server**
   ```bash
   python app.py
   ```
   The application will be available at `http://localhost:5000`

2. **Start Celery worker** (in a separate terminal)
   ```bash
   celery -A app.celery_app worker --loglevel=info
   ```

3. **Start Celery beat scheduler** (in a separate terminal)
   ```bash
   celery -A app.celery_app beat --loglevel=info
   ```

### Default Admin Access
After first run, create an admin user through the application or modify the database directly.

## 📁 Project Structure

```
vehicle-parking-app/
├── app.py                          # Application entry point
├── celery_config.py               # Celery configuration
├── requirements.txt               # Python dependencies
├── application/
│   ├── __init__.py               # Application initialization
│   ├── celery_init.py            # Celery app setup
│   ├── celery_schedule.py        # Periodic task configuration
│   ├── config.py                 # Flask configuration
│   ├── database.py               # Database setup
│   ├── mail.py                   # Email utilities
│   ├── models.py                 # Database models
│   ├── resources.py              # RESTful API endpoints
│   ├── routes.py                 # Flask routes
│   ├── task.py                   # Celery tasks
│   └── utilis.py                 # Helper functions
├── static/
│   ├── script.js                 # Main JavaScript file
│   └── components/               # Vue.js components
│       ├── Dashboard.js
│       ├── Home.js
│       ├── Login.js
│       ├── Register.js
│       └── UsersList.js
├── templates/
│   ├── index.html                # Main template
│   └── monthly_report.html       # Email report template
└── instance/
    └── vpa.sqlite3               # SQLite database
```

## 🔌 API Endpoints

### Authentication
- `POST /api/login` - User login
- `POST /api/register` - User registration

### Parking Lots (Admin)
- `GET /api/parking-lots` - List all parking lots
- `POST /api/parking-lots` - Create parking lot
- `PUT /api/parking-lots/<id>` - Update parking lot
- `DELETE /api/parking-lots/<id>` - Delete parking lot

### Reservations
- `GET /api/reservations` - User's reservations
- `POST /api/reservations` - Create reservation
- `PUT /api/reservations/<id>` - Update reservation
- `DELETE /api/reservations/<id>` - Cancel reservation

### Payments
- `GET /api/payments` - Payment history
- `POST /api/payments` - Process payment

### Reports (Admin)
- `GET /api/reports/activity` - Generate activity report

## 📧 Scheduled Tasks

- **Daily Reminders**: Sent at 20:08 IST daily
- **Monthly Reports**: Generated and emailed at 20:08 IST daily (configurable)

## 🔒 Security Features

- Password hashing with Bcrypt
- Token-based authentication
- Role-based access control (RBAC)
- SQL injection protection via ORM
- CSRF protection

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

IIT Madras - Modern Application Development 2 Project

## 🙏 Acknowledgments

- Flask community for excellent documentation
- Celery for robust task scheduling
- IIT Madras for project guidance
