import csv
from io import StringIO
import logging
from os import path
import shelve

import arrow

from ..exceptions import ClientException
from . import Client, HttpAuth, retry

logger = logging.getLogger(__name__)


class AdsquareClient(Client):
    """Client for adsquare API.

    The API documentation can be found on the Platform wiki:
    https://github.com/rockabox/rbx/wiki/adsquare

    """

    AUTH_PATH = "auth/login"
    ENDPOINT = "https://amp.adsquare.com/api/v1/"
    STANDARD_COMPANY_ID = "588b6428e4b0d7d5f6895bd1"
    TIME_FORMAT = "YYYY-MM-DDTHH:mm:ss.SSS[Z]"

    def __init__(self, company_id, dsp_id, destination="/tmp"):
        super().__init__()
        self.company_id = company_id
        self.dsp_id = dsp_id
        self.shelf = path.join(destination, "adsquare.segments")

    @property
    def auth(self):
        """adsquare uses Digest Authentication."""
        return HttpAuth(self.token, key="X-AUTH-TOKEN")

    @retry.Retry(deadline=300.0)
    def create_config(self, country_code, name, start_date, end_date):
        """Create a new observation configuration.

        The start and end date are expected to be in ISO 8601, though any format understood by
        Arrow will work.
        """
        path = f"measurement/configs/byCompany/{self.company_id}"
        response = self.request(
            "post",
            path,
            data={
                "dspId": self.dsp_id,
                "countryCode": country_code,
                "name": name,
                "active": True,
                "observationMode": "full",
                "radiusInMeter": 50,
                "validFrom": arrow.get(start_date).format(self.TIME_FORMAT),
                "validTo": arrow.get(end_date).format(self.TIME_FORMAT),
            },
        )
        return response["id"]

    def disable_webhook(self, config_id):
        """Disable the registered webhook for the given configuration ID."""
        self.register_webhook(config_id, disable=True)

    @retry.Retry(deadline=300.0)
    def download_config(self, config_id):
        """Download the list of site locations uploaded to the given configuration.

        The points are returned as a dictionary of (lat, long) tuples keyed by assigned ID.
        """
        data = self.request(
            "get",
            f"measurement/configs/{config_id}/dataset/poi",
            content_type="text/plain",
        )

        pois = {}
        reader = csv.DictReader(StringIO(data))
        for row in reader:
            pois[row["id"]] = (row["lat"], row["lon"])

        return pois

    def get_segments(self, company_ids=None, country_code=None):
        """Get segments from local cache."""
        with shelve.open(self.shelf) as shelf:
            try:
                segments = shelf["segments"]
            except KeyError:
                # The cache is empty
                segments = []

        # Always include Standard segments (i.e.: Company ID = adsquare).
        company_ids = company_ids or []
        company_ids.append(self.STANDARD_COMPANY_ID)

        # Exclude company_ids that are either None or empty.
        company_ids[:] = [cid for cid in company_ids if cid]

        segment_list = []
        for segment in segments:
            if segment["company_id"] not in company_ids:
                continue
            if country_code and country_code not in [segment["country"], "ZZ"]:
                continue
            segment_list.append(segment)

        return segment_list

    @retry.Retry(deadline=300.0)
    def list_segments(self):
        """List all segments available.

        According to the documentation, there is no pagination on this endpoint, so we expect the
        full list to be returned with a single call.

        See: https://docs.adsquare.com/#!/enrichmentMetaApi/getEnrichmentAudiences_1
        """
        path = f"enrichmentMeta/audiences/{self.dsp_id}"
        response = self.request("get", path, data={"namev2": "true"})

        return [
            {
                "company_id": audience["companyId"],
                "country": audience["countryCode"],
                "cpm": audience["cpm"],
                "currency": audience["currency"],
                "id": audience["audienceId"],
                "name": audience["name"],
                "owner": (
                    "Standard"
                    if audience["companyId"] == self.STANDARD_COMPANY_ID
                    else "Custom"
                ),
                "type": audience["type"],
            }
            for audience in response["audiences"]
        ]

    def pause_config(self, config_id):
        """Pause the given configuration."""
        self.update_config(config_id=config_id, active=False)

    @retry.Retry(deadline=300.0)
    def register_webhook(self, config_id, disable=False, feedback_url=None):
        """Register a Feedback URL webhook with adsquare for the given configuration ID.

        The same method can be used to re-enable an existing/disabled webhook.
        """
        data = {
            "enabled": not disable,
            "method": "post",
            "contentType": "csv",
        }
        if feedback_url:
            data["feedbackURL"] = feedback_url

        if not disable and not feedback_url:
            raise ClientException("Cannot register a webhook without a URL")

        return self.request(
            "post", f"measurement/configs/{config_id}/feedback", data=data
        )

    def resume_config(self, config_id):
        """Resume the given configuration."""
        self.update_config(config_id=config_id, active=True)

    def store_segments(self):
        """Retrieve the list of segments, and then cache the results on a shelf.

        As no caching mechanism exists on the API, we simply override the content of the cache
        with the results from the list_segments() call.
        """
        segments = self.list_segments()
        with shelve.open(self.shelf) as shelf:
            shelf["segments"] = segments

    @retry.Retry(deadline=300.0)
    def update_config(self, config_id, active=None, start_date=None, end_date=None):
        """Update the given configuration ID.

        Only active and start/end dates can be changed.
        """
        data = {}

        if active is not None:
            data["active"] = active

        if start_date:
            data["validFrom"] = arrow.get(start_date).format(self.TIME_FORMAT)

        if end_date:
            data["validTo"] = arrow.get(end_date).format(self.TIME_FORMAT)

        return self.request("post", f"measurement/configs/{config_id}", data=data)

    @retry.Retry(deadline=300.0)
    def upload_config(self, config_id, points):
        """Upload a list of site locations to the given configuration.

        The points is expected to be a list of (lat, long) tuples as floating values.
        """
        data = ["id,lon,lat"]
        for i, point in enumerate(points):
            data.append(f"{i},{point[1]},{point[0]}")

        # Make sure the payload has a trailing newline
        data.append("")

        self.request(
            "put", f"measurement/configs/{config_id}/dataset/poi", data="\n".join(data)
        )
