import json
from io import BytesIO
from django.conf import settings
from urllib3 import BaseHTTPResponse

from ..classes.singleton_meta import SingletonMeta


class ValarMinio(metaclass=SingletonMeta):

    def __init__(self, client, entity):
        self.client = client
        self.bucket_name = f'{settings.BASE_DIR.name}.{entity}'.replace('_', '-').lower()
        if client and not self.client.bucket_exists(self.bucket_name):
            self.client.make_bucket(self.bucket_name)
            self.client.set_bucket_policy(self.bucket_name, self.__generate_policy__())

    @staticmethod
    def get_object_name(_id, prop, file_name):
        return f"{_id}-{prop}-{file_name}"

    def upload(self, object_name, _bytes):
        file_data = BytesIO(_bytes)
        file_size = len(_bytes)  # file.siz
        self.client.put_object(
            bucket_name=self.bucket_name,
            object_name=object_name,
            data=file_data,
            length=file_size
        )
        return f'{self.bucket_name}/{object_name}'

    def remove(self, path):
        if path:
            bucket_name, object_name = path.split('/')
            self.client.remove_object(
                bucket_name=bucket_name,
                object_name=object_name
            )

    def read(self, object_name) -> BytesIO:
        ret: BaseHTTPResponse = self.client.get_object(
            bucket_name=self.bucket_name,
            object_name=object_name
        )
        return BytesIO(ret.read())

    def __generate_policy__(self):
        return json.dumps({
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "",
                    "Effect": "Allow",
                    "Principal": {"AWS": "*"},
                    "Action": "s3:GetBucketLocation",
                    "Resource": f"arn:aws:s3:::{self.bucket_name}"
                },
                {
                    "Sid": "",
                    "Effect": "Allow",
                    "Principal": {"AWS": "*"},
                    "Action": "s3:ListBucket",
                    "Resource": f"arn:aws:s3:::{self.bucket_name}"
                },
                {
                    "Sid": "",
                    "Effect": "Allow",
                    "Principal": {"AWS": "*"},
                    "Action": "s3:GetObject",
                    "Resource": f"arn:aws:s3:::{self.bucket_name}/*"
                },
                {
                    "Sid": "",
                    "Effect": "Allow",
                    "Principal": {"AWS": "*"},
                    "Action": "s3:PutObject",
                    "Resource": f"arn:aws:s3:::{self.bucket_name}/*"
                }
            ]})
