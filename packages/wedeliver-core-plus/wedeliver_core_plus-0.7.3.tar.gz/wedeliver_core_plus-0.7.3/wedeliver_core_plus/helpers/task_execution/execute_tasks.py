import importlib
import os
import sys
from typing import List, Dict, Any

from wedeliver_core_plus import WedeliverCorePlus
from wedeliver_core_plus.helpers.task_execution.discover_tasks import get_pending_tasks


def execute(tasks_directory: str = "app/scripts/__tasks__") -> Dict[str, Any]:
    """
    Execute all pending database seeding tasks in chronological order.
    
    This function:
    1. Discovers all pending tasks
    2. Executes them in chronological order based on filename timestamps
    3. Stops execution if any task fails
    4. Returns summary of execution results
    
    Args:
        tasks_directory (str): Directory to search for task files
    
    Returns:
        Dict[str, Any]: Execution summary with results and statistics
    """
    app = WedeliverCorePlus.get_app()
    app.logger.info("Starting database task execution process")
    
    # Get all pending tasks
    pending_tasks = get_pending_tasks(tasks_directory)
    
    if not pending_tasks:
        app.logger.info("No pending tasks found")
        return {
            'status': 'success',
            'message': 'No pending tasks to execute',
            'total_tasks': 0,
            'executed_tasks': 0,
            'failed_tasks': 0,
            'results': []
        }
    
    app.logger.info(f"Found {len(pending_tasks)} pending tasks to execute")
    
    execution_results = []
    executed_count = 0
    failed_count = 0
    
    for task_info in pending_tasks:
        try:
            app.logger.info(f"Executing task: {task_info['task_name']} ({task_info['filename']})")
            
            # Execute the task
            result = _execute_single_task(task_info)
            
            execution_results.append({
                'task_name': task_info['task_name'],
                'filename': task_info['filename'],
                'status': 'success',
                'result': result
            })
            
            executed_count += 1
            app.logger.info(f"Task {task_info['task_name']} completed successfully")
            
        except Exception as e:
            error_msg = f"Task {task_info['task_name']} failed: {str(e)}"
            app.logger.error(error_msg)
            
            execution_results.append({
                'task_name': task_info['task_name'],
                'filename': task_info['filename'],
                'status': 'failed',
                'error': str(e)
            })
            
            failed_count += 1
            
            # Stop execution on first failure
            app.logger.error("Stopping task execution due to failure")
            break
    
    # Prepare summary
    summary = {
        'status': 'success' if failed_count == 0 else 'partial_failure',
        'message': f"Executed {executed_count} tasks successfully, {failed_count} failed",
        'total_tasks': len(pending_tasks),
        'executed_tasks': executed_count,
        'failed_tasks': failed_count,
        'results': execution_results
    }
    
    app.logger.info(f"Task execution completed: {summary['message']}")
    
    return summary


def _execute_single_task(task_info: Dict[str, str]) -> Any:
    """
    Execute a single task file.
    
    Args:
        task_info (Dict[str, str]): Task information dictionary
        
    Returns:
        Any: Result from the task execution
        
    Raises:
        Exception: If task execution fails
    """
    file_path = task_info['file_path']
    task_name = task_info['task_name']
    
    # Convert file path to module path
    # e.g., app/scripts/__tasks__/202505121554-add-default-users.py -> app.scripts.__tasks__.202505121554-add-default-users
    module_path = file_path.replace('/', '.').replace('.py', '')
    
    try:
        # Import the task module
        task_module = importlib.import_module(module_path)
        
        # Look for the apply function
        if not hasattr(task_module, 'apply'):
            raise AttributeError(f"Task module {module_path} does not have an 'apply' function")

        apply_function = getattr(task_module, 'apply')
        
        # Apply the task
        result = apply_function()
        
        return result
        
    except ImportError as e:
        raise ImportError(f"Failed to import task module {module_path}: {str(e)}")
    except AttributeError as e:
        raise AttributeError(f"Task execution error in {module_path}: {str(e)}")
    except Exception as e:
        raise Exception(f"Task execution failed in {module_path}: {str(e)}")


def execute_specific_task(task_name: str, tasks_directory: str = "app/scripts/__tasks__") -> Dict[str, Any]:
    """
    Execute a specific task by name.
    
    Args:
        task_name (str): Name of the task to execute
        tasks_directory (str): Directory to search for task files
        
    Returns:
        Dict[str, Any]: Execution result
    """
    app = WedeliverCorePlus.get_app()
    
    from wedeliver_core_plus.helpers.task_execution.discover_tasks import execute as discover_all_tasks
    
    # Find the specific task
    all_tasks = discover_all_tasks(tasks_directory)
    target_task = None
    
    for task in all_tasks:
        if task['task_name'] == task_name:
            target_task = task
            break
    
    if not target_task:
        raise ValueError(f"Task '{task_name}' not found")
    
    app.logger.info(f"Executing specific task: {task_name}")
    
    try:
        result = _execute_single_task(target_task)
        
        return {
            'status': 'success',
            'task_name': task_name,
            'result': result
        }
        
    except Exception as e:
        app.logger.error(f"Failed to execute task {task_name}: {str(e)}")
        
        return {
            'status': 'failed',
            'task_name': task_name,
            'error': str(e)
        }
