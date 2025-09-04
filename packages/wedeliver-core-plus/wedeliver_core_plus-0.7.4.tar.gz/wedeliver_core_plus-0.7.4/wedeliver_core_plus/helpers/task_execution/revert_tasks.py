"""
Task reversion module for database seeding tasks.

This module provides functionality to revert the effects of successfully executed
database seeding tasks, allowing developers to undo changes when needed.
"""

import time
import traceback
import importlib
from datetime import datetime
from typing import Dict, Any

from wedeliver_core_plus import WedeliverCorePlus
from wedeliver_core_plus.helpers.enums import TaskExecutionStatus, TaskReversionStatus
from wedeliver_core_plus.helpers.kafka_producers.notification_center import send_notification_message


def revert_task(task_name: str, tasks_directory: str = "app/scripts/__tasks__") -> Dict[str, Any]:
    """
    Revert a successfully executed database seeding task.
    
    This function:
    1. Validates the task exists and was successfully executed
    2. Checks the task is marked as revertible
    3. Imports the task module and calls its revert() function
    4. Updates database with reversion status and timing
    5. Sends Slack notifications about reversion results
    
    Args:
        task_name (str): Name of the task to revert (e.g., "202507151200_sample_task")
        tasks_directory (str): Directory where task files are stored
        
    Returns:
        Dict[str, Any]: Reversion result with status and details
        
    Raises:
        ValueError: If task doesn't exist, wasn't executed, or isn't revertible
        Exception: If reversion fails
    """
    app = WedeliverCorePlus.get_app()
    db = app.extensions['sqlalchemy'].db
    
    # Import TaskExecution model
    from app.models import TaskExecution
    
    app.logger.info(f"Starting reversion of task: {task_name}")
    
    # Find the task execution record
    task_execution = db.session.query(TaskExecution).filter(
        TaskExecution.task_name == task_name
    ).first()
    
    if not task_execution:
        raise ValueError(f"Task '{task_name}' not found in execution history")
    
    # Validate task was successfully executed
    if task_execution.execution_status != TaskExecutionStatus.SUCCESS.value:
        raise ValueError(f"Task '{task_name}' was not successfully executed (status: {task_execution.execution_status})")
    
    # Check if task is revertible
    if not task_execution.is_revertible:
        raise ValueError(f"Task '{task_name}' is not marked as revertible")
    
    # Check if task has already been reverted
    if task_execution.reversion_status == TaskReversionStatus.SUCCESS.value:
        raise ValueError(f"Task '{task_name}' has already been successfully reverted")
    
    # Find the task module file
    task_module_path = _find_task_module_path(task_name, tasks_directory)
    if not task_module_path:
        raise ValueError(f"Task module file not found for '{task_name}'")
    
    # Update reversion status to pending
    task_execution.reversion_status = TaskReversionStatus.PENDING.value
    task_execution.reversion_time = datetime.now()
    db.session.commit()
    
    start_time = time.time()
    
    try:
        # Import the task module
        module_path = task_module_path.replace('/', '.').replace('.py', '')
        task_module = importlib.import_module(module_path)
        
        # Check if revert function exists
        if not hasattr(task_module, 'revert'):
            raise ValueError(f"Task module '{module_path}' does not have a 'revert' function")
        
        revert_function = getattr(task_module, 'revert')
        
        app.logger.info(f"Executing reversion function for task: {task_name}")
        
        # Execute the reversion
        result = revert_function()
        
        # Calculate reversion time
        end_time = time.time()
        reversion_duration = end_time - start_time
        
        # Update task execution record with success
        task_execution.reversion_status = TaskReversionStatus.SUCCESS.value
        task_execution.reversion_duration_seconds = reversion_duration
        task_execution.reversion_message = str(result) if result else "Task reverted successfully"
        
        db.session.commit()
        
        # Send success notification to Slack
        _send_reversion_success_notification(task_name, reversion_duration, result)
        
        app.logger.info(f"Task {task_name} reverted successfully in {reversion_duration:.2f} seconds")
        
        return {
            'status': 'success',
            'task_name': task_name,
            'reversion_duration': reversion_duration,
            'result': str(result) if result else "Task reverted successfully"
        }
        
    except Exception as e:
        # Calculate reversion time
        end_time = time.time()
        reversion_duration = end_time - start_time
        
        # Update task execution record with failure
        task_execution.reversion_status = TaskReversionStatus.FAILED.value
        task_execution.reversion_duration_seconds = reversion_duration
        task_execution.reversion_message = str(e)
        
        db.session.commit()
        
        # Send failure notification to Slack
        _send_reversion_failure_notification(task_name, reversion_duration, e)
        
        app.logger.error(f"Task {task_name} reversion failed after {reversion_duration:.2f} seconds: {str(e)}")
        
        return {
            'status': 'failed',
            'task_name': task_name,
            'reversion_duration': reversion_duration,
            'error': str(e)
        }


def _find_task_module_path(task_name: str, tasks_directory: str) -> str:
    """
    Find the module path for a task by its name.
    
    Args:
        task_name (str): Task name (e.g., "202507151200_sample_task")
        tasks_directory (str): Directory to search for task files
        
    Returns:
        str: Module path or None if not found
    """
    from wedeliver_core_plus.helpers.task_execution.discover_tasks import execute as discover_all_tasks
    
    # Get all discovered tasks
    all_tasks = discover_all_tasks(tasks_directory)
    
    # Find the task with matching name
    for task in all_tasks:
        if task['task_name'] == task_name:
            return task['file_path']
    
    return None


def _send_reversion_success_notification(task_name: str, duration: float, result: Any):
    """Send Slack notification for successful task reversion."""
    try:
        message = f"🔄 Task Reversion Successful\n" \
                 f"Task: `{task_name}`\n" \
                 f"Duration: {duration:.2f} seconds\n" \
                 f"Result: {result}"
        
        send_notification_message(
            message=message,
            channel="database-tasks",
        )
    except Exception as e:
        app = WedeliverCorePlus.get_app()
        app.logger.warning(f"Failed to send reversion success notification: {e}")


def _send_reversion_failure_notification(task_name: str, duration: float, error: Exception):
    """Send Slack notification for failed task reversion."""
    try:
        message = f"❌ Task Reversion Failed\n" \
                 f"Task: `{task_name}`\n" \
                 f"Duration: {duration:.2f} seconds\n" \
                 f"Error: {str(error)}\n" \
                 f"Traceback: ```{traceback.format_exc()}```"
        
        send_notification_message(
            message=message,
            channel="database-tasks",
        )
    except Exception as e:
        app = WedeliverCorePlus.get_app()
        app.logger.warning(f"Failed to send reversion failure notification: {e}")


def get_revertible_tasks(tasks_directory: str = "app/scripts/__tasks__") -> list:
    """
    Get all tasks that can be reverted.
    
    Args:
        tasks_directory (str): Directory to search for task files
        
    Returns:
        list: List of revertible task information
    """
    app = WedeliverCorePlus.get_app()
    db = app.extensions['sqlalchemy'].db
    
    # Import TaskExecution model
    from app.models import TaskExecution
    
    # Get all successfully executed revertible tasks
    revertible_tasks = db.session.query(TaskExecution).filter(
        TaskExecution.execution_status == TaskExecutionStatus.SUCCESS.value,
        TaskExecution.is_revertible == True
    ).order_by(TaskExecution.execution_end_time.desc()).all()
    
    return revertible_tasks


def get_reversion_status(tasks_directory: str = "app/scripts/__tasks__") -> list:
    """
    Get reversion status of all executed tasks.
    
    Args:
        tasks_directory (str): Directory to search for task files
        
    Returns:
        list: List of task execution records with reversion status
    """
    app = WedeliverCorePlus.get_app()
    db = app.extensions['sqlalchemy'].db
    
    # Import TaskExecution model
    from app.models import TaskExecution
    
    # Get all executed tasks
    executed_tasks = db.session.query(TaskExecution).filter(
        TaskExecution.execution_status == TaskExecutionStatus.SUCCESS.value
    ).order_by(TaskExecution.execution_end_time.desc()).all()
    
    return executed_tasks
