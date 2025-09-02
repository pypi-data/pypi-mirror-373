from rbx.gcp.pubsub import PubSubPublisher


def notify_mdm(payload, project, topic, version):
    """Send an event to Google Pub/Sub to notify the change."""
    PubSubPublisher(project=project, topic=topic, version=version).dispatch(payload)
