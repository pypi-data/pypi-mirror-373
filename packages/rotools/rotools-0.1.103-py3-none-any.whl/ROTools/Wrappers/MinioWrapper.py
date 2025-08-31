import io
import json

from minio.commonconfig import CopySource
from minio.deleteobjects import DeleteObject
from minio.error import S3Error


class MinioWrapper:
    def __init__(self, minio_client, bucket_name=None):
        self.client = minio_client
        self.bucket_name = bucket_name

    def get_data(self, object_name):
        try:
            response = self.client.get_object(self.bucket_name, object_name)
            object_data = response.read()
            response.close()
            response.release_conn()
            return object_data
        except S3Error as err:
            if err.code == 'NoSuchKey':
                return None
            raise err

    def get_json(self, object_name):
        object_data = self.get_data(object_name)
        if object_data is None:
            return None
        return json.loads(object_data.decode('utf-8'))

    def object_exists(self, object_name):
        try:
            self.client.stat_object(self.bucket_name, object_name)
            return True
        except S3Error as err:
            if err.code == 'NoSuchKey':
                return False
            raise

    def list_objects(self, prefix=None, recursive=False):
        return self.client.list_objects(self.bucket_name, prefix=prefix, recursive=recursive)

    def get_metadata(self, object_name):
        stat = self.client.stat_object(self.bucket_name, object_name)
        return stat.metadata

    def put_json(self, object_name, json_obj, metadata=None, content_type="application/json"):
        json_str = json.dumps(json_obj, ensure_ascii=False, indent=2).encode("utf-8")
        self.put_object(object_name, json_str, metadata=metadata, content_type=content_type)

    @staticmethod
    def _get_data_bytes(data, content_type):
        return io.BytesIO(data), content_type

    def put_object(self, object_name, data, content_type, metadata=None):
        data_bytes, content_type = self._get_data_bytes(data, content_type)
        self.put_buffer(object_name, data_bytes=data_bytes, metadata=metadata, content_type=content_type)

    def put_buffer(self, object_name, data_bytes, content_type, metadata=None):
        _len = data_bytes.getbuffer().nbytes
        self.client.put_object(self.bucket_name, object_name, data_bytes, length=_len, content_type=content_type, metadata=metadata)
        obj = self.client.stat_object(self.bucket_name, object_name)
        if obj.object_name != object_name:
            raise Exception("put data error")

    def copy_object(self, source_object_name, destination_object_name):
        copy_source = CopySource(self.bucket_name, source_object_name)
        self.client.copy_object(self.bucket_name, destination_object_name, copy_source)

    def delete_dir(self, prefix):
        for error in self.delete_objects(prefix=prefix, recursive=True):
            raise Exception(f"Error deleting {error.object_name}: {error}")

    def delete_objects(self, prefix=None, recursive=False):
        to_delete = list(self.list_objects(prefix=prefix, recursive=recursive))
        to_delete = [DeleteObject(obj.object_name) for obj in to_delete]
        return self.client.remove_objects(self.bucket_name, to_delete)

    def delete_object(self, object_name=None):
        return self.client.remove_object(self.bucket_name, object_name)

    def create_bucket(self, bucket_name):
        bucket_name = bucket_name or self.bucket_name
        if not self.client.bucket_exists(bucket_name):
            self.client.make_bucket(bucket_name)
