import click
import logging

import boto3
from lib.commands.command import processor
from lib.readers.objectstorage_reader import ObjectStorageReader
from lib.utils.args import extract_args


@click.command(name="read_s3")
@click.option("--s3-bucket", required=True)
@click.option("--s3-prefix", required=True, multiple=True)
@click.option("--s3-format", required=True, type=click.Choice(['csv', 'gz']))
@click.option("--s3-csv-delimiter", default=",")
@click.option("--s3-csv-fieldnames", default=None)
@processor()
def s3(**kwargs):
    return S3Reader(**extract_args('s3_', kwargs))


class S3Reader(ObjectStorageReader):

    def __init__(self, bucket, prefix, format, **kwargs):
        super(S3Reader, self).__init__(bucket, prefix, format, platform="S3", **kwargs)

    def create_client(self, config):
        boto_config = {'region_name': config.REGION_NAME,
                       'aws_access_key_id': config.AWS_ACCESS_KEY_ID,
                       'aws_secret_access_key': config.AWS_SECRET_ACCESS_KEY}
        return boto3.resource('s3', **boto_config)

    def create_bucket(self, client, bucket):
        return client.Bucket(bucket)

    def list_objects(self, bucket, prefix):
        return bucket.objects.filter(Prefix=prefix)

    @staticmethod
    def get_timestamp(o):
        return o.last_modified

    @staticmethod
    def get_key(o):
        return o.key

    @staticmethod
    def to_object(o):
        return o.Object()

    @staticmethod
    def download_object_to_file(o, temp):
        o.download_fileobj(temp)
