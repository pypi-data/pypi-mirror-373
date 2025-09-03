import time
import traceback
import importlib
from datetime import datetime
from functools import wraps

from wedeliver_core_plus import WedeliverCorePlus
from wedeliver_core_plus.helpers.enums import TaskExecutionStatus
from wedeliver_core_plus.helpers.kafka_producers.notification_center import send_notification_message


def task_execution_tracker(task_name, task_file_path):
    """
    Decorator to track task execution and send Slack notifications.
    
    This decorator:
    - Records task execution in the database
    - Sends Slack notifications on success/failure
    - Handles error logging and reporting
    - Updates task execution tracking
    
    Args:
        task_name (str): Name of the task being executed
        task_file_path (str): Path to the task file
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            app = WedeliverCorePlus.get_app()
            db = app.extensions['sqlalchemy'].db
            
            # Import TaskExecution model
            from app.models import TaskExecution
            
            # Check if task has already been executed
            existing_task = db.session.query(TaskExecution).filter(
                TaskExecution.task_name == task_name,
                TaskExecution.execution_status == TaskExecutionStatus.SUCCESS.value
            ).first()
            
            if existing_task:
                app.logger.info(f"Task {task_name} has already been executed successfully. Skipping.")
                return f"Task {task_name} already executed on {existing_task.execution_end_time}"
            
            # Create or update task execution record
            task_execution = db.session.query(TaskExecution).filter(
                TaskExecution.task_name == task_name
            ).first()

            if not task_execution:
                # Check if the task module has a revert function
                is_revertible = _check_task_revertible(task_file_path)

                task_execution = TaskExecution(
                    task_name=task_name,
                    task_file_path=task_file_path,
                    is_revertible=is_revertible
                )
                db.session.add(task_execution)
            else:
                # Update revertible status for existing tasks
                is_revertible = _check_task_revertible(task_file_path)
                task_execution.is_revertible = is_revertible
            
            # Update execution status and start time
            task_execution.execution_status = TaskExecutionStatus.RUNNING.value
            task_execution.execution_start_time = datetime.now()
            task_execution.error_message = None
            task_execution.result_message = None
            
            db.session.commit()
            
            start_time = time.time()
            
            try:
                app.logger.info(f"Starting execution of task: {task_name}")
                
                # Execute the task
                result = func(*args, **kwargs)
                
                # Calculate execution time
                end_time = time.time()
                execution_duration = end_time - start_time
                
                # Update task execution record with success
                task_execution.execution_status = TaskExecutionStatus.SUCCESS.value
                task_execution.execution_end_time = datetime.now()
                task_execution.execution_duration_seconds = execution_duration
                task_execution.result_message = str(result) if result else "Task completed successfully"
                
                db.session.commit()
                
                # Send success notification to Slack
                _send_success_notification(task_name, execution_duration, result, task_execution.is_revertible)
                
                app.logger.info(f"Task {task_name} completed successfully in {execution_duration:.2f} seconds")
                
                return result
                
            except Exception as e:
                # Calculate execution time
                end_time = time.time()
                execution_duration = end_time - start_time
                
                # Update task execution record with failure
                task_execution.execution_status = TaskExecutionStatus.FAILED.value
                task_execution.execution_end_time = datetime.now()
                task_execution.execution_duration_seconds = execution_duration
                task_execution.error_message = str(e)
                task_execution.result_message = "Task failed with error"
                
                db.session.commit()
                
                # Send failure notification to Slack
                _send_failure_notification(task_name, execution_duration, e)
                
                app.logger.error(f"Task {task_name} failed after {execution_duration:.2f} seconds: {str(e)}")
                
                # Re-raise the exception
                raise e
        
        return wrapper
    return decorator


def _send_success_notification(task_name, execution_duration, result, is_revertible=False):
    """Send Slack notification for successful task execution"""
    try:
        message = f"✅ **Database Task Completed Successfully**\n\n"
        message += f"**Task:** {task_name}\n"
        message += f"**Duration:** {execution_duration:.2f} seconds\n"
        message += f"**Result:** {str(result)[:500] if result else 'Task completed successfully'}\n"

        if is_revertible:
            message += f"\n🔄 **Reversion Available:** To revert changes: `flask task revert {task_name}`"

        send_notification_message(
            title="Database Task Success",
            message=message,
            channel="database-tasks",
            emoji=":white_check_mark:",
            color="#36a64f"
        )
    except Exception as e:
        app = WedeliverCorePlus.get_app()
        app.logger.error(f"Failed to send success notification for task {task_name}: {str(e)}")


def _send_failure_notification(task_name, execution_duration, error):
    """Send Slack notification for failed task execution"""
    try:
        message = f"❌ **Database Task Failed**\n\n"
        message += f"**Task:** {task_name}\n"
        message += f"**Duration:** {execution_duration:.2f} seconds\n"
        message += f"**Error:** {str(error)[:500]}\n"
        message += f"**Traceback:**\n```\n{traceback.format_exc()[:1000]}\n```"
        
        send_notification_message(
            title="Database Task Failure",
            message=message,
            channel="database-tasks",
            emoji=":x:",
            color="#ff0000"
        )
    except Exception as e:
        app = WedeliverCorePlus.get_app()
        app.logger.error(f"Failed to send failure notification for task {task_name}: {str(e)}")


def _check_task_revertible(task_file_path: str) -> bool:
    """
    Check if a task module has a revert function.

    Args:
        task_file_path (str): Path to the task file

    Returns:
        bool: True if task has a revert function, False otherwise
    """
    try:
        # Convert file path to module path
        module_path = task_file_path.replace('/', '.').replace('.py', '')

        # Import the task module
        task_module = importlib.import_module(module_path)

        # Check if revert function exists
        return hasattr(task_module, 'revert')

    except Exception as e:
        app = WedeliverCorePlus.get_app()
        app.logger.warning(f"Failed to check if task is revertible: {e}")
        return False
