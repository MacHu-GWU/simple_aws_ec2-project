# -*- coding: utf-8 -*-

import pytest


def test():
    from simple_aws_ec2 import api

    _ = api.CannotDetectOSTypeError
    _ = api.EC2InstanceStatusEnum
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


if __name__ == "__main__":
    import os

    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
