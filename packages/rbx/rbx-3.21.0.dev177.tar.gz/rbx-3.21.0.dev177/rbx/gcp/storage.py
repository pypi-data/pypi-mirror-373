import logging

from google.cloud.storage import Client

logger = logging.getLogger(__name__)


class Storage:
    """Provides functionality to upload/download content to/from GCS."""

    def __init__(self, project_id=None, bucket=None):
        self.client = Client()
        self.bucket = self.client.get_bucket(bucket or f"{project_id}.appspot.com")

    def copy(self, blob, new_name, bucket=None, public=False):
        logger.debug(f'Copying "{blob.name}" to "{new_name}"')
        new_blob = self.bucket.copy_blob(blob, bucket or self.bucket, new_name=new_name)
        if public:
            new_blob.make_public()
        return new_blob

    def download(self, location, raw=False):
        blob = self.bucket.blob(location)
        if blob.exists():
            logger.debug(f'Downloading from storage: "{blob.name}"')
            content = blob.download_as_string()
            if raw:
                return content
            else:
                return content.decode("utf-8")

    def list_objects(self, prefix=None):
        """Return an iterator of all objects in the bucket matching the prefix.

        The objects are returned as bytes.
        """
        if prefix is not None:
            prefix = prefix.lstrip("/")

        for blob in self.bucket.list_blobs(prefix=prefix):
            yield blob.download_as_string()

    def upload(self, content, location, content_type="text/plain", public=False):
        blob = self.bucket.blob(location.lstrip("/"))
        logger.debug(f'Uploading to storage: "{blob.name}"')
        blob.upload_from_string(content.encode("utf-8"), content_type=content_type)
        if public:
            blob.make_public()

        return blob

    def delete(self, location):
        """Delete a file from the storage.

        Args:
            location: The path to the file to delete.

        Returns:
            bool: True if the file was deleted, False if it didn't exist.
        """
        blob = self.bucket.blob(location.lstrip("/"))
        if blob.exists():
            logger.debug(f'Deleting from storage: "{blob.name}"')
            blob.delete()
            return True
        return False
