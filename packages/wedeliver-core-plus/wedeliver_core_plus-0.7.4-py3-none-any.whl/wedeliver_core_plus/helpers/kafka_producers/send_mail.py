from wedeliver_core_plus.helpers.kafka_producer import Producer
from wedeliver_core_plus.helpers.topics import Topics

def send_mail(emails, message, title):
    response = dict(
        body=message,
        title=title,
        emails=emails
    )

    Producer().send_topic(Topics().SEND_MAIL, response)