# -*- coding: utf-8 -*-

"""
Abstract dataclass for EC2 instance.
"""

import typing as T
import enum
import dataclasses
from urllib import request
from func_args import resolve_kwargs, NOTHING
from iterproxy import IterProxy

if T.TYPE_CHECKING:  # pragma: no cover
    from boto_session_manager import BotoSesManager


def get_response(url: str) -> str:  # pragma: no cover
    """
    Get the text response from the url.
    """
    with request.urlopen(url) as response:
        return response.read().decode("utf-8").strip()


def get_instance_id() -> str:  # pragma: no cover
    """
    Get the EC2 instance id from the AWS EC2 metadata API.
    """
    url = "http://169.254.169.254/latest/meta-data/instance-id"
    return get_response(url).strip()


class EC2InstanceStatusEnum(str, enum.Enum):
    pending = "pending"
    running = "running"
    shutting_down = "shutting-down"
    terminated = "terminated"
    stopping = "stopping"
    stopped = "stopped"


@dataclasses.dataclass
class Ec2Instance:
    """
    Represent an EC2 instance.
    """

    id: str = dataclasses.field()
    status: str = dataclasses.field()
    public_ip: T.Optional[str] = dataclasses.field(default=None)
    private_ip: T.Optional[str] = dataclasses.field(default=None)
    vpc_id: T.Optional[str] = dataclasses.field(default=None)
    subnet_id: T.Optional[str] = dataclasses.field(default=None)
    security_groups: T.List[T.Dict[str, str]] = dataclasses.field(default_factory=list)
    image_id: T.Optional[str] = dataclasses.field(default=None)
    instance_type: T.Optional[str] = dataclasses.field(default=None)
    key_name: T.Optional[str] = dataclasses.field(default=None)
    tags: T.Dict[str, str] = dataclasses.field(default_factory=dict)
    data: T.Dict[str, T.Any] = dataclasses.field(default_factory=dict)

    @classmethod
    def from_dict(cls, dct: dict) -> "Ec2Instance":
        """
        Create an EC2 instance object from the ``describe_instances`` API response.

        Ref:

        - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2/client/describe_instances.html
        """
        return cls(
            id=dct["InstanceId"],
            status=dct["State"]["Name"],
            public_ip=dct.get("PublicIpAddress"),
            private_ip=dct.get("PrivateIpAddress"),
            vpc_id=dct.get("VpcId"),
            subnet_id=dct.get("SubnetId"),
            security_groups=dct.get("SecurityGroups", []),
            image_id=dct.get("ImageId"),
            instance_type=dct.get("InstanceType"),
            key_name=dct.get("KeyName"),
            tags={kv["Key"]: kv["Value"] for kv in dct.get("Tags", [])},
            data=dct,
        )

    def is_pending(self) -> bool:
        """ """
        return self.status == EC2InstanceStatusEnum.pending.value

    def is_running(self) -> bool:
        """ """
        return self.status == EC2InstanceStatusEnum.running.value

    def is_shutting_down(self) -> bool:
        """ """
        return self.status == EC2InstanceStatusEnum.shutting_down.value

    def is_terminated(self) -> bool:
        """ """
        return self.status == EC2InstanceStatusEnum.terminated.value

    def is_stopping(self) -> bool:
        """ """
        return self.status == EC2InstanceStatusEnum.stopping.value

    def is_stopped(self) -> bool:
        """ """
        return self.status == EC2InstanceStatusEnum.stopped.value

    def is_ready_to_stop(self) -> bool:
        """ """
        return self.is_running() is True

    def is_ready_to_start(self) -> bool:
        """ """
        return self.is_stopped() is True

    def start_instance(self, bsm: "BotoSesManager"):
        """ """
        return bsm.ec2_client.start_instances(
            InstanceIds=[self.id],
            DryRun=False,
        )

    def stop_instance(self, bsm: "BotoSesManager"):
        """ """
        return bsm.ec2_client.stop_instances(
            InstanceIds=[self.id],
            DryRun=False,
        )

    # --------------------------------------------------------------------------
    # more constructor methods
    # --------------------------------------------------------------------------
    @classmethod
    def _yield_dict_from_describe_instances_response(
        cls, res: dict
    ) -> T.Iterable["Ec2Instance"]:
        reservations = res.get("Reservations", [])
        if len(reservations):
            instances = reservations[0].get("Instances", [])
            if len(instances):
                for instance_dict in instances:
                    yield cls.from_dict(instance_dict)

    @classmethod
    def query(
        cls,
        bsm: "BotoSesManager",
        filters: T.List[dict] = NOTHING,
        instance_ids: T.List[str] = NOTHING,
    ) -> "Ec2InstanceIterProxy":
        """ """

        def run():
            paginator = bsm.ec2_client.get_paginator("describe_instances")
            response_iterator = paginator.paginate(
                **resolve_kwargs(
                    Filters=filters,
                    InstanceIds=instance_ids,
                    PaginationConfig={
                        "MaxItems": 9999,
                        "PageSize": 100,
                    },
                )
            )
            for response in response_iterator:
                yield from cls._yield_dict_from_describe_instances_response(response)

        return Ec2InstanceIterProxy(run())

    @classmethod
    def from_id(cls, bsm: "BotoSesManager", inst_id: str) -> T.Optional["Ec2Instance"]:
        """ """
        return cls.query(
            bsm,
            instance_ids=[inst_id],
        ).one_or_none()

    @classmethod
    def from_ec2_inside(
        cls, bsm: "BotoSesManager"
    ) -> T.Optional["Ec2Instance"]:  # pragma: no cover
        """ """
        instance_id = get_instance_id()
        return cls.query(
            bsm,
            instance_ids=[instance_id],
        ).one()

    @classmethod
    def from_tag_key_value(
        cls,
        bsm: "BotoSesManager",
        key: str,
        value: str,
    ) -> "Ec2InstanceIterProxy":
        """ """
        return cls.query(
            bsm,
            filters=[
                dict(Name=f"tag:{key}", Values=[value]),
            ],
        )

    @classmethod
    def from_ec2_name(
        cls,
        bsm: "BotoSesManager",
        name: str,
    ) -> "Ec2InstanceIterProxy":
        """ """
        return cls.from_tag_key_value(bsm, key="Name", value=name)


class Ec2InstanceIterProxy(IterProxy[Ec2Instance]):
    """ """

    pass
