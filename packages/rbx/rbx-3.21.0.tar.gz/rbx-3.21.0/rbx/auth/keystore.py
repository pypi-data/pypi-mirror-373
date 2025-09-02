from dataclasses import asdict, dataclass, field, InitVar
import os
from unittest import mock

import google.auth.credentials
from google.api_core import retry
from google.api_core.exceptions import RetryError
from google.cloud.firestore import Client

from ..clients.retry import Retry
from ..exceptions import TransientException
from ..settings import RBX_PROJECT

default_retry = retry.Retry(initial=0.1, maximum=3.0, multiplier=1.3, deadline=10.0)


class Keystore:
    """Manages API Keys stored in Google Cloud Firestore (Native Mode)."""

    def __init__(self):
        # Use mocked credentials to interact with the Firestore emulator.
        if os.getenv("GAE_ENV", "").startswith("standard"):
            db = Client(project=RBX_PROJECT)
        else:
            credentials = mock.Mock(spec=google.auth.credentials.Credentials)
            db = Client(
                project=os.getenv("GOOGLE_CLOUD_PROJECT"), credentials=credentials
            )

        self.collection = db.collection("api_keys")
        self.inventory = db.collection("inventory")

    def _inventory(self, key, document):
        """Given a DocumentSnapshot, return the fully loaded Inventory object."""
        return Inventory(**{"key": key, "keystore": self, **document.to_dict()})

    def _key(self, document):
        """Given a DocumentSnapshot, return the fully loaded Key object."""
        return Key(**{"keystore": self, "key_id": document.id, **document.to_dict()})

    def add_campaign(self, campaign):
        """Add a campaign to the campaigns inventory."""
        self.add_campaigns([campaign])

    @Retry(deadline=120.0)
    def add_campaigns(self, campaigns):
        """Add campaigns to the campaigns inventory."""
        inventory = self.get_inventory()
        inventory.add(campaigns)

    @Retry(deadline=120.0)
    def create_key(
        self, email, name, campaigns=None, is_restricted=None, services=None
    ):
        """Make a new API key.

        A key is associated with a user via her email address. If a key already exists for that
        user, the key is updated instead.
        """
        key = self.get_key(email=email)
        if not key:
            key = {
                "campaigns": campaigns or [],
                "email": email,
                "is_restricted": is_restricted if is_restricted is not None else True,
                "name": name,
                "services": services if services is not None else ["*.*"],
                "status": "active",
            }

            try:
                _, ref = self.collection.add(key, retry=default_retry)
                key = self._key(ref.get(retry=default_retry))
            except RetryError as e:
                raise TransientException(e)
        else:
            key.update(
                **{
                    "campaigns": campaigns or key.campaigns,
                    "is_restricted": (
                        is_restricted
                        if is_restricted is not None
                        else key.is_restricted
                    ),
                    "name": name or key.name,
                    "services": services or key.services,
                    "status": "active",  # the key is resuscitated
                }
            )

        # Unrestricted keys get access to all inventory
        if not key.is_restricted:
            key.campaigns = self.get_campaigns()

        return key

    def get_campaigns(self):
        """List all campaigns in the inventory."""
        inventory = self.get_inventory()
        if not inventory:
            return []

        return inventory.values

    def get_inventory(self, key="campaigns"):
        """Retrieve a key from the inventory."""
        try:
            document = self.inventory.document(key).get(retry=default_retry)
        except RetryError as e:
            raise TransientException(e)

        if not document.exists:
            return Inventory(key=key, keystore=self)
        else:
            return self._inventory(key, document)

    def get_key(self, key_id=None, email=None):
        """Retrieve a key by ID or email."""
        key = None

        try:
            if key_id:
                document = self.collection.document(key_id).get(retry=default_retry)
                if document.exists:
                    key = self._key(document)

            if email:
                document = next(
                    self.collection.where("email", "==", email).stream(
                        retry=default_retry
                    ),
                    False,
                )
                if document:
                    key = self._key(document)
        except RetryError as e:
            raise TransientException(e)

        # Unrestricted keys get access to all inventory
        if key and not key.is_restricted:
            key.campaigns = self.get_campaigns()

        return key

    def update_key(self, key, attributes):
        """Set the new Key values in Firestore."""
        assert isinstance(key, Key), f"excepted rbx.auth.Key, got {type(key)}"
        document = self.collection.document(key.key_id)
        try:
            document.set(attributes, merge=True, retry=default_retry)
        except RetryError as e:
            raise TransientException(e)


@dataclass
class Inventory:
    key: InitVar[str]
    keystore: InitVar[Keystore]
    values: list = field(default_factory=list)

    def __post_init__(self, key, keystore):
        self.key = key
        self.keystore = keystore

    def add(self, added_values):
        values = set(self.values)
        values.update(set(added_values))
        document = self.keystore.inventory.document(self.key)
        try:
            document.set(
                {"values": sorted(list(values))}, merge=True, retry=default_retry
            )
        except RetryError as e:
            raise TransientException(e)


@dataclass
class Key:
    key_id: InitVar[str]
    keystore: InitVar[Keystore]
    email: str
    name: str
    campaigns: list = field(default_factory=list)
    is_restricted: bool = True
    services: list = field(default_factory=["*.*"])
    status: str = "active"

    def __post_init__(self, key_id, keystore):
        # These are defined as InitVar so that they are not part of the pickled data, and aren't
        # included in the to_dict() representation.
        self.key_id = key_id
        self.keystore = keystore

    def activate(self):
        self.update(status="active")

    def deactivate(self):
        self.update(status="inactive")

    def has_access(self, service, operation):
        """Check whether the service and operation are granted access by this Key."""
        if self.status != "active":
            return False

        operation_ns = operation.split(".")
        for grant in self.services:
            name, _, endpoint = grant.partition(".")

            if name == "*":
                return True

            elif name == service:
                try:
                    if all(
                        [
                            value == "*" or value == operation_ns[key]
                            for key, value in enumerate(endpoint.split("."))
                        ]
                    ):
                        return True

                except IndexError:
                    continue

        return False

    def to_dict(self):
        return asdict(self)

    def update(self, **kwargs):
        for key, value in kwargs.items():
            if key in self.__annotations__.keys() and key not in ("key_id", "keystore"):
                setattr(self, key, value)

        self.keystore.update_key(self, self.to_dict())
