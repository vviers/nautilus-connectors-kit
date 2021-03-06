# GNU Lesser General Public License v3.0 only
# Copyright (C) 2020 Artefact
# licence-information@artefact.com
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 3 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
import click

from google.cloud import storage
from nck.commands.command import processor
from nck.readers.objectstorage_reader import ObjectStorageReader
from nck.utils.args import extract_args
from nck.helpers.google_base import GoogleBaseClass
import urllib


@click.command(name="read_gcs")
@click.option("--gcs-bucket", required=True)
@click.option("--gcs-prefix", required=True, multiple=True)
@click.option("--gcs-format", required=True, type=click.Choice(["csv", "gz"]))
@click.option("--gcs-dest-key-split", default=-1, type=int)
@click.option("--gcs-csv-delimiter", default=",")
@click.option("--gcs-csv-fieldnames", default=None)
@processor()
def gcs(**kwargs):
    return GCSReader(**extract_args("gcs_", kwargs))


class GCSReader(ObjectStorageReader, GoogleBaseClass):
    def __init__(self, bucket, prefix, format, dest_key_split=-1, **kwargs):
        super().__init__(
            bucket, prefix, format, dest_key_split, platform="GCS", **kwargs
        )

    def create_client(self, config):
        return storage.Client(
            credentials=self._get_credentials(), project=config.project_id
        )

    def create_bucket(self, client, bucket):
        return client.bucket(bucket)

    def list_objects(self, bucket, prefix):
        return bucket.list_blobs(prefix=prefix)

    @staticmethod
    def get_timestamp(_object):
        return _object.updated

    @staticmethod
    def get_key(_object):
        return urllib.parse.unquote(_object.path).split("o/", 1)[-1]

    @staticmethod
    def to_object(_object):
        return _object

    @staticmethod
    def download_object_to_file(_object, temp):
        _object.download_to_file(temp)
