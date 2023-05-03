# -*- coding: utf-8 -*-

import os
import pytest
import moto
from boto_session_manager import BotoSesManager

from simple_aws_ec2.ec2 import Ec2Instance


class TestEc2:
    mock_ec2 = None
    bsm: BotoSesManager = None

    @classmethod
    def setup_ec2_resources(cls):
        image_id = cls.bsm.ec2_client.describe_images()["Images"][0]["ImageId"]

        cls.inst_id_1 = cls.bsm.ec2_client.run_instances(
            MinCount=1,
            MaxCount=1,
            ImageId=image_id,
        )["Instances"][0]["InstanceId"]

        cls.inst_id_2 = cls.bsm.ec2_client.run_instances(
            MinCount=1,
            MaxCount=1,
            ImageId=image_id,
            TagSpecifications=[
                dict(
                    ResourceType="instance",
                    Tags=[
                        dict(Key="Name", Value="my-server"),
                    ],
                )
            ],
        )["Instances"][0]["InstanceId"]

        cls.inst_id_3 = cls.bsm.ec2_client.run_instances(
            MinCount=1,
            MaxCount=1,
            ImageId=image_id,
            TagSpecifications=[
                dict(
                    ResourceType="instance",
                    Tags=[
                        dict(Key="Env", Value="dev"),
                    ],
                )
            ],
        )["Instances"][0]["InstanceId"]

    @classmethod
    def setup_class(cls):
        cls.mock_ec2 = moto.mock_ec2()
        cls.mock_ec2.start()
        cls.bsm = BotoSesManager(region_name="us-east-1")
        cls.setup_ec2_resources()

    @classmethod
    def teardown_class(cls):
        cls.mock_ec2.stop()

    def _test(self):
        inst_id_list = [
            self.inst_id_1,
            self.inst_id_2,
            self.inst_id_3,
        ]
        for inst_id in inst_id_list:
            ec2_inst = Ec2Instance.from_id(self.bsm, inst_id)
            assert ec2_inst.is_running() is True
            assert ec2_inst.is_pending() is False
            assert ec2_inst.is_shutting_down() is False
            assert ec2_inst.is_stopped() is False
            assert ec2_inst.is_stopping() is False
            assert ec2_inst.is_terminated() is False
            assert ec2_inst.is_ready_to_start() is False
            assert ec2_inst.is_ready_to_stop() is True
            assert ec2_inst.id == inst_id

        ec2_inst_list = Ec2Instance.from_ec2_name(self.bsm, "my-server").all()
        assert len(ec2_inst_list) == 1
        ec2_inst = ec2_inst_list[0]
        assert ec2_inst.id == self.inst_id_2
        assert ec2_inst.tags["Name"] == "my-server"

        ec2_inst.stop_instance(self.bsm)
        ec2_inst = Ec2Instance.from_ec2_name(self.bsm, "my-server").one()
        assert ec2_inst.is_running() is False
        assert ec2_inst.is_stopped() is True

        ec2_inst.start_instance(self.bsm)
        ec2_inst = Ec2Instance.from_ec2_name(self.bsm, "my-server").one()
        assert ec2_inst.is_stopped() is False
        assert ec2_inst.is_running() is True

        ec2_inst_list = Ec2Instance.from_tag_key_value(
            self.bsm, key="Env", value="dev"
        ).all()
        assert len(ec2_inst_list) == 1
        ec2_inst = ec2_inst_list[0]
        assert ec2_inst.id == self.inst_id_3
        assert ec2_inst.tags["Env"] == "dev"

    def test(self):
        self._test()


if __name__ == "__main__":
    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
