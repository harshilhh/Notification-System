from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from models.schema import  db
from dotenv import load_dotenv
from celery import Celery
from celery.schedules import crontab
import os

# Initialize Flask app
app = Flask(__name__)

load_dotenv()
# Redis configuration
redis_password = os.getenv("REDIS_PASSWORD")
redis_host = os.getenv("REDIS_HOST")
redis_port = os.getenv("REDIS_PORT")
redis_db = os.getenv("REDIS_DB")
# PostgreSQL configuration
postgres_user = os.getenv("POSTGRES_USER")
postgres_password = os.getenv("POSTGRES_PASSWORD")
postgres_host = os.getenv("POSTGRES_HOST")
postgres_db = os.getenv("POSTGRES_DB")

# Initialize Celery
celery = Celery(
    app,
    broker=f'redis://:{redis_password}@{redis_host}:{redis_port}/{redis_db}',
    backend=f'db+postgresql://{postgres_user}:{postgres_password}@{postgres_host}/{postgres_db}'
)
celery.conf.beat_schedule = {
    'send-task-deadline-notifications-every-minute': {
        'task': 'utils.helper_functions.send_task_deadline_notifications',
        'schedule': crontab(minute='*/1'),  # Run every minute
    },
}
celery.conf.timezone = 'UTC'


def create_app():
    # Database configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{postgres_user}:{postgres_password}@{postgres_host}/{postgres_db}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # Celery configuration
    celery.conf.update(
        broker_connection_retry_on_startup=True  
    )
    # Initialize database
    db.init_app(app)
    # Register blueprints
    from models.schema import core_models
    app.register_blueprint(core_models)
    from api.routes import core_api
    app.register_blueprint(core_api)

    return app


