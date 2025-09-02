import os
from pathlib import Path

RBX_ENV = os.getenv("RBX_ENV", "dev")
RBX_PROJECT = f"{RBX_ENV}-platform-eu"

GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT")

MDM_PUBSUB_TOPIC = os.getenv("MDM_PUBSUB_TOPIC", "platform-notifications")
MDM_PAYLOAD_VERSION = 2

AWS_BUCKET = os.getenv("AWS_BUCKET")
AWS_REGION = os.getenv("AWS_REGION")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
