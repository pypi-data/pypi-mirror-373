import datetime
from typing import NamedTuple


class S3File(NamedTuple):
    bucket: str
    file: str
    etag: str
    last_modified: datetime.datetime

    def __repr__(self):
        return f"<S3File(bucket='{self.bucket}'"

    def __str__(self):
        return f"s3://{self.bucket}/{self.file} - etag={self.etag} - last_modified={self.last_modified}"
