from unittest import mock

from .keystore import Key, Keystore


def fake_key(
    key_id="6DSfBxFKsp3EDfUAETZn",
    campaigns=None,
    email="dev-mode@localhost.com",
    is_restricted=True,
    name=None,
    services=None,
    status="active",
):
    return Key(
        keystore=mock.Mock(spec_set=Keystore),
        key_id=key_id,
        campaigns=campaigns or [],
        email=email or "john.doe@rip.com",
        is_restricted=is_restricted,
        name=name or "John Doe",
        services=services if services is not None else ["*.*"],
        status=status,
    )


class KeystoreMock:
    def add_campaign(self, *args, **kwargs):
        return

    def add_campaigns(self, *args, **kwargs):
        return

    def create_key(
        self, email, name, campaigns=None, is_restricted=None, services=None
    ):
        return fake_key(
            key_id="6DSfBxFKsp3EDfUAETZn",
            name=name,
            email=email or "dev-mode@localhost.com",
            is_restricted=False,
        )

    def get_campaigns(self):
        return []

    def get_key(self, key_id=None, email=None, name=None):
        return fake_key(
            key_id=key_id or "6DSfBxFKsp3EDfUAETZn",
            name=name or "DEV Mode",
            email=email or "dev-mode@localhost.com",
            is_restricted=False,
        )

    def update_key(self, *args, **kwargs):
        return
