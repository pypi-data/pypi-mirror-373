import os
import click
from datetime import datetime

from wedeliver_core_plus import WedeliverCorePlus


def register_task_commands(app, tasks_directory: str = "app/scripts/__tasks__"):
    """
    Register task management CLI commands with the Flask app.
    
    Args:
        app: Flask application instance
        tasks_directory (str): Directory where task files are stored
    """
    
    @app.cli.command('task')
    @click.argument('action')
    @click.argument('task_name', required=False)
    @click.option('--dry-run', is_flag=True, help='Show what would be created without actually creating it')
    def task_command(action, task_name, dry_run):
        """
        Database task management commands.
        
        Actions:
            create <task-name>  - Create a new task file with template
            list               - List all discovered tasks
            pending            - List pending tasks
            executed           - List executed tasks
            apply              - Execute all pending tasks
            apply <task-name>  - Execute a specific task
            revert <task-name> - Revert a successfully executed task
            revert list      - List all revertible tasks
            revert status    - Show reversion status of all executed tasks
        """
        if action == 'create':
            if not task_name:
                click.echo("Error: task-name is required for create action")
                click.echo("Usage: flask task create <task-name>")
                return
            
            create_task_file(task_name, tasks_directory, dry_run)
            
        elif action == 'list':
            list_all_tasks(tasks_directory)
            
        elif action == 'pending':
            list_pending_tasks(tasks_directory)
            
        elif action == 'executed':
            list_executed_tasks()
            
        elif action == 'apply':
            if task_name:
                apply_specific_task(task_name, tasks_directory)
            else:
                apply_all_pending_tasks(tasks_directory)

        elif action == 'revert':
            if task_name == "list":
                list_revertible_tasks(tasks_directory)
            elif task_name == "status":
                show_reversion_status(tasks_directory)
            elif task_name:
                revert_specific_task(task_name, tasks_directory)
            else:
                click.echo("❌ Please specify a task name or use list/status")
                click.echo("Usage: flask task revert <task-name>")
                click.echo("       flask task revert --list")
                click.echo("       flask task revert --status")

        else:
            click.echo(f"Unknown action: {action}")
            click.echo("Available actions: create, list, pending, executed, apply, revert")


def create_task_file(task_name: str, tasks_directory: str, dry_run: bool = False):
    """Create a new task file with the proper naming convention and template."""
    
    # Generate timestamp prefix
    timestamp = datetime.now().strftime('%Y%m%d%H%M')
    
    # Clean task name (replace spaces and special chars with hyphens)
    clean_task_name = task_name.lower().replace(' ', '-').replace('_', '-')
    
    # Generate filename
    filename = f"{timestamp}-{clean_task_name}.py"
    
    # Ensure tasks directory exists
    if not dry_run and not os.path.exists(tasks_directory):
        os.makedirs(tasks_directory)
        click.echo(f"Created directory: {tasks_directory}")
    
    # Full file path
    file_path = os.path.join(tasks_directory, filename)
    
    # Generate task template
    template_content = _generate_task_template(clean_task_name, filename)
    
    if dry_run:
        click.echo("DRY RUN - Would create the following:")
        click.echo(f"File: {file_path}")
        click.echo("Content:")
        click.echo("=" * 50)
        click.echo(template_content)
        click.echo("=" * 50)
    else:
        # Check if file already exists
        if os.path.exists(file_path):
            click.echo(f"Error: File {file_path} already exists")
            return
        
        # Write the file
        with open(file_path, 'w') as f:
            f.write(template_content)
        
        click.echo(f"✅ Created task file: {file_path}")
        click.echo(f"📝 Task name: {clean_task_name.replace('-', '_')}")
        click.echo(f"🕐 Timestamp: {timestamp}")
        click.echo("")
        click.echo("Next steps:")
        click.echo("1. Edit the task file and implement your logic in the apply() function")
        click.echo("2. Test your task: flask task run " + clean_task_name.replace('-', '_'))
        click.echo("3. Run all pending tasks: flask task run")


def _generate_task_template(task_name: str, filename: str) -> str:
    """Generate the task file template content."""

    # Extract timestamp and descriptive name from filename
    # filename format: YYYYMMDDHHMM-descriptive-name.py
    base_filename = filename.replace('.py', '')
    if '-' in base_filename:
        timestamp_part, descriptive_part = base_filename.split('-', 1)
        # Create function name with timestamp to ensure uniqueness
        function_name = f"{timestamp_part}_{descriptive_part.replace('-', '_')}"
    else:
        # Fallback for non-standard filenames
        function_name = task_name.replace('-', '_')
    
    template = f'''"""
Database seeding task: {task_name}

This task was generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
File: {filename}

Instructions:
1. Implement your database seeding logic in the apply() function below
2. Optionally implement revert() function to enable task reversion
3. The task will be tracked automatically and run only once
4. Slack notifications will be sent on success/failure
5. Return a descriptive message about what was accomplished

Example patterns:
- Creating default data
- Migrating existing data
- Fixing data inconsistencies
- Adding missing relationships

Reversion Guidelines:
- Implement revert() function to undo the changes made by apply()
- Only implement revert() if the changes can be safely undone
- Use database transactions for atomic operations
- Test reversion logic thoroughly before deployment
"""

from app import app, db
from wedeliver_core_plus.helpers.task_execution.task_decorator import task_execution_tracker


@task_execution_tracker(
    task_name="{function_name}",
    task_file_path="app/scripts/__tasks__/{filename}"
)
def apply():
    """
    Apply the {task_name} database seeding task.

    TODO: Implement your task logic here

    Returns:
        str: Description of what was accomplished
    """
    
    # TODO: Add your database seeding logic here
    # Example:
    # 
    # # Create some default data
    # from app.models.core.some_model import SomeModel
    # 
    # if not db.session.query(SomeModel).filter(SomeModel.name == "default").first():
    #     default_item = SomeModel(name="default", value="some_value")
    #     db.session.add(default_item)
    #     db.session.commit()
    #     return "Created default SomeModel entry"
    # else:
    #     return "Default SomeModel entry already exists"
    
    app.logger.info("Executing {task_name} task")

    # Replace this with your actual implementation
    return "Task {task_name} executed successfully - TODO: implement actual logic"


def revert():
    """
    Revert the {task_name} database seeding task.

    This function should undo the changes made by the apply() function.
    Only implement this if the task changes can be safely reverted.

    TODO: Implement your reversion logic here (optional)

    Returns:
        str: Description of what was reverted
    """

    # TODO: Add your reversion logic here
    # Example:
    #
    # # Remove the data created by apply()
    # from app.models.core.some_model import SomeModel
    #
    # default_item = db.session.query(SomeModel).filter(SomeModel.name == "default").first()
    # if default_item:
    #     db.session.delete(default_item)
    #     db.session.commit()
    #     return "Removed default SomeModel entry"
    # else:
    #     return "Default SomeModel entry was not found (already removed or never created)"

    app.logger.info("Reverting {task_name} task")

    # Replace this with your actual reversion implementation
    # Remove this function entirely if the task cannot be safely reverted
    return "Task {task_name} reverted successfully - TODO: implement actual reversion logic"


if __name__ == "__main__":
    from app import app

    with app.app_context():
        result = apply()
        print(f"Task result: {{result}}")
'''
    
    return template


def list_all_tasks(tasks_directory: str):
    """List all discovered tasks."""
    from wedeliver_core_plus.helpers.task_execution.discover_tasks import execute as discover_tasks
    
    tasks = discover_tasks(tasks_directory)
    
    if not tasks:
        click.echo(f"No tasks found in {tasks_directory}")
        return
    
    click.echo(f"Found {len(tasks)} tasks:")
    click.echo("")
    
    for task in tasks:
        click.echo(f"📄 {task['filename']}")
        click.echo(f"   Task: {task['task_name']}")
        click.echo(f"   Timestamp: {task['timestamp']}")
        click.echo("")


def list_pending_tasks(tasks_directory: str):
    """List pending (not yet executed) tasks."""
    from wedeliver_core_plus.helpers.task_execution.discover_tasks import get_pending_tasks
    
    pending_tasks = get_pending_tasks(tasks_directory)
    
    if not pending_tasks:
        click.echo("No pending tasks found")
        return
    
    click.echo(f"Found {len(pending_tasks)} pending tasks:")
    click.echo("")
    
    for task in pending_tasks:
        click.echo(f"⏳ {task['filename']}")
        click.echo(f"   Task: {task['task_name']}")
        click.echo(f"   Timestamp: {task['timestamp']}")
        click.echo("")


def list_executed_tasks():
    """List executed tasks."""
    app = WedeliverCorePlus.get_app()
    db = app.extensions['sqlalchemy'].db

    from app.models import TaskExecution
    from wedeliver_core_plus.helpers.enums import TaskExecutionStatus
    

    executed_tasks = db.session.query(TaskExecution).filter(
        TaskExecution.execution_status == TaskExecutionStatus.SUCCESS.value
    ).order_by(TaskExecution.execution_end_time.desc()).all()
    
    if not executed_tasks:
        click.echo("No executed tasks found")
        return
    
    click.echo(f"Found {len(executed_tasks)} executed tasks:")
    click.echo("")
    
    for task in executed_tasks:
        click.echo(f"✅ {task.task_name}")
        click.echo(f"   Executed: {task.execution_end_time}")
        click.echo(f"   Duration: {task.execution_duration_seconds:.2f}s")
        click.echo(f"   Result: {task.result_message[:100]}...")
        click.echo("")


def apply_all_pending_tasks(tasks_directory: str):
    """Execute all pending tasks."""
    from wedeliver_core_plus.helpers.task_execution.execute_tasks import execute as execute_all_tasks
    
    click.echo("🚀 Applying all pending tasks...")
    
    try:
        result = execute_all_tasks(tasks_directory)
        
        if result['status'] == 'success':
            click.echo(f"✅ {result['message']}")
        else:
            click.echo(f"⚠️  {result['message']}")
        
        click.echo(f"📊 Total: {result['total_tasks']}, Executed: {result['executed_tasks']}, Failed: {result['failed_tasks']}")
        
    except Exception as e:
        click.echo(f"❌ Failed to apply tasks: {str(e)}")


def apply_specific_task(task_name: str, tasks_directory: str):
    """Execute a specific task by name."""
    from wedeliver_core_plus.helpers.task_execution.execute_tasks import execute_specific_task
    from wedeliver_core_plus.helpers.task_execution.discover_tasks import execute as discover_all_tasks

    click.echo(f"🚀 Applying task: {task_name}")

    try:
        # First try to find the task with the exact name provided
        try:
            result = execute_specific_task(task_name, tasks_directory)
        except ValueError:
            # If not found, try to find tasks that match the descriptive part
            # This provides backward compatibility for old naming convention
            all_tasks = discover_all_tasks(tasks_directory)
            matching_tasks = []

            for task in all_tasks:
                # Check if the task name ends with the provided name (for backward compatibility)
                if task['task_name'].endswith(f"_{task_name}") or task['task_name'] == task_name:
                    matching_tasks.append(task)

            if not matching_tasks:
                raise ValueError(f"Task '{task_name}' not found")
            elif len(matching_tasks) == 1:
                # Execute the single matching task
                result = execute_specific_task(matching_tasks[0]['task_name'], tasks_directory)
            else:
                # Multiple matches found, show them to the user
                click.echo(f"❌ Multiple tasks found matching '{task_name}':")
                for task in matching_tasks:
                    click.echo(f"   - {task['task_name']} ({task['filename']})")
                click.echo("Please specify the full task name including timestamp.")
                return
        
        if result['status'] == 'success':
            click.echo(f"✅ Task completed: {result['result']}")
        else:
            click.echo(f"❌ Task failed: {result['error']}")
            
    except Exception as e:
        click.echo(f"❌ Failed to apply task: {str(e)}")


def revert_specific_task(task_name: str, tasks_directory: str):
    """Revert a specific task by name."""
    from wedeliver_core_plus.helpers.task_execution.revert_tasks import revert_task

    click.echo(f"🔄 Reverting task: {task_name}")

    # Confirm reversion for safety
    if not click.confirm(f"Are you sure you want to revert task '{task_name}'? This action will undo the task's changes."):
        click.echo("❌ Reversion cancelled by user")
        return

    try:
        result = revert_task(task_name, tasks_directory)

        if result['status'] == 'success':
            click.echo(f"✅ Task reverted successfully: {result['result']}")
            click.echo(f"   Duration: {result['reversion_duration']:.2f} seconds")
        else:
            click.echo(f"❌ Task reversion failed: {result['error']}")

    except Exception as e:
        click.echo(f"❌ Failed to revert task: {str(e)}")


def list_revertible_tasks(tasks_directory: str):
    """List all tasks that can be reverted."""
    from wedeliver_core_plus.helpers.task_execution.revert_tasks import get_revertible_tasks

    click.echo("🔄 Revertible Tasks")
    click.echo("=" * 60)

    try:
        revertible_tasks = get_revertible_tasks(tasks_directory)

        if not revertible_tasks:
            click.echo("No revertible tasks found.")
            return

        click.echo(f"Found {len(revertible_tasks)} revertible tasks:\n")

        for task in revertible_tasks:
            status_icon = "🔄" if task.reversion_status is None else "✅" if task.reversion_status == "Success" else "❌"
            reversion_info = ""

            if task.reversion_status == "Success":
                reversion_info = f" (Reverted: {task.reversion_time.strftime('%Y-%m-%d %H:%M:%S')})"
            elif task.reversion_status == "Failed":
                reversion_info = f" (Reversion Failed: {task.reversion_time.strftime('%Y-%m-%d %H:%M:%S')})"

            click.echo(f"{status_icon} {task.task_name}")
            click.echo(f"   Executed: {task.execution_end_time.strftime('%Y-%m-%d %H:%M:%S')}")
            click.echo(f"   Duration: {task.execution_duration_seconds:.2f}s")
            if reversion_info:
                click.echo(f"   {reversion_info}")
            click.echo("")

    except Exception as e:
        click.echo(f"❌ Failed to list revertible tasks: {str(e)}")


def show_reversion_status(tasks_directory: str):
    """Show reversion status of all executed tasks."""
    from wedeliver_core_plus.helpers.task_execution.revert_tasks import get_reversion_status

    click.echo("📊 Task Reversion Status")
    click.echo("=" * 60)

    try:
        executed_tasks = get_reversion_status(tasks_directory)

        if not executed_tasks:
            click.echo("No executed tasks found.")
            return

        revertible_count = sum(1 for task in executed_tasks if task.is_revertible)
        reverted_count = sum(1 for task in executed_tasks if task.reversion_status == "Success")

        click.echo(f"Total executed tasks: {len(executed_tasks)}")
        click.echo(f"Revertible tasks: {revertible_count}")
        click.echo(f"Successfully reverted: {reverted_count}")
        click.echo("")

        for task in executed_tasks:
            if task.is_revertible:
                if task.reversion_status is None:
                    status = "🔄 Available for reversion"
                elif task.reversion_status == "Success":
                    status = f"✅ Reverted ({task.reversion_time.strftime('%Y-%m-%d %H:%M:%S')})"
                elif task.reversion_status == "Failed":
                    status = f"❌ Reversion failed ({task.reversion_time.strftime('%Y-%m-%d %H:%M:%S')})"
                else:
                    status = f"⏳ {task.reversion_status}"
            else:
                status = "🚫 Not revertible"

            click.echo(f"{task.task_name}")
            click.echo(f"   Executed: {task.execution_end_time.strftime('%Y-%m-%d %H:%M:%S')}")
            click.echo(f"   Status: {status}")
            click.echo("")

    except Exception as e:
        click.echo(f"❌ Failed to show reversion status: {str(e)}")


# Backward compatibility aliases (deprecated)
def run_all_pending_tasks(tasks_directory: str):
    """
    DEPRECATED: Use apply_all_pending_tasks() instead.
    Execute all pending tasks.
    """
    import warnings
    warnings.warn(
        "run_all_pending_tasks() is deprecated. Use apply_all_pending_tasks() instead.",
        DeprecationWarning,
        stacklevel=2
    )
    return apply_all_pending_tasks(tasks_directory)


def run_specific_task(task_name: str, tasks_directory: str):
    """
    DEPRECATED: Use apply_specific_task() instead.
    Execute a specific task by name.
    """
    import warnings
    warnings.warn(
        "run_specific_task() is deprecated. Use apply_specific_task() instead.",
        DeprecationWarning,
        stacklevel=2
    )
    return apply_specific_task(task_name, tasks_directory)
