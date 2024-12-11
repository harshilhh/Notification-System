# Notification System for Task Deadlines

This project is a Flask-based notification system that sends task reminders using Celery and Twilio. It integrates Redis for task queues and PostgreSQL for database management.

## Setup Instructions

### 1. Add the `.env` File
Create a `.env` file in the root directory and add the following configuration:

#### Redis Configuration
```
REDIS_PASSWORD=maisha123
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
```

#### PostgreSQL Configuration
```
POSTGRES_USER=testing_owner
POSTGRES_PASSWORD=kUx9pEc6CIPn
POSTGRES_HOST=ep-lucky-base-a1q3quci.ap-southeast-1.aws.neon.tech
POSTGRES_PORT=5432
POSTGRES_DB=testing
```

#### Twilio Configuration
```
TWILIO_ACCOUNT_SID=<your-account-sid>
TWILIO_AUTH_TOKEN=<your-auth-token>
TWILIO_PHONE_NUMBER=+18133363271
TWILIO_WHATSAPP_NUMBER=+14155238886
```

### 2. Create a Virtual Environment and Install Requirements
1. Create a virtual environment:
   ```bash
   python3 -m venv venv
   ```

2. Activate the virtual environment:
   - On Linux/macOS:
     ```bash
     source venv/bin/activate
     ```
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```

3. Install all required libraries from `requirements.txt`:
   ```bash
   pip install -r requirements.txt
   ```

### 3. Run the Flask Application
In the first terminal, run the Flask application:
```bash
python3 run.py
```

### 4. Create the Database Tables
Send a `POST` request to the following endpoint to create the required database tables:
```
http://localhost:5000/create-db
```

You can use tools like Postman or `curl` to make the request.

### 5. Start the Celery Worker
In the second terminal, start the Celery worker with the following command:
```bash
celery -A celery_worker.celery worker --concurrency=4 -l info
```

### 6. Start the Celery Beat Scheduler
In the third terminal, start the Celery beat scheduler to run periodic tasks:
```bash
celery -A app.celery beat --loglevel=info
```

### 7. Start Celery Flower
In the fourth terminal, run Flower to monitor Celery tasks:
```bash
celery -A celery_worker.celery flower
```

This will provide a web-based monitoring tool where you can track task failures, retries, successes, and worker activity.

## Endpoints

### Create Database Tables
**URL:** `http://localhost:5000/create-db`  
**Method:** `POST`

## Notes
- Ensure that Redis and PostgreSQL are properly set up and running before starting the application.
- Keep the `.env` file secure as it contains sensitive credentials.
- Use a virtual environment to manage dependencies and avoid conflicts with global Python packages.

## Monitoring
Use Flower to monitor the status of Celery tasks and workers:
- Access Flower at `http://localhost:5555` (default port).

