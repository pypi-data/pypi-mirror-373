import importlib
import json
import os

from confluent_kafka import Consumer, KafkaError

from wedeliver_core_plus import WedeliverCorePlus
from wedeliver_core_plus.app_decorators import handle_exceptions
from wedeliver_core_plus.helpers.exceptions import AppValidationError


def consume_message(value):
    app = WedeliverCorePlus.get_app()

    message_payload = json.loads(value)

    if not message_payload:
        raise AppValidationError("No message payload found..")

    message = ["Got a message"]
    caller_service = message_payload.get("caller_service")

    if caller_service:
        message.append(f"from service: {caller_service}")

    message.append(f"value: {value}")

    app.logger.info(" ".join(message))

    function_name = message_payload.get("function_name")
    function_params = message_payload.get("function_params") or {}
    if not function_name:
        raise AppValidationError("No function name found..")

    @handle_exceptions
    def _execute_method():
        function_file, function_call = os.path.splitext(function_name)
        module = importlib.import_module(function_file)
        method = getattr(module, function_call[1:])

        return method(**function_params)

    _execute_method()
    # function_result = _execute_method()
    # app.logger.debug(function_result)


def create_consumer(topics):
    """
        Start Kafka listener
        """
    app = WedeliverCorePlus.get_app()

    c = Consumer(
        {
            "bootstrap.servers": app.config.get("BOOTSTRAP_SERVERS"),
            "sasl.username": app.config.get("SASL_USERNAME"),
            "sasl.password": app.config.get("SASL_PASSWORD"),
            "security.protocol": "SASL_SSL",
            "sasl.mechanisms": "PLAIN",
            "group.id": "services_group",
            "auto.offset.reset": "latest",  # earliest or latest
        }
    )

    c.subscribe(topics)

    app.logger.info(f"Kafka Consumer created and subscribed to topics [{' - '.join(topics)}]")

    return c


def poll_messages(consumer, wait_time=3.0):
    app = WedeliverCorePlus.get_app()

    wait_time = wait_time  # timeout is set to 10 second

    app.logger.info(f"Kafka is polling messages for each ({wait_time} seconds)...")

    while True:
        msg = consumer.poll(wait_time)
        # print(1)

        if msg is None:
            continue

        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                continue

            app.logger.error("error: {0}".format(msg.error()))
            break

        # message_key = msg.key()

        value = msg.value().decode('utf-8')

        try:
            consume_message(value)
        except AppValidationError:
            # app.logger.error(traceback.format_exc())
            continue

    consumer.close()
