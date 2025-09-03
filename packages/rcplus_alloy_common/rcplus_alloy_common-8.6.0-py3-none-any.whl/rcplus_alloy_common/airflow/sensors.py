from airflow.exceptions import AirflowException
from airflow.sensors.base import BaseSensorOperator
from airflow.providers.amazon.aws.sensors.sqs import SqsSensor
from airflow.providers.amazon.aws.hooks.base_aws import AwsBaseHook

from rcplus_alloy_common.airflow.decorators import alloyize


@alloyize
class AlloySqsSensor(SqsSensor):
    """Alloy Sqs Sensor"""


@alloyize
class AlloyAutoScalingGroupSensor(BaseSensorOperator):
    template_fields = ["autoscaling_group_name"]

    def __init__(self, *args, autoscaling_group_name, expected_capacity=None, **kwargs):
        if expected_capacity is not None and expected_capacity < 0:
            self.log.error(
                f"An incorrect expected capacity value {expected_capacity} detected."
                "Be sure to set "
                "a value equal or above 0 before using this sensor.")
            raise AirflowException("Incorrect AutoScalingGroup capacity value")
        self.autoscaling_group_name = autoscaling_group_name
        self.expected_capacity = expected_capacity
        super().__init__(*args, **kwargs)

    def poke(self, context):
        client = AwsBaseHook(client_type="autoscaling").get_client_type()
        response = client.describe_auto_scaling_groups(
            AutoScalingGroupNames=[
                self.autoscaling_group_name,
            ],
            MaxRecords=1,
        )

        if "AutoScalingGroups" in response and len(response["AutoScalingGroups"]) == 1:
            asg_data = response["AutoScalingGroups"][0]
            if asg_data["DesiredCapacity"] < 0:
                self.log.error(
                    f"The incorrect capacity value {asg_data['DesiredCapacity']} detected "
                    f"for {self.autoscaling_group_name} autoscaling group. Be sure to set "
                    f"a correct value before using this sensor.")
                raise AirflowException("Incorrect AutoScalingGroup capacity value")

            if self.expected_capacity is not None and asg_data["DesiredCapacity"] != self.expected_capacity:
                return False

            if len(asg_data["Instances"]) == asg_data["DesiredCapacity"]:
                in_service = [instance["LifecycleState"] == "InService" for instance in asg_data["Instances"]]
                if all(in_service):
                    instance_ids = [instance["InstanceId"] for instance in asg_data["Instances"]]
                    ec2_client = AwsBaseHook(client_type="ec2").get_client_type()
                    statuses = ec2_client.describe_instance_status(InstanceIds=instance_ids)["InstanceStatuses"]
                    are_running = [status["InstanceStatus"]["Status"] == "ok" for status in statuses]
                    return all(are_running)

        return False
