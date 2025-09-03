from airflow.utils.helpers import chunks
from airflow.exceptions import AirflowException
from airflow.providers.amazon.aws.hooks.s3 import S3Hook


class SilentS3Hook(S3Hook):
    """
    Custom S3Hook because the original hook is very noisy when deleting files on S3
    """

    def delete_objects(self, bucket, keys):
        if isinstance(keys, str):
            keys = [keys]

        s3 = self.get_conn()
        for chunk in chunks(keys, chunk_size=1000):
            response = s3.delete_objects(
                Bucket=bucket, Delete={"Objects": [{"Key": k} for k in chunk]}
            )
            if "Errors" in response:
                raise AirflowException(f"Failed to delete: {keys}")
