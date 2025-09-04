from wedeliver_core_plus.helpers.topics import Topics
from wedeliver_core_plus.helpers import kafka_producers


def log_model_changes(
        data,
        **kwargs
):
    """
    Log model changes to kafka
    """
    kafka_producers.send_topic(topic=Topics().LOG_MODEL_CHANGES, datajson=dict(
        function_name='app.business_logic.logs.save_model_changes.execute',
        function_params=data
    ), kafka_configs=kwargs.get('kafka_configs'))
