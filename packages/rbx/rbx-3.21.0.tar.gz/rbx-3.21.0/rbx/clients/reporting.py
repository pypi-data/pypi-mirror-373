import logging

from . import Client, HttpAuth

logger = logging.getLogger(__name__)


class ReportingClient(Client):
    """API Client for the Reporting Service."""

    def __init__(self, endpoint, token):
        super().__init__()
        self.ENDPOINT = endpoint
        self.token = token

    @property
    def auth(self):
        """The Reporting Service uses Digest Authentication."""
        return HttpAuth(self.token, key="X-RBX-TOKEN")

    def create_schedule(
        self,
        body,
        cron,
        format,
        name,
        recipients,
        reports,
        campaign: int = None,
        company: str = None,
        api_version=None,
    ):
        """Create a scheduled job.

        Return the job_id of the job just created.
        """
        data = {
            "body": body,
            "campaign": campaign,
            "company": company,
            "cron": cron,
            "format": format,
            "name": name,
            "recipients": recipients,
            "reports": reports,
        }

        if api_version is not None:
            data["api_version"] = api_version

        response = self._post("schedule", data=data)

        return response.get("job_id")

    def delete_schedule(self, job_id):
        """Create the scheduled job."""
        response = self._post("schedule/delete", data={"job_id": job_id})
        return response.get("job_id")

    def pause_schedule(self, job_id):
        """Pause the scheduled job."""
        response = self._post("schedule/pause", data={"job_id": job_id})
        return response.get("job_id")

    def resume_schedule(self, job_id):
        """Resume the scheduled job."""
        response = self._post("schedule/resume", data={"job_id": job_id})
        return response.get("job_id")

    def update_schedule(
        self,
        body,
        cron,
        format,
        job_id,
        name,
        recipients,
        reports,
        campaign: int = None,
        company: str = None,
        api_version=None,
    ):
        """Update the scheduled job."""
        data = {
            "body": body,
            "campaign": campaign,
            "company": company,
            "cron": cron,
            "format": format,
            "job_id": job_id,
            "name": name,
            "recipients": recipients,
            "reports": reports,
        }

        if api_version is not None:
            data["api_version"] = api_version

        response = self._post("schedule", data=data)

        return response.get("job_id")

    def get_report(
        self,
        breakdowns,
        metrics=None,
        custom_metrics=None,
        campaign=None,
        anomalies=None,
        filters=None,
        date_range=None,
        start_date=None,
        end_date=None,
        format=None,
        step=None,
        start=None,
        order_by=None,
        time_series=None,
        timezone=None,
    ):
        """Retrieve report data using the specified parameters.

        Parameters:
            breakdowns (list):
                The list of requested breakdowns.
            metrics (list):
                The list of requested metrics.
            custom_metrics (dict):
                A keyed object detailing the labels and units of any custom metrics.
                The key must be the position of the custom metric in the `metrics` parameter,
                beginning with `0`, as a string.

                By default, custom metrics are labelled `N/A` and use the `number` unit.
            campaign (int):
                The id of the Campaign.
            anomalies (str):
                The report anomalies flag is used to determine which variant of the metric to
                 return: exluding anomalies, including anomalies, or anomalies only.

                Valid values for this flag are: `excluded`, `included`, and `only`.
            filters (list[breakdown,operator,value]):
                Filter results on the given Breakdown having the value matching the given operator.
                Supported operators are: `eq`, `neq`, `in`, `nin`, and `like`
            date_range (string):
                A standard date range.
                One of `up_to_yesterday`, `campaign_life`, `today`, `yesterday`, `last_N_days`,
                `last_N_weeks`, `last_full_week`, or `last_full_month`.

                If omitted, all data up to yesterday midnight returned.
            start_date (string):
                The start date and time in ISO 8601 format.

                If omitted, the start date defaults to the oldest date on record.
                For a single campaign, that would be the first time the campaign received an event.
            end_date (string):
                The end date and time in ISO 8601 format.

                If omitted, the end date defaults to yesterday midnight.
            format (string):
                Specify what format the results should be returned in.
                Available formats are `csv`, `chartjs`, `tabular`, and `xlsx`.

                By default results are returned in JSON `tabular` format.
            step (int):
                The number of results to return. Use to limit the number of rows.

                By default all rows are returned.
            start (int):
                Use alongside `step` to fetch a specific set of results.
                `start` should be the number of the expected first result on the requested page.

                e.g.: using a `step` of 24, to get page 2, use `step=24, start=25`
            start (int):
                Use alongside `step` to fetch a specific set of results.
                `start` should be the number of the expected first result on the requested page.

                e.g.: using a `step` of 24, to get page 2, use `step=24, start=25`
            order_by (list[item,order]):
                Specify how the response should be ordered.

                The `order_by` parameter is expected to be a list of `item: sort` dictionary,
                where `item` is any Breakdown or Metric, and `sort` is either `ASC` or `DESC`.
            time_series (bool):
                Whether to return a time series.
            timezone (str):
                The time zone name of the request,
                If omitted, the time zone is assumed to be UTC.

        Returns:
            Dict.
            A dict response containing the "headers" and "rows", with each row ordered to match the
            order of the headers.
        """
        kwargs = locals()
        data = {}

        for label, value in kwargs.items():
            if label != "self" and value is not None:
                data[label] = value

        return self._post("report", data=data)

    def get_deal_facets(
        self,
        deals: [str],
        date_range: str = None,
        filters: [dict] = None,
        timezone: str = None,
        start_date: str = None,
        end_date: str = None,
    ) -> dict:
        """Retrieve deal traffic facets using the specified parameters.

        Parameters:

            deal_ids (list[str]):
                A list of deal ids to filter by.

            date_range (string):
                A standard relative dat range, in the form N{mhd}.
                Where `N` is the number of minutes (`m`), hours (`h`), or days (`d`), until now.

            filters (list[breakdown,operator,value]):
                Filter results on the given Breakdown having the value matching the given operator.
                Supported operators are: `eq`, `neq`, `in`, `nin`, and `like`

            start_date (string):
                The start date and time in ISO 8601 format.

            end_date (string):
                The end date and time in ISO 8601 format.

            timezone (str):
                The time zone name of the request,
                If omitted, the time zone is assumed to be UTC.

        Returns:
            Dict.
            A dict response containing the facets names and their values list.
        """
        kwargs = locals()
        data = {}

        for label, value in kwargs.items():
            if label != "self" and value is not None:
                data[label] = value

        return self._post("/traffic/deals", data=data)

    def get_traffic_facets(self, filters=None, date_range=None, timezone=None):
        """Retrieve traffic facets using the specified parameters.

        Parameters:

            filters (list[breakdown,operator,value]):
                Filter results on the given Breakdown having the value matching the given operator.
                Supported operators are: `eq`, `neq`, `in`, `nin`, and `like`

            date_range (string):
                A standard relative dat range, in the form N{mhd}.
                Where `N` is the number of minutes (`m`), hours (`h`), or days (`d`), until now.

            start_date (string):
                The start date and time in ISO 8601 format.

            end_date (string):
                The end date and time in ISO 8601 format.

            timezone (str):
                The time zone name of the request,
                If omitted, the time zone is assumed to be UTC.

        Returns:
            Dict.
            A dict response containing the facets names and their values list.
        """
        kwargs = locals()
        data = {}

        for label, value in kwargs.items():
            if label != "self" and value is not None:
                data[label] = value

        return self._post("traffic/facets", data=data)
