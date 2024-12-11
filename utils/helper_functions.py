from twilio.rest import Client
from app import celery
from datetime import datetime, timedelta
from models.schema import Task,db
import os
from dotenv import load_dotenv

load_dotenv()

account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
twilio_phone_number = os.getenv("TWILIO_PHONE_NUMBER")
twilio_whatsapp_number = os.getenv("TWILIO_WHATSAPP_NUMBER")

   

# Create a client
client = Client(account_sid, auth_token)


@celery.task
def celerymytesting(name="utils.helper_functions.celerymytesting"):
    # Simulate some work
    return "Task completed"



# Function to send SMS
@celery.task(name="utils.helper_functions.send_sms", max_retries=3, default_retry_delay=60)
def send_sms_notification(to_number, message_body):
    try:
        message = client.messages.create(
            body=message_body,              
            from_=twilio_phone_number,           
            to=to_number                    
        )
        print(f"SMS sent successfully. SID: {message.sid}")
    except Exception as e:
        raise send_sms_notification.retry(exc=e, countdown=2**send_sms_notification.request.retries)


# Function to send WhatsApp message
@celery.task(name="utils.helper_functions.send_whatsapp", max_retries=3, default_retry_delay=60)
def send_whatsapp_notification(to_number, message_body):
    try:
        message = client.messages.create(
            body=message_body,                    
            from_=f'whatsapp:{twilio_whatsapp_number}',         
            to=f'whatsapp:{to_number}'             
        )
        print(f"WhatsApp message sent successfully. SID: {message.sid}")
    except Exception as e:
        raise send_whatsapp_notification.retry(exc=e, countdown=2**send_whatsapp_notification.request.retries)
        



@celery.task(name="utils.helper_functions.send_task_deadline_notifications")
def send_task_deadline_notifications():
    try:
        # Get the current time
        now = datetime.now()

        # Get all tasks from the database
        tasks = Task.query.all()

        for task in tasks:
            if task.notification_sent:
                continue

            # Calculate the time difference between the deadline and now
            deadline = task.due_date
            time_difference = deadline - now
            # Check if the deadline is within 30 minutes
            if timedelta(minutes=0) <= time_difference <= timedelta(minutes=30):
                # Prepare the notification messages
                sms_message = f"Reminder: Your task '{task.title}' is due in 30 minutes."
                whatsapp_message = f"Hello! Your task '{task.title}' is due in 30 minutes. Don't forget to complete it."

                # Send SMS and WhatsApp notifications
                send_sms_notification.apply_async(args=[task.user_phone, sms_message])
                send_whatsapp_notification.apply_async(args=[task.user_phone, whatsapp_message])

                task.notification_sent = True
                db.session.commit()

                print(f"Notification sent to {task.user_phone} for task {task.title}.")
    except Exception as e:
        print(f"Error checking task deadlines: {str(e)}")


@celery.task(name="utils.helper_functions.send_task_deadline_reminder")
def send_task_deadline_reminder():
    try:
        # Get the current time
        now = datetime.now()

        tasks = Task.query.filter(Task.due_date > now).all()

        for task in tasks:
            message_body = f"Reminder: Your task '{task.title}' is due soon! Deadline: {task.due_date.strftime('%Y-%m-%d %H:%M:%S')}"
            send_whatsapp_notification.apply_async(args=[task.user_phone, message_body])  # Send WhatsApp reminder

        return {"message": "Reminders sent for tasks with upcoming deadlines."}
    except Exception as e:
        print(f"Error sending reminders: {e}")
        return {"error": str(e)}



    