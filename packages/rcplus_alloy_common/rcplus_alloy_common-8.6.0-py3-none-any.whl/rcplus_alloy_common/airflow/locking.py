"""
Distributed locking implementation for Alloy Airflow DAGs based on S3
"""
import botocore

from airflow.models import BaseOperator
from airflow.exceptions import AirflowException
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.providers.amazon.aws.sensors.s3 import S3KeySensor

from rcplus_alloy_common.airflow.decorators import alloyize


class AcquireLockOperator(BaseOperator):
    """
    Custom operator to acquire S3-based lock. The implemented lock is the re-entrant lock.
    If the lock file already exists on S3 and its `lock_id` matches the provided `lock_id` then the lock is acquired.
    Otherwise (if lock's `lock_id` doesn't match the provided `lock_id`) the Airflow exception is raised.
    """

    def __init__(
        self,
        *,
        bucket: str,
        lock_key: str,
        tenant: str | None = None,
        lock_id: str | None = None,
        aws_conn_id: str = "aws_default",
        **kwargs,
    ):
        if not bucket or not lock_key:
            raise AirflowException("Required parameters: bucket, lock_key")

        super().__init__(**kwargs)
        self.bucket = bucket
        self.tenant = tenant
        if self.tenant and not lock_key.startswith(f"{self.tenant}/"):
            lock_key = f"{self.tenant}/{lock_key}"
        self.lock_key = lock_key
        self.lock_id = lock_id or self.dag_id
        self.aws_conn_id = aws_conn_id

    def execute(self, context):
        s3_hook = S3Hook(aws_conn_id=self.aws_conn_id)
        s3_object = s3_hook.head_object(self.lock_key, self.bucket)
        if s3_object is not None:
            lock_id = s3_hook.read_key(self.lock_key, self.bucket)
            if lock_id != self.lock_id:
                raise AirflowException(f"Failed to acquire the lock s3://{self.bucket}/{self.lock_key}")

        s3_hook.load_string(self.lock_id, self.lock_key, self.bucket, replace=True)
        self.log.info(f"Acquired the lock s3://{self.bucket}/{self.lock_key} for lock_id {self.lock_id}")


@alloyize
class AlloyAcquireLockOperator(AcquireLockOperator):
    """Alloy AcquireLockOperator"""


class WaitAcquireLockSensor(S3KeySensor):
    """
    Custom sensor to wait until it is possible to acquire a lock and acquire it immediately.
    The implemented lock is the re-entrant lock. If the lock file already exists on S3 and its `lock_id` matches
    the provided `lock_id` then the lock is acquired and sensor finishes.

    NOTE: the `wildcard_match` option for the original `S3KeySensor` is ignored.
    """

    def __init__(
        self,
        *args,
        tenant: str | None = None,
        lock_id: str | None = None,
        **kwargs
    ):
        if tenant and not kwargs["bucket_key"].startswith(f"{tenant}/"):
            kwargs["bucket_key"] = f"{tenant}/{kwargs['bucket_key']}"
        super().__init__(*args, **kwargs)
        self.lock_id = lock_id or self.dag_id

    def _check_key(self, key, **kwargs):  # NOTE: in airflow==2.10 context is introduced, therefore **kwargs
        self.log.info(f"Checking the lock s3://{self.bucket_name}/{key}")

        s3_hook = self.hook
        s3_object = s3_hook.head_object(key, self.bucket_name)
        if s3_object is None:
            s3_hook.load_string(self.lock_id, key, self.bucket_name, replace=True)
            self.log.info(f"Acquired the lock s3://{self.bucket_name}/{key}")
            return True

        try:
            lock_id = s3_hook.read_key(key, self.bucket_name)
            if lock_id == self.lock_id:
                s3_hook.load_string(self.lock_id, key, self.bucket_name, replace=True)
                self.log.info(
                    f"Re-acquire the lock s3://{self.bucket_name}/{key} because its lock_id {lock_id} is equal "
                    f"to the provided lock_id {self.lock_id}")
                return True
        except botocore.exceptions.ClientError as ex:
            # Looks like it isn't possible to catch the nice `NoSuchKey` exception from boto3 in Airflow
            if "An error occurred (404)" not in str(ex):
                # raise an exception if anything else then error 404 has happened.
                raise

            # An edge case when a lock content is about to read but the lock owner just released it so nothing
            # could be read. This is recoverable actually but I added this workaround just to avoid errors and
            # long waiting pauses.
            s3_hook.load_string(self.lock_id, key, self.bucket_name, replace=True)
            self.log.info(f"Acquired the lock s3://{self.bucket_name}/{key}")
            return True

        self.log.info(f"Wait for the lock s3://{self.bucket_name}/{key} to be released")
        return False


@alloyize
class AlloyWaitAcquireLockSensor(WaitAcquireLockSensor):
    """Alloy WaitAcquireLockSensor"""


class ReleaseLockOperator(BaseOperator):
    """
    Custom operator to release a lock from S3. The lock can be released only if a DAG "owns" the lock.
    The ownership is detected by lock's file content which is set to `lock_id`.
    In case of DAG the `lock_id` is DAG ID in most cases (but it can be any string value).
    If lock's `lock_id` doesn't match the provided `lock_id` the Airflow exception is raised.
    """

    def __init__(
        self,
        *,
        bucket: str,
        lock_key: str,
        tenant: str | None = None,
        lock_id: str | None = None,
        aws_conn_id: str = "aws_default",
        **kwargs,
    ):
        if not bucket or not lock_key:
            raise AirflowException("Required parameters: bucket, lock_key")

        super().__init__(**kwargs)
        self.bucket = bucket
        self.tenant = tenant
        if self.tenant and not lock_key.startswith(f"{self.tenant}/"):
            lock_key = f"{self.tenant}/{lock_key}"
        self.lock_key = lock_key
        self.lock_id = lock_id or self.dag_id
        self.aws_conn_id = aws_conn_id

    def execute(self, context):
        s3_hook = S3Hook(aws_conn_id=self.aws_conn_id)
        s3_object = s3_hook.head_object(self.lock_key, self.bucket)
        if s3_object is None:
            self.log.info(f"The lock s3://{self.bucket}/{self.lock_key} is released already")
            return

        lock_id = s3_hook.read_key(self.lock_key, self.bucket)
        if lock_id != self.lock_id:
            raise AirflowException(
                f"Failed to release the lock s3://{self.bucket}/{self.lock_key} because its "
                f"lock_id is {lock_id} but expected {self.lock_id}")

        s3_hook.delete_objects(bucket=self.bucket, keys=self.lock_key)
        self.log.info(f"Released the lock s3://{self.bucket}/{self.lock_key}")


@alloyize
class AlloyReleaseLockOperator(ReleaseLockOperator):
    """Alloy ReleaseLockOperator"""


class WaitReleaseLockSensor(S3KeySensor):
    """
    Custom sensor to wait until the lock is released. The implemented locks are re-entrant locks so a lock owner can
    ignore the lock immediately. The lock ownership is based on lock_id. See `AlloyAcquireLockOperator` and
    `AlloyReleaseLockOperator` for more details.

    NOTE: the `wildcard_match` option for the original `S3KeySensor` is ignored.
    """

    def __init__(
        self,
        *args,
        tenant: str | None = None,
        lock_id: str | None = None,
        **kwargs
    ):
        if tenant and not kwargs["bucket_key"].startswith(f"{tenant}/"):
            kwargs["bucket_key"] = f"{tenant}/{kwargs['bucket_key']}"
        super().__init__(*args, **kwargs)
        self.lock_id = lock_id or self.dag_id

    def _check_key(self, key, **kwargs):  # NOTE: in airflow==2.10 context is introduced, therefore **kwargs
        self.log.info(f"Checking the lock for s3://{self.bucket_name}/{key}")

        s3_hook = self.hook
        s3_object = s3_hook.head_object(key, self.bucket_name)
        if s3_object is None:
            return True

        lock_id = s3_hook.read_key(key, self.bucket_name)
        if lock_id == self.lock_id:
            self.log.info(
                f"Re-enter the lock s3://{self.bucket_name}/{key} because its lock_id {lock_id} "
                f"is equal to the provided lock_id {self.lock_id}")
            s3_hook.delete_objects(bucket=self.bucket_name, keys=key)
            return True

        return False


@alloyize
class AlloyWaitReleaseLockSensor(WaitReleaseLockSensor):
    """Alloy WaitReleaseLockSensor"""
