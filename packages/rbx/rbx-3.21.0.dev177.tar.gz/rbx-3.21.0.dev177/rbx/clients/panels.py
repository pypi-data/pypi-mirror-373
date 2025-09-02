import logging

from . import Client, HttpAuth

logger = logging.getLogger(__name__)


class PanelsClient(Client):
    """API Client for the Panels Service."""

    def __init__(self, endpoint, token):
        super().__init__()
        self.ENDPOINT = endpoint.rstrip("/")
        self.token = token

    @property
    def auth(self):
        """The Panels Service uses Digest Authentication."""
        return HttpAuth(self.token, key="X-RBX-TOKEN")

    def search(self, **parameters):
        """Perform a Panels search."""
        return self._post("/search", data=parameters)

    def set_weather_watch(self, caller, country, supplier):
        """Set a watch on the specified country and supplier, using the caller ID."""
        return self.request(
            method="get",
            path="/forecast/watch",
            data={"caller": caller, "country": country, "supplier": supplier},
        )

    def set_weather_unwatch(self, caller, country, supplier):
        """Remove a watch on the specified country and supplier, using the caller ID."""
        return self.request(
            method="get",
            path="/forecast/unwatch",
            data={"caller": caller, "country": country, "supplier": supplier},
        )
