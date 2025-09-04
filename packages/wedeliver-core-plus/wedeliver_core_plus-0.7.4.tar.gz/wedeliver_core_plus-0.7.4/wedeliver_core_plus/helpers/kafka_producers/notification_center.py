import platform
from datetime import datetime

from wedeliver_core_plus import WedeliverCorePlus
from wedeliver_core_plus.helpers.topics import Topics
from wedeliver_core_plus.helpers import kafka_producers


def send_critical_error(message, channel=None):
    channel = channel or "critical-errors"
    send_notification_message(
        channel=channel,
        title="critical",
        color="#df0000",
        message=message,
        emoji=":pleading_face:"
    )


def send_notification_message(
        message, channel="logs", title="Log", color="#32a4a7", emoji=":dizzy_face:",
        prefix_channel=True, prefix_title=True, prefix_message=True
):
    app = WedeliverCorePlus.get_app()
    env = app.config.get("FLASK_ENV")
    service_name = str(app.config.get("SERVICE_NAME"))

    if prefix_channel:
        channel = f"eng-{env if env == 'production' else 'development'}-{channel}"

    if prefix_title:
        title = f"New {title} in {service_name} Service"

    datetime_now = datetime.now().strftime("%Y-%m-%d %H:%M")

    if prefix_message:
        message = (
            f"Node: {platform.node()}\n"
            f"Env: {env}\n"
            f"Date: {datetime_now}\n"
            f"{message}"
        )

    data = {
        "notification_method": "slack",
        "payload": {
            "channel": channel,
            "title": title,
            "text": message,
            "color": color,
            "icon_emoji": emoji,
        },
    }

    kafka_producers.send_topic(topic=Topics().INTERNAL_NOTIFICATION_MESSAGE, datajson=data)


def send_push_notification(
        message_text, reference_type, user_ids, title=None, payload=None, created_by=None, **kwargs
):
    # token = None

    data = dict(
        user_ids=user_ids,
        reference_type=reference_type,
        created_by=created_by,
        title=title or "weDeliver",
        message_text=message_text,
        payload=payload,
        # language="ar"
    )

    kafka_producers.send_topic(topic=Topics().SEND_PUSH_NOTIFICATION, datajson=dict(
        function_name='app.business_logic.notification.send_push_notification.execute',
        function_params=data
    ), kafka_configs=kwargs.get('kafka_configs'))


def send_slack_notification_message_with_file_content(
        message,file_content, channel="logs", title="Log", color="#32a4a7", emoji=":dizzy_face:"
):
    app = WedeliverCorePlus.get_app()
    channel = "eng-{0}-{1}".format(
        app.config.get("FLASK_ENV")
        if app.config.get("FLASK_ENV") == "production"
        else "development",
        channel,
    )
    datetime_now = datetime.now().strftime("%Y-%m-%d %H:%M")
    message = "Node: {0}\nEnv:{3}\nDate: {1}\n{2}".format(
        platform.node(), datetime_now, message, str(app.config.get("FLASK_ENV"))
    )
    data = {
        "notification_method": "slack_file",
        "payload": {
            "channel": channel,
            "title": "New {0} in {1} Service".format(
                title, str(app.config.get("SERVICE_NAME"))
            ),
            "text": message,
            "color": color,
            "icon_emoji": emoji,
            "file_content":file_content
        },
    }
    kafka_producers.send_topic(topic=Topics().INTERNAL_NOTIFICATION_MESSAGE, datajson=data)
