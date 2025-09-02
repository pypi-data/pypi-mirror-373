import logging

from google.api_core.retry import Retry
from google.api_core.exceptions import AlreadyExists, GoogleAPIError
from google.cloud import tasks_v2

logger = logging.getLogger(__name__)


class Queue:
    """Utility class to create queues and tasks in Google Cloud Tasks."""

    def __init__(self, project_id, location, queue_name, service="default"):
        """Initialise the Google Cloud Queue.

        Parameters:
            project_id (str):
                The Google Cloud Project ID.
            location (str):
                The location code of the Queue.
                This must match the location of the App Engine application.
            queue_name (str):
                The name of the queue.
            service:
                The default App Engine service that the task will be sent to.
                By default, tasks are sent to the 'default' service.

        """
        self.client = tasks_v2.CloudTasksClient()
        self.location = f"projects/{project_id}/locations/{location}"
        self.service = service

        name = self.client.queue_path(project_id, location, queue_name)
        self.queue = tasks_v2.Queue(name=name)

    @property
    def retry(self):
        """Exponential retry decorator.

        This class is a decorator used to add exponential back-off retry behavior to the
        create_task RPC call.

        We implement it here as a property of the queue, first to always use the same retry logic,
        and second to allow us to mock it more easily in tests.
        """
        return Retry(initial=0.1, maximum=60, multiplier=1.3, deadline=600)

    def create(self):
        try:
            self.client.create_queue(parent=self.location, queue=self.queue)
        except AlreadyExists:
            logger.debug(f'Queue "{self.queue.name}" already exists.')
        except GoogleAPIError as e:
            logger.exception(e)

    def enqueue(self, uri, headers=None, method="POST", payload=None, service=None):
        """Create a task in the queue.

        This will create an App Engine HTTP request. The task will be delivered to the App Engine
        app which belongs to the same project as the queue.

        Parameters:
            uri (str):
                The url that the task will be sent to.
            headers (dict):
                Optional additional HTTP request headers.
                This map contains the header field names and values.
            method (str):
                The HTTP method to use for the request. Can be either GET or POST.
                The default is POST.
            payload (bytes):
                HTTP request body.
                A request body is allowed only if the HTTP method is POST.
                The payload must be encoded.
            service:
                The App Engine service that the task will be sent to.
                By default, the task is sent to the service implemented by the Queue.

        Raises:
            TypeError: If the payload parameter is not a bytes type.

        """
        http_method = {
            "GET": tasks_v2.HttpMethod.GET,
            "POST": tasks_v2.HttpMethod.POST,
        }.get(method, tasks_v2.HttpMethod.GET)

        task = {
            "app_engine_http_request": {
                "app_engine_routing": {"service": service or self.service},
                "headers": headers or {},
                "http_method": http_method,
                "relative_uri": uri,
            }
        }
        if payload:
            task["app_engine_http_request"]["body"] = payload

        try:
            self.client.create_task(parent=self.queue.name, task=task, retry=self.retry)
        except GoogleAPIError as e:
            logger.exception(e)
