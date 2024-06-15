# -*- coding: utf-8 -*-

"""
Abstract dataclass for EC2 instance.
"""

import typing as T
import enum
import json
import dataclasses
from datetime import datetime
from urllib import request

from botocore.exceptions import ClientError
from func_args import resolve_kwargs, NOTHING
from iterproxy import IterProxy

from .vendor.waiter import Waiter
from .exc import StatusError

if T.TYPE_CHECKING:  # pragma: no cover
    from mypy_boto3_ec2.client import EC2Client


class CannotDetectOSTypeError(TypeError):
    """
    raised when unable to use the name and description to detect the OS type
    of the AMI.
    """

    pass


def get_response(url: str) -> str:  # pragma: no cover
    """
    Get the text response from the url.
    """
    with request.urlopen(url) as response:
        return response.read().decode("utf-8").strip()


def _get_metadata(name: str) -> str:  # pragma: no cover
    """
    Get the EC2 instance id from the AWS EC2 metadata API.

    Reference:

    - https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/instancedata-data-retrieval.html
    """
    url = f"http://169.254.169.254/latest/meta-data/{name}"
    return get_response(url).strip()


class EC2InstanceStatusEnum(str, enum.Enum):
    """
    EC2 instance status enumerations.

    See also: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/monitoring-instance-state-changes.html
    """

    pending = "pending"
    running = "running"
    shutting_down = "shutting-down"
    terminated = "terminated"
    stopping = "stopping"
    stopped = "stopped"


T_STATUS_ENUM_SET = T.Set[EC2InstanceStatusEnum]


class EC2InstanceStatusGroupEnum:
    """
    Aggregate EC2 instance status into logical groups.

    :var ended: status won't change anymore
    :var in_transition: status is in transition
    """

    ended: T_STATUS_ENUM_SET = {
        EC2InstanceStatusEnum.running,
        EC2InstanceStatusEnum.terminated,
        EC2InstanceStatusEnum.stopped,
    }

    in_transition: T_STATUS_ENUM_SET = {
        EC2InstanceStatusEnum.pending,
        EC2InstanceStatusEnum.shutting_down,
        EC2InstanceStatusEnum.stopping,
    }


class EC2InstanceArchitectureEnum(str, enum.Enum):
    """
    Ec2 instance architecture enumerations.
    """

    i386 = "i386"
    x86_64 = "x86_64"
    arm64 = "arm64"
    x86_64_mac = "x86_64_mac"
    arm64_mac = "arm64_mac"


class Ec2InstanceHypervisorEnum(str, enum.Enum):
    """
    Ec2 instance hypervisor enumerations.
    """

    ovm = "ovm"
    xen = "xen"


@dataclasses.dataclass
class Ec2Instance:
    """
    Represent an EC2 instance.
    """

    id: str = dataclasses.field()
    status: str = dataclasses.field()
    status_transition_reason: T.Optional[str] = dataclasses.field(default=None)
    public_ip: T.Optional[str] = dataclasses.field(default=None)
    private_ip: T.Optional[str] = dataclasses.field(default=None)
    public_dns_name: T.Optional[str] = dataclasses.field(default=None)
    private_dns_name: T.Optional[str] = dataclasses.field(default=None)
    vpc_id: T.Optional[str] = dataclasses.field(default=None)
    subnet_id: T.Optional[str] = dataclasses.field(default=None)
    security_groups: T.List[T.Dict[str, str]] = dataclasses.field(default_factory=list)
    image_id: T.Optional[str] = dataclasses.field(default=None)
    platform: T.Optional[str] = dataclasses.field(default=None)
    platform_details: T.Optional[str] = dataclasses.field(default=None)
    instance_type: T.Optional[str] = dataclasses.field(default=None)
    launch_time: T.Optional[datetime] = dataclasses.field(default=None)
    key_name: T.Optional[str] = dataclasses.field(default=None)
    architecture: T.Optional[str] = dataclasses.field(default=None)
    ebs_optimized: T.Optional[bool] = dataclasses.field(default=None)
    ena_support: T.Optional[bool] = dataclasses.field(default=None)
    hypervisor: T.Optional[str] = dataclasses.field(default=None)
    iam_instance_profile_arn: T.Optional[str] = dataclasses.field(default=None)
    iam_instance_profile_id: T.Optional[str] = dataclasses.field(default=None)
    instance_lifecycle: T.Optional[str] = dataclasses.field(default=None)
    root_device_name: T.Optional[str] = dataclasses.field(default=None)
    root_device_type: T.Optional[str] = dataclasses.field(default=None)
    spot_instance_request_id: T.Optional[str] = dataclasses.field(default=None)
    sriov_net_support: T.Optional[str] = dataclasses.field(default=None)
    virtualization_type: T.Optional[str] = dataclasses.field(default=None)
    boot_mode: T.Optional[str] = dataclasses.field(default=None)
    usage_operation: T.Optional[str] = dataclasses.field(default=None)
    usage_operation_update_time: T.Optional[datetime] = dataclasses.field(default=None)
    current_instance_boot_mode: T.Optional[str] = dataclasses.field(default=None)
    ipv6_address: T.Optional[str] = dataclasses.field(default=None)
    tags: T.Dict[str, str] = dataclasses.field(default_factory=dict)
    data: T.Dict[str, T.Any] = dataclasses.field(default_factory=dict)

    @classmethod
    def from_dict(cls, dct: dict):
        """
        Create an EC2 instance object from the ``describe_instances`` API response.

        Ref:

        - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2/client/describe_instances.html
        """
        return cls(
            id=dct["InstanceId"],
            status=dct["State"]["Name"],
            status_transition_reason=dct.get("StateTransitionReason"),
            public_ip=dct.get("PublicIpAddress"),
            private_ip=dct.get("PrivateIpAddress"),
            public_dns_name=dct.get("PublicDnsName"),
            private_dns_name=dct.get("PrivateDnsName"),
            vpc_id=dct.get("VpcId"),
            subnet_id=dct.get("SubnetId"),
            security_groups=dct.get("SecurityGroups", []),
            image_id=dct.get("ImageId"),
            platform=dct.get("Platform"),
            platform_details=dct.get("PlatformDetails"),
            instance_type=dct.get("InstanceType"),
            launch_time=dct.get("LaunchTime"),
            key_name=dct.get("KeyName"),
            architecture=dct.get("Architecture"),
            ebs_optimized=dct.get("EbsOptimized"),
            ena_support=dct.get("EnaSupport"),
            hypervisor=dct.get("Hypervisor"),
            iam_instance_profile_arn=dct.get("IamInstanceProfile", {}).get("Arn"),
            iam_instance_profile_id=dct.get("IamInstanceProfile", {}).get("Id"),
            instance_lifecycle=dct.get("InstanceLifecycle"),
            root_device_name=dct.get("RootDeviceName"),
            root_device_type=dct.get("RootDeviceType"),
            spot_instance_request_id=dct.get("SpotInstanceRequestId"),
            sriov_net_support=dct.get("SriovNetSupport"),
            virtualization_type=dct.get("VirtualizationType"),
            boot_mode=dct.get("BootMode"),
            usage_operation=dct.get("UsageOperation"),
            usage_operation_update_time=dct.get("UsageOperationUpdateTime"),
            current_instance_boot_mode=dct.get("CurrentInstanceBootMode"),
            ipv6_address=dct.get("Ipv6Address"),
            tags={kv["Key"]: kv["Value"] for kv in dct.get("Tags", [])},
            data=dct,
        )

    def is_pending(self) -> bool:
        """
        Check if EC2 instance is pending.
        """
        return self.status == EC2InstanceStatusEnum.pending.value

    def is_running(self) -> bool:
        """
        Check if EC2 instance is running.
        """
        return self.status == EC2InstanceStatusEnum.running.value

    def is_shutting_down(self) -> bool:
        """
        Check if EC2 instance is shutting down.
        """
        return self.status == EC2InstanceStatusEnum.shutting_down.value

    def is_terminated(self) -> bool:
        """
        Check if EC2 instance is terminated.
        """
        return self.status == EC2InstanceStatusEnum.terminated.value

    def is_stopping(self) -> bool:
        """
        Check if EC2 instance is stopping.
        """
        return self.status == EC2InstanceStatusEnum.stopping.value

    def is_stopped(self) -> bool:
        """
        Check if EC2 instance is stopped.
        """
        return self.status == EC2InstanceStatusEnum.stopped.value

    def is_ready_to_stop(self) -> bool:
        """
        Check if EC2 instance is ready to stop.
        """
        return self.is_running() is True

    def is_ready_to_start(self) -> bool:
        """
        Check if EC2 instance is ready to start.
        """
        return self.is_stopped() is True

    def start_instance(self, ec2_client: "EC2Client"):
        """
        Start instance.
        """
        return ec2_client.start_instances(
            InstanceIds=[self.id],
            DryRun=False,
        )

    def stop_instance(self, ec2_client: "EC2Client"):
        """
        Stop instance.
        """
        return ec2_client.stop_instances(
            InstanceIds=[self.id],
            DryRun=False,
        )

    def terminate_instance(self, ec2_client: "EC2Client"):
        """
        Terminate instance.
        """
        return ec2_client.terminate_instances(
            InstanceIds=[self.id],
            DryRun=False,
        )

    # --------------------------------------------------------------------------
    # Waiter
    # --------------------------------------------------------------------------
    def wait_for_status(
        self,
        ec2_client: "EC2Client",
        stop_status: T.Union[EC2InstanceStatusEnum, T.List[EC2InstanceStatusEnum]],
        delays: T.Union[int, float] = 10,
        timeout: T.Union[int, float] = 300,
        error_status: T.Optional[
            T.Union[EC2InstanceStatusEnum, T.List[EC2InstanceStatusEnum]]
        ] = None,
        indent: int = 0,
        verbose: bool = True,
    ) -> "Ec2Instance":  # pragma: no cover
        """
        wait until the EC2 instance reaches the specified status defined in
        ``stop_status``. If reaches any of ``error_status ``, raise error.

        :param ec2_client:
        :param stop_status: status to stop waiting
        :param delays: delay between each check
        :param timeout: timeout in seconds
        :param error_status: status to raise error
        :param indent: indent level for logging
        :param verbose: whether to print log

        :return: the :class:`Ec2Instance` representing the latest status.
        """
        if isinstance(stop_status, EC2InstanceStatusEnum):
            stop_status_set = {stop_status.value}
        else:
            stop_status_set = {status.value for status in stop_status}
        if error_status is None:
            error_status_set = set()
        elif isinstance(error_status, EC2InstanceStatusEnum):
            error_status_set = {error_status.value}
        else:
            error_status_set = {status.value for status in error_status}

        for attempt, elapse in Waiter(
            delays=delays,
            timeout=timeout,
            indent=indent,
            verbose=verbose,
        ):
            ec2_inst = self.from_id(ec2_client, self.id)
            if ec2_inst.status in stop_status_set:
                return ec2_inst
            elif ec2_inst.status in error_status_set:
                raise StatusError(f"stop because status reaches {ec2_inst.status!r}")
            else:
                pass

    def wait_for_running(
        self,
        ec2_client: "EC2Client",
        delays: T.Union[int, float] = 10,
        timeout: T.Union[int, float] = 300,
        indent: int = 0,
        verbose: bool = True,
    ) -> "Ec2Instance":  # pragma: no cover
        """
        Similar to :meth:`Ec2Instance.wait_for_status`, but wait for
        EC2 instance to reach "running" status.
        """
        return self.wait_for_status(
            ec2_client=ec2_client,
            stop_status=EC2InstanceStatusEnum.running,
            delays=delays,
            timeout=timeout,
            error_status=[
                EC2InstanceStatusEnum.shutting_down,
                EC2InstanceStatusEnum.terminated,
                EC2InstanceStatusEnum.stopping,
                EC2InstanceStatusEnum.stopped,
            ],
            indent=indent,
            verbose=verbose,
        )

    def wait_for_stopped(
        self,
        ec2_client: "EC2Client",
        delays: T.Union[int, float] = 10,
        timeout: T.Union[int, float] = 300,
        indent: int = 0,
        verbose: bool = True,
    ) -> "Ec2Instance":  # pragma: no cover
        """
        Similar to :meth:`Ec2Instance.wait_for_status`, but wait for
        EC2 instance to reach "stopped" status.
        """
        return self.wait_for_status(
            ec2_client=ec2_client,
            stop_status=EC2InstanceStatusEnum.stopped,
            delays=delays,
            timeout=timeout,
            error_status=[
                EC2InstanceStatusEnum.pending,
                EC2InstanceStatusEnum.running,
                EC2InstanceStatusEnum.shutting_down,
                EC2InstanceStatusEnum.terminated,
            ],
            indent=indent,
            verbose=verbose,
        )

    def wait_for_terminated(
        self,
        ec2_client: "EC2Client",
        delays: T.Union[int, float] = 10,
        timeout: T.Union[int, float] = 300,
        indent: int = 0,
        verbose: bool = True,
    ) -> "Ec2Instance":  # pragma: no cover
        """
        Similar to :meth:`Ec2Instance.wait_for_status`, but wait for
        EC2 instance to reach "terminated" status.
        """
        return self.wait_for_status(
            ec2_client=ec2_client,
            stop_status=EC2InstanceStatusEnum.terminated,
            delays=delays,
            timeout=timeout,
            error_status=[
                EC2InstanceStatusEnum.pending,
                EC2InstanceStatusEnum.running,
                EC2InstanceStatusEnum.stopping,
                EC2InstanceStatusEnum.stopped,
            ],
            indent=indent,
            verbose=verbose,
        )

    # --------------------------------------------------------------------------
    # more constructor methods
    # --------------------------------------------------------------------------
    @classmethod
    def _yield_dict_from_describe_instances_response(
        cls, res: dict
    ) -> T.Iterable["Ec2Instance"]:
        for reservation in res.get("Reservations", []):
            for instance_dict in reservation.get("Instances", []):
                yield cls.from_dict(instance_dict)

    @classmethod
    def query(
        cls,
        ec2_client: "EC2Client",
        filters: T.List[dict] = NOTHING,
        instance_ids: T.List[str] = NOTHING,
    ) -> "Ec2InstanceIterProxy":
        """
        A wrapper around ``ec2_client.describe_instances``.

        Multiple filters join with logic "AND", multiple values in a filter
        join with logic "OR".
        """

        def run():
            paginator = ec2_client.get_paginator("describe_instances")
            kwargs = resolve_kwargs(
                Filters=filters,
                InstanceIds=instance_ids,
                PaginationConfig={
                    "MaxItems": 9999,
                    "PageSize": 100,
                },
            )
            if instance_ids is not NOTHING:
                del kwargs["PaginationConfig"]
            response_iterator = paginator.paginate(**kwargs)
            for response in response_iterator:
                yield from cls._yield_dict_from_describe_instances_response(response)

        return Ec2InstanceIterProxy(run())

    @classmethod
    def from_id(
        cls,
        ec2_client: "EC2Client",
        inst_id: str,
    ) -> T.Optional["Ec2Instance"]:
        """
        Get ec2 instance details by it's id.
        """
        return cls.query(
            ec2_client=ec2_client,
            instance_ids=[inst_id],
        ).one_or_none()

    @classmethod
    def from_ec2_inside(
        cls,
        ec2_client: "EC2Client",
    ) -> T.Optional["Ec2Instance"]:  # pragma: no cover
        """
        Use ec2 metadata API to get the instance id.

        .. note::

            This function should only be called on an EC2 instance
        """
        instance_id = cls.get_instance_id()
        return cls.query(
            ec2_client=ec2_client,
            instance_ids=[instance_id],
        ).one()

    @classmethod
    def from_tag_key_value(
        cls,
        ec2_client: "EC2Client",
        key: str,
        value: T.Union[str, T.Iterable[str]],
    ) -> "Ec2InstanceIterProxy":
        """
        Query EC2 Instance by tag key and values.

        :param key: tag key
        :param value: tag value or values
        """
        if isinstance(value, str):
            values = [value]
        else:
            values = list(value)
        return cls.query(
            ec2_client=ec2_client,
            filters=[
                dict(Name=f"tag:{key}", Values=values),
            ],
        )

    @classmethod
    def from_ec2_name(
        cls,
        ec2_client: "EC2Client",
        name: T.Union[str, T.Iterable[str]],
    ) -> "Ec2InstanceIterProxy":
        """
        Get EC2 instance details by the ``tag:name``.
        """
        if isinstance(name, str):
            names = [name]
        else:
            names = name
        return cls.query(
            ec2_client=ec2_client,
            filters=[
                dict(Name=f"tag:Name", Values=names),
            ],
        )

    # --------------------------------------------------------------------------
    # Retrieve instance metadata
    # these methods should only be used within EC2 instance
    # --------------------------------------------------------------------------
    @classmethod
    def get_ami_id(cls) -> str:  # pragma: no cover
        """
        Get the AMI id of the EC2 instance. This method should only be used
        within EC2 instance.
        """
        return _get_metadata(name="ami-id")

    @classmethod
    def get_instance_id(cls) -> str:  # pragma: no cover
        """
        Get the instance id of the EC2 instance. This method should only be used
        within EC2 instance.
        """
        return _get_metadata(name="instance-id")

    @classmethod
    def get_instance_type(cls) -> str:  # pragma: no cover
        """
        Get the instance type of the EC2 instance. This method should only be used
        within EC2 instance.
        """
        return _get_metadata(name="instance-type")

    @classmethod
    def get_hostname(cls) -> str:  # pragma: no cover
        """
        Get the hostname of the EC2 instance. This method should only be used
        within EC2 instance.
        """
        return _get_metadata(name="hostname")

    @classmethod
    def get_local_hostname(cls) -> str:  # pragma: no cover
        """
        Get the local hostname of the EC2 instance. This method should only be used
        within EC2 instance.
        """
        return _get_metadata(name="local-hostname")

    @classmethod
    def get_local_ipv4(cls) -> str:  # pragma: no cover
        """
        Get the local ipv4 of the EC2 instance. This method should only be used
        within EC2 instance.
        """
        return _get_metadata(name="local-ipv4")

    @classmethod
    def get_public_hostname(cls) -> str:  # pragma: no cover
        """
        Get the public hostname of the EC2 instance. This method should only be used
        within EC2 instance.
        """
        return _get_metadata(name="public-hostname")

    @classmethod
    def get_public_ipv4(cls) -> str:  # pragma: no cover
        """
        Get the public ipv4 of the EC2 instance. This method should only be used
        within EC2 instance.
        """
        return _get_metadata(name="public-ipv4")

    @classmethod
    def get_security_groups(cls) -> T.List[str]:  # pragma: no cover
        """
        Get the security groups of the EC2 instance. This method should only be used
        within EC2 instance.
        """
        return _get_metadata(name="security-groups").splitlines()

    @classmethod
    def get_iam_info(cls) -> T.Dict[str, str]:  # pragma: no cover
        """
        Get the IAM info of the EC2 instance. This method should only be used
        within EC2 instance.

        Example response:

        .. code-block:: python

            {
                "Code" : "Success",
                "LastUpdated" : "2023-01-01T00:00:00Z",
                "InstanceProfileId" : "ABCD..."
                "InstanceProfileArn" : "arn:aws:iam::111122223333:instance-profile/profile-name",
            }
        """
        return json.loads(_get_metadata(name="iam/info"))

    @classmethod
    def get_placement_region(cls) -> str:  # pragma: no cover
        """
        Get the placement region of the EC2 instance. This method should only be used
        within EC2 instance.
        """
        return _get_metadata(name="placement/region")

    @classmethod
    def get_reservation_id(cls) -> str:  # pragma: no cover
        """
        Get the reservation id of the EC2 instance. This method should only be used
        within EC2 instance.
        """
        return _get_metadata(name="reservation-id")


class Ec2InstanceIterProxy(IterProxy[Ec2Instance]):
    """
    Advanced iterator proxy for :class:`Ec2Instance`.
    """


# ------------------------------------------------------------------------------
# AMI Image
# ------------------------------------------------------------------------------
class ImageTypeEnum(str, enum.Enum):
    """
    AMI Image type enumerations.
    """

    machine = "machine"
    kernel = "kernel"
    ramdisk = "ramdisk"


class ImageStateEnum(str, enum.Enum):
    """
    AMI Image state enumerations.
    """

    pending = "pending"
    available = "available"
    invalid = "invalid"
    deregistered = "deregistered"
    transient = "transient"
    failed = "failed"
    error = "error"
    disabled = "disabled"


class ImageRootDeviceTypeEnum(str, enum.Enum):
    """
    AMI Image root device type enumerations.
    """

    ebs = "ebs"
    instance_store = "instance-store"


class ImageVirtualizationTypeEnum(str, enum.Enum):
    """
    AMI Image virtualization type enumerations.
    """

    hvm = "hvm"
    paravirtual = "paravirtual"


class ImageBootModeEnum(str, enum.Enum):
    """
    AMI Image boot mode enumerations.
    """

    legacy_bios = "legacy-bios"
    uefi = "uefi"
    uefi_preferred = "uefi-preferred"


class ImageOwnerGroupEnum(str, enum.Enum):
    """
    AMI Image owner group enumerations.
    """

    self = "self"
    amazon = "amazon"
    aws_marketplace = "aws-marketplace"


type_to_users: T.Dict[str, T.List[str]] = {
    "AmazonLinux": ["ec2-user"],
    "CentOS": ["centos", "ec2-user"],
    "Debian": ["admin"],
    "Fedora": ["fedora", "ec2-user"],
    "RHEL": ["ec2-user", "root"],
    "SUSE": ["ec2-user", "root"],
    "Ubuntu": ["ubuntu"],
    "Oracle": ["ec2-user"],
    "Bitnami": ["bitnami"],
    "Other": ["unknown"],
}


class ImageOSTypeEnum(str, enum.Enum):
    """
    Reference:

    - Default user name for AMI: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/connection-prereqs.html#connection-prereqs-get-info-about-instance
    """

    AmazonLinux = "AmazonLinux"
    CentOS = "CentOS"
    Debian = "Debian"
    Fedora = "Fedora"
    RHEL = "RHEL"
    SUSE = "SUSE"
    Ubuntu = "Ubuntu"
    Oracle = "Oracle"
    Bitnami = "Bitnami"
    Other = "Other"

    @property
    def users(self) -> T.List[str]:
        return type_to_users[self.value]


@dataclasses.dataclass
class Image:
    """
    Represent an AMI image.
    """

    id: str = dataclasses.field()
    image_location: T.Optional[str] = dataclasses.field(default=None)
    image_type: T.Optional[str] = dataclasses.field(default=None)
    architecture: T.Optional[str] = dataclasses.field(default=None)
    creation_date: T.Optional[str] = dataclasses.field(default=None)
    public: T.Optional[bool] = dataclasses.field(default=None)
    kernel_id: T.Optional[str] = dataclasses.field(default=None)
    owner_id: T.Optional[str] = dataclasses.field(default=None)
    platform: T.Optional[str] = dataclasses.field(default=None)
    platform_details: T.Optional[str] = dataclasses.field(default=None)
    usage_operation: T.Optional[str] = dataclasses.field(default=None)
    ramdisk_id: T.Optional[str] = dataclasses.field(default=None)
    state: T.Optional[str] = dataclasses.field(default=None)
    state_reason_code: T.Optional[str] = dataclasses.field(default=None)
    state_reason_message: T.Optional[str] = dataclasses.field(default=None)
    description: T.Optional[str] = dataclasses.field(default=None)
    ena_support: T.Optional[bool] = dataclasses.field(default=None)
    hypervisor: T.Optional[str] = dataclasses.field(default=None)
    image_owner_alias: T.Optional[str] = dataclasses.field(default=None)
    name: T.Optional[str] = dataclasses.field(default=None)
    root_device_name: T.Optional[str] = dataclasses.field(default=None)
    root_device_type: T.Optional[str] = dataclasses.field(default=None)
    sriov_net_support: T.Optional[str] = dataclasses.field(default=None)
    virtualization_type: T.Optional[str] = dataclasses.field(default=None)
    boot_mode: T.Optional[str] = dataclasses.field(default=None)
    tpm_support: T.Optional[str] = dataclasses.field(default=None)
    deprecation_time: T.Optional[str] = dataclasses.field(default=None)
    imds_support: T.Optional[str] = dataclasses.field(default=None)
    tags: T.Dict[str, str] = dataclasses.field(default_factory=dict)
    data: T.Dict[str, T.Any] = dataclasses.field(default_factory=dict)

    @classmethod
    def from_dict(cls, dct: dict):
        """
        Create an AMI Image object from the ``describe_images`` API response.

        Ref:

        - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2/client/describe_images.html
        """
        return cls(
            id=dct["ImageId"],
            image_location=dct.get("ImageLocation"),
            image_type=dct.get("ImageType"),
            architecture=dct.get("Architecture"),
            creation_date=dct.get("CreationDate"),
            public=dct.get("Public"),
            kernel_id=dct.get("KernelId"),
            owner_id=dct.get("OwnerId"),
            platform=dct.get("Platform"),
            platform_details=dct.get("PlatformDetails"),
            usage_operation=dct.get("UsageOperation"),
            ramdisk_id=dct.get("RamdiskId"),
            state=dct.get("State"),
            state_reason_code=dct.get("StateReason", {}).get("Code"),
            state_reason_message=dct.get("StateReason", {}).get("Message"),
            description=dct.get("Description"),
            ena_support=dct.get("EnaSupport"),
            hypervisor=dct.get("Hypervisor"),
            image_owner_alias=dct.get("ImageOwnerAlias"),
            name=dct.get("Name"),
            root_device_name=dct.get("RootDeviceName"),
            root_device_type=dct.get("RootDeviceType"),
            sriov_net_support=dct.get("SriovNetSupport"),
            virtualization_type=dct.get("VirtualizationType"),
            boot_mode=dct.get("BootMode"),
            tpm_support=dct.get("TpmSupport"),
            deprecation_time=dct.get("DeprecationTime"),
            imds_support=dct.get("ImdsSupport"),
            tags={kv["Key"]: kv["Value"] for kv in dct.get("Tags", [])},
            data=dct,
        )

    def image_type_is_machine(self) -> bool:
        """
        Check if the image type is machine.
        """
        return self.image_type == ImageTypeEnum.machine.value

    def image_type_is_kernel(self) -> bool:
        """
        Check if the image type is kernel.
        """
        return self.image_type == ImageTypeEnum.kernel.value

    def image_type_is_ramdisk(self) -> bool:
        """
        Check if the image type is ramdisk.
        """
        return self.image_type == ImageTypeEnum.ramdisk.value

    def is_pending(self) -> bool:
        """
        Check if the image status is pending.
        """
        return self.state == ImageStateEnum.pending.value

    def is_available(self) -> bool:
        """
        Check if the image status is available.
        """
        return self.state == ImageStateEnum.available.value

    def is_invalid(self) -> bool:
        """
        Check if the image status is invalid.
        """
        return self.state == ImageStateEnum.invalid.value

    def is_deregistered(self) -> bool:
        """
        Check if the image status is deregistered.
        """
        return self.state == ImageStateEnum.deregistered.value

    def is_transient(self) -> bool:
        """
        Check if the image status is transient.
        """
        return self.state == ImageStateEnum.transient.value

    def is_failed(self) -> bool:
        """
        Check if the image status is failed.
        """
        return self.state == ImageStateEnum.failed.value

    def is_error(self) -> bool:
        """
        Check if the image status is error.
        """
        return self.state == ImageStateEnum.error.value

    def is_disabled(self) -> bool:
        """
        Check if the image status is disabled.
        """
        return self.state == ImageStateEnum.disabled.value

    def image_root_device_type_is_ebs(self) -> bool:
        """
        Check if the image root device type is ebs.
        """
        return self.root_device_type == ImageRootDeviceTypeEnum.ebs.value

    def image_root_device_type_is_instance_store(self) -> bool:
        """
        Check if the image root device type is instance store.
        """
        return self.root_device_type == ImageRootDeviceTypeEnum.instance_store.value

    def image_virtualization_type_is_hvm(self) -> bool:
        """
        Check if the image virtualization type is hvm.
        """
        return self.virtualization_type == ImageVirtualizationTypeEnum.hvm.value

    def image_virtualization_type_is_paravirtual(self) -> bool:
        """
        Check if the image virtualization type is paravirtual.
        """
        return self.virtualization_type == ImageVirtualizationTypeEnum.paravirtual.value

    def image_boot_mode_is_legacy_bios(self) -> bool:
        """
        Check if the image boot mode is legacy bios.
        """
        return self.boot_mode == ImageBootModeEnum.legacy_bios.value

    def image_boot_mode_is_uefi(self) -> bool:
        """
        Check if the image boot mode is uefi.
        """
        return self.boot_mode == ImageBootModeEnum.uefi.value

    def image_boot_mode_is_uefi_preferred(self) -> bool:
        """
        Check if the image boot mode is uefi preferred.
        """
        return self.boot_mode == ImageBootModeEnum.uefi_preferred.value

    @property
    def os_type(self) -> ImageOSTypeEnum:  # pragma: no cover
        """
        Try to use the image name and description to determine the OS type.

        If the OS type cannot be determined, raise :class:`CannotDetectOSTypeError`.
        """
        if self.name.startswith("al"):
            if self.description is not None:
                if self.description.startswith("Amazon Linux"):
                    return ImageOSTypeEnum.AmazonLinux
        elif self.name.startswith("ubuntu"):
            if self.description is not None:
                if "Ubuntu" in self.description:
                    return ImageOSTypeEnum.Ubuntu
        elif self.name.startswith("RHEL"):
            if self.description is not None:
                if self.description.startswith("RHEL"):
                    return ImageOSTypeEnum.RHEL
        elif self.name.startswith("debian"):
            if self.description is not None:
                if self.description.startswith("Debian"):
                    return ImageOSTypeEnum.Debian
        elif self.name.startswith("suse"):
            if self.description is not None:
                if self.description.startswith("SUSE"):
                    return ImageOSTypeEnum.SUSE
        elif "fedora" in self.name.lower():
            if self.description is not None:
                if "fedora" in self.description.lower():
                    return ImageOSTypeEnum.Fedora
        elif "centos" in self.name.lower():
            if self.description is not None:
                if "centos" in self.description.lower():
                    return ImageOSTypeEnum.CentOS
        elif "oracle" in self.name.lower():
            if self.description is not None:
                if "oracle" in self.description.lower():
                    return ImageOSTypeEnum.Oracle
        elif "bitnami" in self.name.lower():
            if self.description is not None:
                if "bitnami" in self.description.lower():
                    return ImageOSTypeEnum.Bitnami
        else:
            raise CannotDetectOSTypeError

        raise CannotDetectOSTypeError

    def is_amazon_linux_os(self) -> bool:  # pragma: no cover
        """
        Check if the image OS is Amazon Linux.
        """
        return self.os_type is ImageOSTypeEnum.AmazonLinux

    def is_centos_os(self) -> bool:  # pragma: no cover
        """
        Check if the image OS is CentOS.
        """
        return self.os_type is ImageOSTypeEnum.CentOS

    is_cent_os_os = is_centos_os  # for backward compatibility

    def is_debian_os(self) -> bool:  # pragma: no cover
        """
        Check if the image OS is Debian.
        """
        return self.os_type is ImageOSTypeEnum.Debian

    def is_fedora_os(self) -> bool:  # pragma: no cover
        """
        Check if the image OS is Fedora.
        """
        return self.os_type is ImageOSTypeEnum.Fedora

    def is_rhel_os(self) -> bool:  # pragma: no cover
        """
        Check if the image OS is RHEL.
        """
        return self.os_type is ImageOSTypeEnum.RHEL

    def is_suse_os(self) -> bool:  # pragma: no cover
        """
        Check if the image OS is SUSE.
        """
        return self.os_type is ImageOSTypeEnum.SUSE

    def is_ubuntu_os(self) -> bool:  # pragma: no cover
        """
        Check if the image OS is Ubuntu.
        """
        return self.os_type is ImageOSTypeEnum.Ubuntu

    def is_oracle_os(self) -> bool:  # pragma: no cover
        """
        Check if the image OS is Oracle.
        """
        return self.os_type is ImageOSTypeEnum.Oracle

    def is_bitnami_os(self) -> bool:  # pragma: no cover
        """
        Check if the image OS is Bitnami.
        """
        return self.os_type is ImageOSTypeEnum.Bitnami

    def is_other_os(self) -> bool:  # pragma: no cover
        """
        Check if the image OS is other.
        """
        return self.os_type is ImageOSTypeEnum.Other

    @property
    def users(self) -> T.List[str]:
        """
        Return the potential default user names for the Image. It try to use
        the image name and description to determine the OS type.
        If the OS type cannot be determined, raise :class:`CannotDetectOSTypeError`.
        """
        return self.os_type.users

    @property
    def ebs_snapshot_id_list(self) -> T.List[str]:
        """
        Get the list of snapshot ids associated with the AMI.
        """
        snapshot_id_list = []
        for dct in self.data.get("BlockDeviceMappings", []):
            snapshot_id = dct.get("Ebs", {}).get("SnapshotId")
            if snapshot_id:
                snapshot_id_list.append(snapshot_id)
        return snapshot_id_list

    # --------------------------------------------------------------------------
    # more constructor methods
    # --------------------------------------------------------------------------
    @classmethod
    def _yield_dict_from_describe_images_response(
        cls,
        res: dict,
    ) -> T.Iterable["Image"]:
        for image_dict in res.get("Images", []):
            yield cls.from_dict(image_dict)

    @classmethod
    def query(
        cls,
        ec2_client: "EC2Client",
        filters: T.List[dict] = NOTHING,
        image_ids: T.List[str] = NOTHING,
        executable_users: T.List[str] = NOTHING,
        owners: T.List[str] = NOTHING,
        include_deprecated: bool = NOTHING,
    ) -> "ImageIterProxy":
        """
        A wrapper around ``ec2_client.describe_images``.

        Multiple filters join with logic "AND", multiple values in a filter
        join with logic "OR".
        """

        def run():
            paginator = ec2_client.get_paginator("describe_images")
            kwargs = resolve_kwargs(
                ExecutableUsers=executable_users,
                Filters=filters,
                ImageIds=image_ids,
                Owners=owners,
                IncludeDeprecated=include_deprecated,
                PaginationConfig={
                    "MaxItems": 9999,
                    "PageSize": 100,
                },
            )
            if image_ids is not NOTHING:
                del kwargs["PaginationConfig"]
            response_iterator = paginator.paginate(**kwargs)
            for response in response_iterator:
                yield from cls._yield_dict_from_describe_images_response(response)

        return ImageIterProxy(run())

    @classmethod
    def from_id(
        cls,
        ec2_client: "EC2Client",
        image_id: str,
    ) -> T.Optional["Image"]:
        """
        Get :class:`Image` object by the image id.
        """
        return cls.query(
            ec2_client=ec2_client,
            image_ids=[image_id],
        ).one_or_none()

    @classmethod
    def from_tag_key_value(
        cls,
        ec2_client: "EC2Client",
        key: str,
        value: T.Union[str, T.Iterable[str]],
    ) -> "ImageIterProxy":
        """
        Query AMI Image by tag key and values.

        :param key: tag key
        :param value: tag value or values
        """
        if isinstance(value, str):
            values = [value]
        else:
            values = list(value)
        return cls.query(
            ec2_client=ec2_client,
            filters=[
                dict(Name=f"tag:{key}", Values=values),
            ],
        )

    @classmethod
    def from_image_name(
        cls,
        ec2_client: "EC2Client",
        name: T.Union[str, T.Iterable[str]],
    ) -> "ImageIterProxy":
        """
        Get image details by the name of the AMI (provided during image creation).
        This name is not the ``tag:name``
        """
        if isinstance(name, str):
            names = [name]
        else:
            names = name
        return cls.query(
            ec2_client=ec2_client,
            filters=[
                dict(Name="name", Values=names),
            ],
        )

    @classmethod
    def from_ec2_inside(
        cls,
        ec2_client: "EC2Client",
    ) -> T.Optional["Image"]:  # pragma: no cover
        """
        Use ec2 metadata API to get the instance id, then get the image details

        .. note::

            This function should only be called on an EC2 instance
        """
        ec2_inst = Ec2Instance.from_ec2_inside(ec2_client=ec2_client)
        return cls.from_id(ec2_client=ec2_client, image_id=ec2_inst.image_id)

    def deregister(
        self,
        ec2_client: "EC2Client",
        delete_snapshot: bool = False,
        skip_prompt: bool = False,
        verbose: bool = False,
    ):
        """
        Deregister this image.

        :param delete_snapshot: if True, also delete the snapshot.
        :param skip_prompt: by default, it prompts to confirm. You can set it to
            True, to skip the prompt.
        :param verbose: whether to print log
        """
        if delete_snapshot:  # pragma: no cover
            if skip_prompt is False:
                entered = input(
                    "Are you sure you also wants to delete the snapshot of the "
                    f"AMI {self.id}? This cannot be undone! "
                    f"Enter 'YES' to proceed: "
                )
                if entered != "YES":
                    raise KeyboardInterrupt()

        ec2_client.deregister_image(ImageId=self.id)

        # ensure the image is deregistered
        for attempt, elapse in Waiter(
            delays=1,
            timeout=30,
            verbose=verbose,
        ):  # pragma: no cover
            try:
                images = self.query(ec2_client=ec2_client, image_ids=[self.id]).all()
                if len(images) == 0:
                    break
                if images[0].is_deregistered():
                    break
            except ClientError as e:
                if e.response["Error"]["Code"].startswith("InvalidAMIID"):
                    break
                else:  # pragma: no cover
                    raise e

        if delete_snapshot:  # pragma: no cover
            for snapshot_id in self.ebs_snapshot_id_list:
                ec2_client.delete_snapshot(SnapshotId=snapshot_id)

    # --------------------------------------------------------------------------
    # Waiter
    # --------------------------------------------------------------------------
    def wait_for_status(
        self,
        ec2_client: "EC2Client",
        stop_status: T.Union[ImageStateEnum, T.List[ImageStateEnum]],
        delays: T.Union[int, float] = 10,
        timeout: T.Union[int, float] = 300,
        error_status: T.Optional[
            T.Union[ImageStateEnum, T.List[ImageStateEnum]]
        ] = None,
        indent: int = 0,
        verbose: bool = True,
    ) -> "Image":  # pragma: no cover
        """
        wait until the AMI Image reaches the specified status defined in
        ``stop_status``. If reaches any of ``error_status ``, raise error.

        :param ec2_client:
        :param stop_status: status to stop waiting
        :param delays: delay between each check
        :param timeout: timeout in seconds
        :param error_status: status to raise error
        :param indent: indent level for logging
        :param verbose: whether to print log

        :return: the :class:`Image` representing the latest status.
        """
        if isinstance(stop_status, ImageStateEnum):
            stop_status_set = {stop_status.value}
        else:
            stop_status_set = {status.value for status in stop_status}
        if error_status is None:
            error_status_set = set()
        elif isinstance(error_status, ImageStateEnum):
            error_status_set = {error_status.value}
        else:
            error_status_set = {status.value for status in error_status}

        for attempt, elapse in Waiter(
            delays=delays,
            timeout=timeout,
            indent=indent,
            verbose=verbose,
        ):
            image = self.from_id(ec2_client, self.id)
            if image.state in stop_status_set:
                return image
            elif image.state in error_status_set:
                raise StatusError(f"stop because status reaches {image.state!r}")
            else:
                pass

    def wait_for_available(
        self,
        ec2_client: "EC2Client",
        delays: T.Union[int, float] = 10,
        timeout: T.Union[int, float] = 300,
        indent: int = 0,
        verbose: bool = True,
    ) -> "Image":  # pragma: no cover
        """
        Similar to :meth:`Image.wait_for_status`, but wait for
        AMI to reach "available" status.
        """
        return self.wait_for_status(
            ec2_client=ec2_client,
            stop_status=ImageStateEnum.available,
            delays=delays,
            timeout=timeout,
            error_status=[
                ImageStateEnum.invalid,
                ImageStateEnum.deregistered,
                ImageStateEnum.failed,
                ImageStateEnum.error,
                ImageStateEnum.disabled,
            ],
            indent=indent,
            verbose=verbose,
        )

    def wait_for_deregistered(
        self,
        ec2_client: "EC2Client",
        delays: T.Union[int, float] = 10,
        timeout: T.Union[int, float] = 300,
        indent: int = 0,
        verbose: bool = True,
    ) -> "Image":  # pragma: no cover
        """
        Similar to :meth:`Image.wait_for_status`, but wait for
        AMI to reach "deregistered" status.
        """
        return self.wait_for_status(
            ec2_client=ec2_client,
            stop_status=ImageStateEnum.deregistered,
            delays=delays,
            timeout=timeout,
            error_status=[
                ImageStateEnum.available,
                ImageStateEnum.invalid,
                ImageStateEnum.failed,
                ImageStateEnum.error,
                ImageStateEnum.disabled,
            ],
            indent=indent,
            verbose=verbose,
        )


class ImageIterProxy(IterProxy[Image]):
    """
    Advanced iterator proxy for :class:`Image`.
    """


# ------------------------------------------------------------------------------
# Elastic IP
# ------------------------------------------------------------------------------
@dataclasses.dataclass
class Eip:
    """
    Represent an Elastic IP Address.
    """

    allocation_id: str = dataclasses.field(default=None)
    public_ip: T.Optional[str] = dataclasses.field(default=None)
    association_id: T.Optional[str] = dataclasses.field(default=None)
    instance_id: T.Optional[str] = dataclasses.field(default=None)
    domain: T.Optional[str] = dataclasses.field(default=None)
    network_interface_id: T.Optional[str] = dataclasses.field(default=None)
    network_interface_owner_id: T.Optional[str] = dataclasses.field(default=None)
    private_ip_address: T.Optional[str] = dataclasses.field(default=None)
    public_ipv4_pool: T.Optional[str] = dataclasses.field(default=None)
    network_border_group: T.Optional[str] = dataclasses.field(default=None)
    customer_owned_ip: T.Optional[str] = dataclasses.field(default=None)
    customer_owned_ipv4_pool: T.Optional[str] = dataclasses.field(default=None)
    carrier_ip: T.Optional[str] = dataclasses.field(default=None)
    tags: T.Dict[str, str] = dataclasses.field(default_factory=dict)
    data: T.Dict[str, T.Any] = dataclasses.field(default_factory=dict)

    @classmethod
    def from_dict(cls, dct: dict):
        """
        Create an AMI Image object from the ``describe_images`` API response.

        Ref:

        - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2/client/describe_images.html
        """
        return cls(
            allocation_id=dct.get("AllocationId"),
            public_ip=dct.get("PublicIp"),
            association_id=dct.get("AssociationId"),
            instance_id=dct.get("InstanceId"),
            domain=dct.get("Domain"),
            network_interface_id=dct.get("NetworkInterfaceId"),
            network_interface_owner_id=dct.get("NetworkInterfaceOwnerId"),
            private_ip_address=dct.get("PrivateIpAddress"),
            public_ipv4_pool=dct.get("PublicIpv4Pool"),
            network_border_group=dct.get("NetworkBorderGroup"),
            customer_owned_ip=dct.get("CustomerOwnedIp"),
            customer_owned_ipv4_pool=dct.get("CustomerOwnedIpv4Pool"),
            carrier_ip=dct.get("CarrierIp"),
            tags={kv["Key"]: kv["Value"] for kv in dct.get("Tags", [])},
            data=dct,
        )

    def is_associated(self) -> bool:
        """
        Check if the EIP is associated with an instance.
        """
        return self.association_id is not None

    # --------------------------------------------------------------------------
    # more constructor methods
    # --------------------------------------------------------------------------
    @classmethod
    def _yield_dict_from_describe_addresses(
        cls,
        res: dict,
    ) -> T.Iterable["Eip"]:
        for eip_dict in res.get("Addresses", []):
            yield cls.from_dict(eip_dict)

    @classmethod
    def query(
        cls,
        ec2_client: "EC2Client",
        filters: T.List[dict] = NOTHING,
        allocation_ids: T.List[str] = NOTHING,
        public_ips: T.List[str] = NOTHING,
    ) -> "EipIterProxy":
        """
        A wrapper around ``ec2_client.describe_addresses``.

        Multiple filters join with logic "AND", multiple values in a filter
        join with logic "OR".
        """

        def run():
            kwargs = resolve_kwargs(
                Filters=filters,
                AllocationIds=allocation_ids,
                PublicIps=public_ips,
            )
            response = ec2_client.describe_addresses(**kwargs)
            yield from cls._yield_dict_from_describe_addresses(response)

        return EipIterProxy(run())

    @classmethod
    def from_id(
        cls,
        ec2_client: "EC2Client",
        allocation_id: str,
    ) -> T.Optional["Eip"]:
        """
        Get :class:`Eip` object by the allocation id.
        """
        return cls.query(
            ec2_client=ec2_client,
            allocation_ids=[allocation_id],
        ).one_or_none()

    @classmethod
    def from_public_ip(
        cls,
        ec2_client: "EC2Client",
        public_ip: str,
    ) -> T.Optional["Eip"]:
        """
        Get :class:`Eip` object by the public ip.
        """
        return cls.query(
            ec2_client=ec2_client,
            public_ips=[public_ip],
        ).one_or_none()


class EipIterProxy(IterProxy[Eip]):
    """
    Advanced iterator proxy for :class:`Eip`.
    """
