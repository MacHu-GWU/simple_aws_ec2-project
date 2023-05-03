# -*- coding: utf-8 -*-

import pytest


def test():
    from simple_aws_ec2 import api

    _ = api.EC2InstanceStatusEnum
    _ = api.Ec2Instance
    _ = api.Ec2InstanceIterproxy


if __name__ == "__main__":
    import os

    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
