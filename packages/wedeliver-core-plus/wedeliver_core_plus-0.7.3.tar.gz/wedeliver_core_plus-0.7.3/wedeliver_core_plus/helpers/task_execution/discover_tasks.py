import os
import glob
import re
from datetime import datetime
from typing import List, Dict

from wedeliver_core_plus import WedeliverCorePlus


def execute(tasks_directory: str = "app/scripts/__tasks__") -> List[Dict[str, str]]:
    """
    Discover all task files in the tasks directory and return them sorted by timestamp.
    
    Args:
        tasks_directory (str): Directory to search for task files
    
    Returns:
        List[Dict]: List of task information dictionaries with keys:
            - task_name: The extracted task name from filename
            - file_path: Full path to the task file
            - timestamp: Extracted timestamp from filename
            - filename: Just the filename
    """
    app = WedeliverCorePlus.get_app()
    
    # Ensure the tasks directory exists
    if not os.path.exists(tasks_directory):
        app.logger.warning(f"Tasks directory {tasks_directory} does not exist")
        return []
    
    # Find all Python files in the tasks directory
    task_files = glob.glob(os.path.join(tasks_directory, "*.py"))
    
    # Filter out __init__.py and other non-task files
    task_files = [f for f in task_files if not os.path.basename(f).startswith("__")]
    
    discovered_tasks = []
    
    for file_path in task_files:
        filename = os.path.basename(file_path)
        
        # Extract task information from filename
        task_info = _parse_task_filename(filename, file_path)
        
        if task_info:
            discovered_tasks.append(task_info)
        else:
            app.logger.warning(f"Skipping file {filename} - does not match task naming convention")
    
    # Sort tasks by timestamp (chronological order)
    discovered_tasks.sort(key=lambda x: x['timestamp'])
    
    app.logger.info(f"Discovered {len(discovered_tasks)} tasks in {tasks_directory}")
    
    return discovered_tasks


def _parse_task_filename(filename: str, file_path: str) -> Dict[str, str]:
    """
    Parse task filename to extract task information.
    
    Expected format: YYYYMMDDHHMM-descriptive-name.py
    Example: 202505121554-add-default-users.py
    
    Args:
        filename (str): The task filename
        file_path (str): Full path to the task file
        
    Returns:
        Dict[str, str]: Task information or None if filename doesn't match pattern
    """
    app = WedeliverCorePlus.get_app()
    
    # Pattern to match YYYYMMDDHHMM-descriptive-name.py
    pattern = r'^(\d{12})-(.+)\.py$'
    match = re.match(pattern, filename)
    
    if not match:
        return None
    
    timestamp_str = match.group(1)
    descriptive_name = match.group(2)
    
    # Validate timestamp format
    try:
        timestamp = datetime.strptime(timestamp_str, '%Y%m%d%H%M')
    except ValueError:
        app.logger.error(f"Invalid timestamp format in filename {filename}")
        return None
    
    # Generate task name including timestamp to ensure uniqueness
    # Format: timestamp_descriptive_name (e.g., "202507151200_sample_task")
    task_name = f"{timestamp_str}_{descriptive_name.replace('-', '_')}"
    
    return {
        'task_name': task_name,
        'file_path': file_path,
        'timestamp': timestamp_str,
        'filename': filename,
        'descriptive_name': descriptive_name,
        'parsed_timestamp': timestamp
    }


def get_pending_tasks(tasks_directory: str = "app/scripts/__tasks__") -> List[Dict[str, str]]:
    """
    Get all tasks that haven't been executed successfully yet.
    
    Args:
        tasks_directory (str): Directory to search for task files
    
    Returns:
        List[Dict]: List of pending task information
    """
    app = WedeliverCorePlus.get_app()
    db = app.extensions['sqlalchemy'].db
    
    from app.models import TaskExecution
    from wedeliver_core_plus.helpers.enums import TaskExecutionStatus
    

    # Get all discovered tasks
    all_tasks = execute(tasks_directory)
    
    # Get list of successfully executed task names
    executed_tasks = db.session.query(TaskExecution.task_name).filter(
        TaskExecution.execution_status == TaskExecutionStatus.SUCCESS.value
    ).all()
    
    executed_task_names = {task[0] for task in executed_tasks}
    
    # Filter out already executed tasks
    pending_tasks = [
        task for task in all_tasks 
        if task['task_name'] not in executed_task_names
    ]
    
    app.logger.info(f"Found {len(pending_tasks)} pending tasks out of {len(all_tasks)} total tasks")
    
    return pending_tasks
