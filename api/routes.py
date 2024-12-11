
from flask import Blueprint, request, jsonify
from models.schema import db, Task
from utils.helper_functions import send_sms_notification ,send_whatsapp_notification ,celerymytesting,send_task_deadline_reminder

core_api = Blueprint('core_api', __name__)


@core_api.route('/create-db', methods=['POST'])
def create_db():
    try:
        db.create_all()
        return {"message": "Database created successfully."}, 200
    except Exception as e:
        return {"error": str(e)}, 500


# Create a new task
@core_api.route('/tasks', methods=['POST'])
def create_task():
    data = request.get_json()
    try:
        task = Task(
            title=data['title'],
            description=data.get('description', ''),
            due_date=data['due_date'],
            user_phone=data['user_phone']
        )
        db.session.add(task)
        db.session.commit()
        # Send SMS and WhatsApp notifications
        sms_message = f"Task created successfully: {task.title}. Due date: {task.due_date}"
        whatsapp_message = f"Hello! You have a new task: {task.title}. Due date: {task.due_date}"

        send_sms_notification.apply_async(args=[task.user_phone, sms_message])
        send_whatsapp_notification.apply_async(args=[task.user_phone, whatsapp_message])

        return jsonify({
            "message": "Task created successfully.",
            "task": {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "due_date": task.due_date,
                "user_phone": task.user_phone
            }
        }), 201
    except Exception as e:
        return {"error": str(e)}, 400

# Read all tasks
@core_api.route('/tasks', methods=['GET'])
def get_tasks():
    try:
        tasks = Task.query.all()
        tasks_list = [
            {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "due_date": task.due_date,
                "user_phone": task.user_phone
            } for task in tasks
        ]
        return jsonify(tasks_list), 200
    except Exception as e:
        return {"error": str(e)}, 500

# Read a single task
@core_api.route('/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    try:
        task = Task.query.get_or_404(task_id)
        return jsonify({
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "due_date": task.due_date,
            "user_phone": task.user_phone
        }), 200
    except Exception as e:
        return {"error": str(e)}, 404

@core_api.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    data = request.get_json()
    try:
        # Fetch the task from the database
        task = Task.query.get_or_404(task_id)

        # Update task fields
        task.title = data.get('title', task.title)
        task.description = data.get('description', task.description)
        task.due_date = data.get('due_date', task.due_date)
        task.user_phone = data.get('user_phone', task.user_phone)

        # Commit the changes to the database
        db.session.commit()

        # Prepare the SMS and WhatsApp messages
        sms_message = f"Task updated successfully: {task.title}. New due date: {task.due_date}"
        whatsapp_message = f"Hello! Your task '{task.title}' has been updated. New due date: {task.due_date}"

        # Send the notifications asynchronously using Celery
        send_sms_notification.apply_async(args=[task.user_phone, sms_message])
        send_whatsapp_notification.apply_async(args=[task.user_phone, whatsapp_message])

        # Return success message along with updated task details
        return jsonify({
            "message": "Task updated successfully.",
            "task": {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "due_date": task.due_date,
                "user_phone": task.user_phone
            }
        }), 200
    except Exception as e:
        return {"error": str(e)}, 400

# Delete a task
@core_api.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    try:
        task = Task.query.get_or_404(task_id)
        db.session.delete(task)
        db.session.commit()
        return jsonify({"message": "Task deleted successfully."}), 200
    except Exception as e:
        return {"error": str(e)}, 500



@core_api.route('/reminder', methods=['GET'])
def testing():
    send_task_deadline_reminder.apply_async()
    return {"message": "Reminders sent for tasks with upcoming deadlines."}




