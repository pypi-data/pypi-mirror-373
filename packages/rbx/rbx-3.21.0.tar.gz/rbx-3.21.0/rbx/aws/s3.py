import logging
import os

import boto3
import botocore

from rbx.exceptions import AWSException

logger = logging.getLogger(__name__)


class S3Bucket:
    """An AWS S3 Bucket.

    Wraps the boto3.Bucket class to provide a higher level of abstraction, as needed by the
    Platform.

    The main purpose of the create() and delete() method is to aid integration testing.
    We therefore skip any CORS or permission setting when creating buckets.
    In a production environment, these buckets are expected to already exist, and to have been
    configured accordingly.
    """

    def __init__(self, name, region):
        """The name may include the bucket prefix.

        e.g.: bucket-name/path/to/dir/

        In which case the prefix instance attribute will be automatically prefixed to all keys.
        """
        self.name, _, self.prefix = name.partition("/")
        if self.prefix and not self.prefix.endswith("/"):
            self.prefix += "/"
        self.region = region

        self.resource = boto3.resource("s3", region_name=self.region)
        self.bucket = self.resource.Bucket(self.name)

        self.create()

    def clone(self, source, dest):
        """Clone the given S3 key to the location given in 'dest'."""
        source_key = self.prefix + source
        dest_key = self.prefix + dest
        try:
            for key in self.bucket.objects.filter(Prefix=source_key):
                d = dest_key + key.key[len(source_key) :]
                copy_source = {"Bucket": self.name, "Key": key.key}
                self.bucket.copy(copy_source, d)

        except botocore.exceptions.ClientError as e:
            logger.error(e, extra=e.response)
            raise AWSException(e)

    def copy(self, filename, key, content_type="binary/octet-stream", download=False):
        """Copy a file to the given S3 key.

        The filename will be read, so filename is expected to be the path to the file itself.

        When download is True, we add the "ContentDisposition: attachment" header so that it makes
        browsers download the file when accessed directly.
        """
        content_type = (
            content_type or "binary/octet-stream"
        )  # Content-Type cannot be None
        options = {"ContentType": content_type}
        if download:
            options["ContentDisposition"] = "attachment"

        try:
            self.bucket.upload_file(filename, self.prefix + key, ExtraArgs=options)
        except botocore.exceptions.ClientError as e:
            logger.error(e, extra=e.response)
            raise AWSException(e)

    def create(self):
        """Create the S3 Bucket.

        Only create the bucket if it does not already exist.
        """
        if not self.exists():
            self.bucket = self.resource.create_bucket(
                Bucket=self.name,
                CreateBucketConfiguration={"LocationConstraint": self.region},
            )

    def delete(self):
        """Delete the S3 Bucket."""
        if self.exists():
            for key in self.bucket.objects.all():
                key.delete()

            self.bucket.delete()

    def delete_keys(self, path, startswith=None):
        """Delete keys from the S3 Bucket

        Will delete all keys in the Bucket given a key unless you specify a prefix, then it will
        only delete files which start with that particular prefix.
        """
        path_prefix = self.prefix + path
        deleted_keys = []

        try:
            for key in self.bucket.objects.filter(Prefix=path_prefix):
                if not startswith:
                    key.delete()
                    deleted_keys.append(key)
                elif key.key.startswith(os.path.join(path_prefix, startswith)):
                    key.delete()
                    deleted_keys.append(key)
            return deleted_keys
        except botocore.exceptions.ClientError as e:
            logger.error(e, extra=e.response)
            raise AWSException(e)

    def exists(self):
        """Check whether the Bucket exists in S3."""
        try:
            self.resource.meta.client.head_bucket(Bucket=self.name)
        except botocore.exceptions.ClientError as e:
            # If a client error is thrown, then check that it was a 404 error.
            # If it was a 404 error, then the bucket does not exist.
            error_code = e.response["Error"]["Code"]
            if error_code == "404":
                return False
            else:
                logger.error(e)

        return True

    def get_key(self, key):
        """Check whether the given key exists in the bucket.
        Will return the object or None.
        """
        object = self.bucket.Object(self.prefix + key)

        try:
            object.load()
        except botocore.exceptions.ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "404":
                return
            else:
                logger.error(e)
        else:
            return object

    def save(self, fileobj, key, content_type="binary/octet-stream", download=False):
        """Save a file-like object to the given S3 key.

        When download is True, we add the "ContentDisposition: attachment" header so that it makes
        browsers download the file when accessed directly.
        """
        # Content-Type cannot be None
        options = {"ContentType": content_type or "binary/octet-stream"}
        if download:
            options["ContentDisposition"] = "attachment"

        try:
            self.bucket.upload_fileobj(fileobj, self.prefix + key, ExtraArgs=options)
        except ValueError as e:
            raise AWSException(e)
        except botocore.exceptions.ClientError as e:
            logger.error(e, extra=e.response)
            raise AWSException(e)
