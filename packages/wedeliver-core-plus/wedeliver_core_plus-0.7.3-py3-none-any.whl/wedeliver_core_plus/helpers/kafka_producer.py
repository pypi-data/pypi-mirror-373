import json
import random
import string
import traceback

from wedeliver_core_plus import WedeliverCorePlus
from confluent_kafka import Producer as kafka_Producer

from wedeliver_core_plus.helpers.exceptions import AppValidationError
from wedeliver_core_plus.helpers.micro_fetcher import MicroFetcher


class Producer:
    app = None

    def __init__(self):
        self.app = WedeliverCorePlus.get_app()
        self._producer = (
            None
            if not self.app or self.app.config.get("FLASK_ENV") == "local"
            else kafka_Producer(
                {
                    "sasl.mechanisms": "PLAIN",
                    "request.timeout.ms": 20000,
                    "bootstrap.servers": self.app.config.get("BOOTSTRAP_SERVERS"),
                    "retry.backoff.ms": 500,
                    "sasl.username": self.app.config.get("SASL_USERNAME"),
                    "sasl.password": self.app.config.get("SASL_PASSWORD"),
                    "security.protocol": "SASL_SSL",
                }
            )
        )

    def send_topic(self, topic, datajson, **configs):

        if not self.app:
            return True

        self.app.logger.debug(datajson)

        micro_fetcher_instead_of_kafka = self.app.config.get("MICRO_FETCHER_INSTEAD_OF_KAFKA", False)

        if micro_fetcher_instead_of_kafka:
            service_name = configs.get('service_name')
            if service_name:
                self.app.logger.debug("Kafka: Direct HTTP Call is enabled")

                MicroFetcher(service_name).from_function(datajson.get('function_name')).with_params(
                    **datajson.get('function_params')).execute()

                return True

            self.app.logger.error(
                f"Kafka ({topic}) No service name found, you need to provide service_name in configs to use MicroFetcher instead of kafka")
            self.app.logger.debug("Kafka: Direct HTTP Call is disabled")


        if self._producer is None:
            self.app.logger.debug(
                "Can not send Kafka message, this is {} environment".format(
                    self.app.config.get("FLASK_ENV")
                )
            )
            return True

        def acked(err, msg):
            """Delivery report handler called on
            successful or failed delivery of message
            """
            if err is not None:

                self.app.logger.error("Failed to deliver message: {0}".format(err))

            else:
                self.app.logger.debug(
                    "Produced record to topic {0} partition [{1}] @ offset {2}".format(
                        msg.topic(), msg.partition(), msg.offset()
                    )
                )
                # is_success = True

        # record_key = "alice"
        record_key = str(random.choices(string.digits, k=5))

        self._producer.produce(
            topic, key=record_key, value=json.dumps(datajson), on_delivery=acked
        )
        self._producer.poll(0)
        self._producer.flush()

        return True
