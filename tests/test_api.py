# -*- coding: utf-8 -*-

from simple_aws_ec2 import api


def test():

    # top level API
    _ = api.CannotDetectOSTypeError
    _ = api.EC2InstanceStatusEnum
    _ = api.EC2InstanceStatusGroupEnum
    _ = api.EC2InstanceArchitectureEnum
    _ = api.Ec2InstanceHypervisorEnum
    _ = api.Ec2Instance
    _ = api.Ec2InstanceIterProxy
    _ = api.ImageTypeEnum
    _ = api.ImageStateEnum
    _ = api.ImageRootDeviceTypeEnum
    _ = api.ImageVirtualizationTypeEnum
    _ = api.ImageBootModeEnum
    _ = api.ImageOwnerGroupEnum
    _ = api.ImageOSTypeEnum
    _ = api.Image
    _ = api.ImageIterProxy
    _ = api.Eip
    _ = api.EipIterProxy

    _ = api.Ec2MetadataCache

    # attribute and method
    _ = api.Ec2Instance.is_pending
    _ = api.Ec2Instance.is_running
    _ = api.Ec2Instance.is_shutting_down
    _ = api.Ec2Instance.is_terminated
    _ = api.Ec2Instance.is_stopping
    _ = api.Ec2Instance.is_stopped
    _ = api.Ec2Instance.is_ready_to_stop
    _ = api.Ec2Instance.is_ready_to_start
    _ = api.Ec2Instance.start_instance
    _ = api.Ec2Instance.stop_instance
    _ = api.Ec2Instance.terminate_instance
    _ = api.Ec2Instance.wait_for_status
    _ = api.Ec2Instance.wait_for_running
    _ = api.Ec2Instance.wait_for_stopped
    _ = api.Ec2Instance.wait_for_terminated
    _ = api.Ec2Instance.query
    _ = api.Ec2Instance.from_id
    _ = api.Ec2Instance.from_ec2_inside
    _ = api.Ec2Instance.from_tag_key_value
    _ = api.Ec2Instance.from_ec2_name
    _ = api.Ec2Instance.get_ami_id
    _ = api.Ec2Instance.get_instance_id
    _ = api.Ec2Instance.get_instance_type
    _ = api.Ec2Instance.get_local_hostname
    _ = api.Ec2Instance.get_local_ipv4
    _ = api.Ec2Instance.get_public_hostname
    _ = api.Ec2Instance.get_public_ipv4
    _ = api.Ec2Instance.get_security_groups

    _ = api.Image.from_dict
    _ = api.Image.image_type_is_machine
    _ = api.Image.image_type_is_kernel
    _ = api.Image.image_type_is_ramdisk
    _ = api.Image.is_pending
    _ = api.Image.is_available
    _ = api.Image.is_invalid
    _ = api.Image.is_deregistered
    _ = api.Image.is_transient
    _ = api.Image.is_failed
    _ = api.Image.is_error
    _ = api.Image.image_root_device_type_is_ebs
    _ = api.Image.image_root_device_type_is_instance_store
    _ = api.Image.image_virtualization_type_is_hvm
    _ = api.Image.image_virtualization_type_is_paravirtual
    _ = api.Image.image_boot_mode_is_legacy_bios
    _ = api.Image.image_boot_mode_is_uefi
    _ = api.Image.image_boot_mode_is_uefi_preferred
    _ = api.Image.os_type
    _ = api.Image.is_amazon_linux_os
    _ = api.Image.is_cent_os_os
    _ = api.Image.is_debian_os
    _ = api.Image.is_fedora_os
    _ = api.Image.is_rhel_os
    _ = api.Image.is_suse_os
    _ = api.Image.is_ubuntu_os
    _ = api.Image.is_oracle_os
    _ = api.Image.is_bitnami_os
    _ = api.Image.is_other_os
    _ = api.Image.users
    _ = api.Image.query
    _ = api.Image.from_id
    _ = api.Image.from_tag_key_value
    _ = api.Image.from_image_name
    _ = api.Image.from_ec2_inside

    _ = api.Eip.from_dict
    _ = api.Eip.is_associated
    _ = api.Eip.query
    _ = api.Eip.from_id
    _ = api.Eip.from_public_ip


if __name__ == "__main__":
    from simple_aws_ec2.tests import run_cov_test

    run_cov_test(__file__, "simple_aws_ec2.api", preview=False)
