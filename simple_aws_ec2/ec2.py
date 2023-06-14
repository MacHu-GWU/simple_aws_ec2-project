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


def get_response(url: str) -> str:  # pragma: no cover
    """
    Get the text response from the url.
    """
    with request.urlopen(url) as response:
        return response.read().decode("utf-8").strip()


def get_instance_id() -> str:  # pragma: no cover
    """
    Get the EC2 instance id from the AWS EC2 metadata API.

    Reference:

    - https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/instancedata-data-retrieval.html
    """
    url = "http://169.254.169.254/latest/meta-data/instance-id"
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
    public_ip: T.Optional[str] = dataclasses.field(default=None)
    private_ip: T.Optional[str] = dataclasses.field(default=None)
    public_dns_name: T.Optional[str] = dataclasses.field(default=None)
    private_dns_name: T.Optional[str] = dataclasses.field(default=None)
    vpc_id: T.Optional[str] = dataclasses.field(default=None)
    subnet_id: T.Optional[str] = dataclasses.field(default=None)
    security_groups: T.List[T.Dict[str, str]] = dataclasses.field(default_factory=list)
    image_id: T.Optional[str] = dataclasses.field(default=None)
    instance_type: T.Optional[str] = dataclasses.field(default=None)
    key_name: T.Optional[str] = dataclasses.field(default=None)
    architecture: T.Optional[str] = dataclasses.field(default=None)
    hypervisor: T.Optional[str] = dataclasses.field(default=None)
    ipv6_address: T.Optional[str] = dataclasses.field(default=None)
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
            public_dns_name=dct.get("PublicDnsName"),
            private_dns_name=dct.get("PrivateDnsName"),
            vpc_id=dct.get("VpcId"),
            subnet_id=dct.get("SubnetId"),
            security_groups=dct.get("SecurityGroups", []),
            image_id=dct.get("ImageId"),
            instance_type=dct.get("InstanceType"),
            key_name=dct.get("KeyName"),
            architecture=dct.get("Architecture"),
            hypervisor=dct.get("Hypervisor"),
            ipv6_address=dct.get("Ipv6Address"),
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

    def start_instance(self, ec2_client):
        """ """
        return ec2_client.start_instances(
            InstanceIds=[self.id],
            DryRun=False,
        )

    def stop_instance(self, ec2_client):
        """ """
        return ec2_client.stop_instances(
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
        for reservation in res.get("Reservations", []):
            for instance_dict in reservation.get("Instances", []):
                yield cls.from_dict(instance_dict)

    @classmethod
    def query(
        cls,
        ec2_client,
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
    def from_id(cls, ec2_client, inst_id: str) -> T.Optional["Ec2Instance"]:
        """
        TODO: docstring
        """
        return cls.query(
            ec2_client=ec2_client,
            instance_ids=[inst_id],
        ).one_or_none()

    @classmethod
    def from_ec2_inside(
        cls,
        ec2_client,
    ) -> T.Optional["Ec2Instance"]:  # pragma: no cover
        """
        TODO: docstring
        """
        instance_id = get_instance_id()
        return cls.query(
            ec2_client=ec2_client,
            instance_ids=[instance_id],
        ).one()

    @classmethod
    def from_tag_key_value(
        cls,
        ec2_client,
        key: str,
        value: T.Union[str, T.Iterable[str]],
    ) -> "Ec2InstanceIterProxy":
        """
        TODO: docstring
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
        ec2_client,
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


class Ec2InstanceIterProxy(IterProxy[Ec2Instance]):
    """
    Advanced iterator proxy for :class:`Ec2Instance`.
    """


# ------------------------------------------------------------------------------
# AMI Image
# ------------------------------------------------------------------------------


class ImageTypeEnum(str, enum.Enum):
    machine = "machine"
    kernel = "kernel"
    ramdisk = "ramdisk"


class ImageStateEnum(str, enum.Enum):
    pending = "pending"
    available = "available"
    invalid = "invalid"
    deregistered = "deregistered"
    transient = "transient"
    failed = "failed"
    error = "error"


class ImageRootDeviceTypeEnum(str, enum.Enum):
    ebs = "ebs"
    instance_store = "instance-store"


class ImageVirtualizationTypeEnum(str, enum.Enum):
    hvm = "hvm"
    paravirtual = "paravirtual"


class ImageBootModeEnum(str, enum.Enum):
    legacy_bios = "legacy-bios"
    uefi = "uefi"
    uefi_preferred = "uefi-preferred"


class ImageOwnerGroupEnum(str, enum.Enum):
    self = "self"
    amazon = "amazon"
    aws_marketplace = "aws-marketplace"


@dataclasses.dataclass
class Image:
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
    def from_dict(cls, dct: dict) -> "Image":
        """
        Create an EC2 instance object from the ``describe_instances`` API response.

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
        """ """
        return self.image_type == ImageTypeEnum.machine.value

    def image_type_is_kernel(self) -> bool:
        """ """
        return self.image_type == ImageTypeEnum.kernel.value

    def image_type_is_ramdisk(self) -> bool:
        """ """
        return self.image_type == ImageTypeEnum.ramdisk.value

    def is_pending(self) -> bool:
        """ """
        return self.state == ImageStateEnum.pending.value

    def is_available(self) -> bool:
        """ """
        return self.state == ImageStateEnum.available.value

    def is_invalid(self) -> bool:
        """ """
        return self.state == ImageStateEnum.invalid.value

    def is_deregistered(self) -> bool:
        """ """
        return self.state == ImageStateEnum.deregistered.value

    def is_transient(self) -> bool:
        """ """
        return self.state == ImageStateEnum.transient.value

    def is_failed(self) -> bool:
        """ """
        return self.state == ImageStateEnum.failed.value

    def is_error(self) -> bool:
        """ """
        return self.state == ImageStateEnum.error.value

    def image_root_device_type_is_ebs(self) -> bool:
        return self.root_device_type == ImageRootDeviceTypeEnum.ebs.value

    def image_root_device_type_is_instance_store(self) -> bool:
        return self.root_device_type == ImageRootDeviceTypeEnum.instance_store.value

    # class ImageVirtualizationTypeEnum(str, enum.Enum):

    def image_virtualization_type_is_hvm(self) -> bool:
        return self.virtualization_type == ImageVirtualizationTypeEnum.hvm.value

    def image_virtualization_type_is_paravirtual(self) -> bool:
        return self.virtualization_type == ImageVirtualizationTypeEnum.paravirtual.value

    def image_boot_mode_is_legacy_bios(self) -> bool:
        return self.boot_mode == ImageBootModeEnum.legacy_bios.value

    def image_boot_mode_is_uefi(self) -> bool:
        return self.boot_mode == ImageBootModeEnum.uefi.value

    def image_boot_mode_is_uefi_preferred(self) -> bool:
        return self.boot_mode == ImageBootModeEnum.uefi_preferred.value

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
        ec2_client,
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
        ec2_client,
        image_id: str,
    ) -> T.Optional["Image"]:
        """
        TODO: docstring
        """
        return cls.query(
            ec2_client=ec2_client,
            image_ids=[image_id],
        ).one_or_none()

    @classmethod
    def from_tag_key_value(
        cls,
        ec2_client,
        key: str,
        value: T.Union[str, T.Iterable[str]],
    ) -> "ImageIterProxy":
        """
        TODO: docstring
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
        ec2_client,
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


class ImageIterProxy(IterProxy[Image]):
    """
    Advanced iterator proxy for :class:`Image`.
    """
