from wedeliver_core_plus.helpers.kafka_producer import Producer
from wedeliver_core_plus import WedeliverCorePlus


def send_topic(topic, datajson, kafka_configs=None):
    if kafka_configs is None:
        kafka_configs = {}

    kafka_configs.update(
        producer_version=2
    )
    if datajson and isinstance(datajson, dict):
        app = WedeliverCorePlus.get_app()
        datajson.update(caller_service=app.config.get('SERVICE_NAME'))
    Producer().send_topic(topic=topic, datajson=datajson, **kafka_configs)
