"""
TaskExecutionBaseModel for tracking database seeding tasks.

This is a core infrastructure component that provides a base model for task execution
tracking across all services. It follows the ThrivveService architecture pattern
where core infrastructure components are moved to wedeliver_core_plus for reusability.
"""

from wedeliver_core_plus import WedeliverCorePlus
from wedeliver_core_plus.helpers.get_country_code import get_country_code
from wedeliver_core_plus.helpers.enums import TaskExecutionStatus


def init_task_execution_base_model():
    """Initialize the TaskExecutionBaseModel for tracking database seeding tasks."""

    app = WedeliverCorePlus.get_app()
    db = app.extensions['sqlalchemy'].db

    from wedeliver_core_plus import init_base_model

    # Import base model
    base_model = init_base_model()

    class TaskExecutionBaseModel(base_model):
        """Base model for tracking executed database seeding tasks"""

        __abstract__ = True

        task_name = db.Column(db.String(255), nullable=False, unique=True, index=True)
        task_file_path = db.Column(db.String(500), nullable=False)
        execution_status = db.Column(
            db.String(32),
            nullable=False,
            default=TaskExecutionStatus.PENDING.value,
            index=True
        )
        execution_start_time = db.Column(db.DateTime, nullable=True)
        execution_end_time = db.Column(db.DateTime, nullable=True)
        execution_duration_seconds = db.Column(db.Float, nullable=True)
        error_message = db.Column(db.Text, nullable=True)
        result_message = db.Column(db.Text, nullable=True)
        country_code = db.Column(db.String(2), default=get_country_code)

        # Reversion tracking fields
        is_revertible = db.Column(db.Boolean, default=False, index=True)
        reversion_status = db.Column(db.String(32), nullable=True, index=True)
        reversion_time = db.Column(db.DateTime, nullable=True)
        reversion_message = db.Column(db.Text, nullable=True)
        reversion_duration_seconds = db.Column(db.Float, nullable=True)

        def __repr__(self):
            return f"<TaskExecution {self.task_name}: {self.execution_status}>"

    return TaskExecutionBaseModel
