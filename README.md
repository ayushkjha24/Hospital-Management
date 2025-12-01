# Hospital Management System

A comprehensive system for managing hospital operations, including patient, doctor, and appointment management. This project is built with a modern web stack, featuring a Vue.js frontend and a Python (Flask) backend.

## Features

*   **Role-based access control:** Separate interfaces for Patients, Doctors, and Admins.
*   **Patient Management:** Patients can register, book appointments, view their medical history, and manage their profile.
*   **Doctor Management:** Doctors can manage their availability, view upcoming appointments, and update patient medical records.
*   **Admin Dashboard:** Admins can manage doctors, patients, departments, and view system-wide statistics.
*   **Appointment Scheduling:** Patients can book appointments with doctors based on their availability.
*   **Asynchronous Tasks:** Celery is used for background tasks like sending reminders and generating reports.

## Project Structure

The project is divided into two main parts:

### `backend`

*   **Framework:** Flask
*   **Database:** SQLAlchemy with Flask-Migrate for migrations.
*   **Asynchronous Tasks:** Celery with Redis/RabbitMQ.
*   **Structure:**
    *   `main.py`: The main entry point for the Flask application.
    *   `controller/`: Contains the core application logic.
        *   `routes.py`: Defines the API endpoints.
        *   `models.py`: SQLAlchemy database models.
        *   `auth.py`: Handles authentication and authorization.
        *   `jobs/`: Contains Celery tasks.
    *   `migrations/`: Database migration scripts.

### `frontend`

*   **Framework:** Vue.js with Vite
*   **Routing:** Vue Router
*   **State Management:** Pinia
*   **Structure:**
    *   `src/`: Contains the main source code.
        *   `main.js`: The entry point for the Vue application.
        *   `App.vue`: The root Vue component.
        *   `router/`: Defines the application routes.
        *   `stores/`: Pinia stores for state management.
        *   `views/`: Vue components for different pages, organized by role (admin, doctor, patient).
        *   `api/`: Functions for making API calls to the backend.

## Getting Started

### Prerequisites

*   Python 3.8+
*   Node.js 14+
*   A running instance of Redis for Celery.

### Backend Setup

1.  Navigate to the `backend` directory:
    ```bash
    cd backend
    ```
2.  Create and activate a virtual environment:
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```
3.  Install the dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4.  Initialize the database:
    ```bash
    python main.py
    ```
5.  In a separate terminal, run the Celery worker:
    ```bash
    celery -A celery_app.celery worker --loglevel=info
    ```

### Frontend Setup

1.  Navigate to the `frontend` directory:
    ```bash
    cd frontend
    ```
2.  Install the dependencies:
    ```bash
    npm install
    ```
3.  Run the development server:
    ```bash
    npm run dev
    ```

### 🚀 Starting Flask, Celery Worker & Celery Beat
# 1️⃣ Activate your virtual environment
```
source .venv/bin/activate
```

# 2️⃣ Start Flask API (Terminal 1)
```
python main.py
```

# 3️⃣ Start Celery Worker (Terminal 2)
```
celery -A celery_app.celery worker --loglevel=info
```

# 4️⃣ Start Celery Beat Scheduler (Terminal 3)
```
celery -A celery_app.celery beat --loglevel=info
```

### ⚡ Run Worker + Beat Together (Development Only)
```
celery -A celery_app.celery worker --beat --loglevel=info
```

## Technologies Used

*   **Backend:** Python, Flask, SQLAlchemy, Celery
*   **Frontend:** Vue.js, Vite, Vue Router, Pinia
*   **Database:** SQLite
*   **Task Queue:** Redis


### Problems that I have faced 

- Migration problem
- Task scheduling 
- Circular import in db
- Improper Project structure
- Authentication and Authorization challenges
- Vue API communication issues
- And Many more....