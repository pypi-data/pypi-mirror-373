import json
import logging

from datetime import datetime
from google.cloud import pubsub

logger = logging.getLogger(__name__)


def strip(message):
    """Strip whitespaces from the message payload."""
    payload = {
        k: v.strip() if type(v) is str else v for k, v in message["payload"].items()
    }
    message["payload"] = payload
    return message


class PubSubPublisher:
    """Publish messages to Pub/Sub."""

    def __init__(self, project, topic, version):
        self.project = project
        self.publisher = pubsub.PublisherClient()
        self.topic = topic
        self.version = version

    def _format(self, message, timestamp):
        """Format a message item into a Pub/Sub message."""
        return {
            "version": self.version,
            "timestamp": timestamp,
            "payload": message,
        }

    def _publish(self, message):
        """Publish to Pub/Sub.

        We wait for the result to ensure the publish operation has succeeded. The 30 seconds
        timeout is set in case something goes horribly wrong, which would lock the thread forever.

        Note that the Pub/Sub message must be sent as a bytestring.
        """
        logger.debug('Notifying "{}": <{}>'.format(self.topic, message))
        future = self.publisher.publish(
            f"projects/{self.project}/topics/{self.topic}",
            json.dumps(strip(message)).encode("utf-8"),
        )
        return future.result(30)

    def dispatch(self, payload):
        """Dispatch events to be published.

        The Pub/Sub library takes care of batching behind the hook, so all we
        need to do is post the messages independently.
        """
        self.timestamp = datetime.utcnow().isoformat()

        if type(payload) in (list, tuple):
            messages = [
                self._format(message, timestamp=self.timestamp) for message in payload
            ]
        else:
            messages = [self._format(payload, timestamp=self.timestamp)]

        for message in messages:
            self._publish(message)
