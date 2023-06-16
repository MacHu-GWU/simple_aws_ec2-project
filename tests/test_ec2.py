# -*- coding: utf-8 -*-

import os
import pytest
import moto
from boto_session_manager import BotoSesManager

from simple_aws_ec2.ec2 import (
    StatusError,
    EC2InstanceStatusEnum,
    Ec2Instance,
    Image,
    ImageOwnerGroupEnum,
    ImageOSTypeEnum,
)


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

        cls.image_id_1 = cls.bsm.ec2_client.create_image(
            Name="my-image-1",
            InstanceId=cls.inst_id_1,
            TagSpecifications=[
                dict(
                    ResourceType="image",
                    Tags=[
                        dict(Key="Env", Value="dev"),
                    ],
                )
            ],
        )["ImageId"]

    @classmethod
    def setup_class(cls):
        cls.mock_ec2 = moto.mock_ec2()
        cls.mock_ec2.start()
        cls.bsm = BotoSesManager(region_name="us-east-1")
        cls.setup_ec2_resources()

    @classmethod
    def teardown_class(cls):
        cls.mock_ec2.stop()

    def _test_ec2(self):
        inst_id_list = [
            self.inst_id_1,
            self.inst_id_2,
            self.inst_id_3,
        ]
        for inst_id in inst_id_list:
            ec2_inst = Ec2Instance.from_id(self.bsm.ec2_client, inst_id)
            assert ec2_inst.is_running() is True
            assert ec2_inst.is_pending() is False
            assert ec2_inst.is_shutting_down() is False
            assert ec2_inst.is_stopped() is False
            assert ec2_inst.is_stopping() is False
            assert ec2_inst.is_terminated() is False
            assert ec2_inst.is_ready_to_start() is False
            assert ec2_inst.is_ready_to_stop() is True
            assert ec2_inst.id == inst_id

        ec2_inst_list_1 = Ec2Instance.from_ec2_name(
            self.bsm.ec2_client, "my-server"
        ).all()
        ec2_inst_list_2 = Ec2Instance.from_ec2_name(
            self.bsm.ec2_client,
            ["my-server"],
        ).all()
        for ec2_inst_list in [ec2_inst_list_1, ec2_inst_list_2]:
            assert len(ec2_inst_list) == 1
            ec2_inst = ec2_inst_list[0]
            assert ec2_inst.id == self.inst_id_2
            assert ec2_inst.tags["Name"] == "my-server"

        ec2_inst_list_1 = Ec2Instance.from_tag_key_value(
            self.bsm.ec2_client, key="Env", value="dev"
        ).all()
        ec2_inst_list_2 = Ec2Instance.from_tag_key_value(
            self.bsm.ec2_client, key="Env", value=["dev"]
        ).all()
        for ec2_inst_list in [ec2_inst_list_1, ec2_inst_list_2]:
            assert len(ec2_inst_list) == 1
            ec2_inst = ec2_inst_list[0]
            assert ec2_inst.id == self.inst_id_3
            assert ec2_inst.tags["Env"] == "dev"

    def _test_ec2_start_and_stop(self):
        ec2_inst = Ec2Instance.from_id(self.bsm.ec2_client, self.inst_id_1)
        ec2_inst.stop_instance(self.bsm.ec2_client)
        ec2_inst = Ec2Instance.from_id(self.bsm.ec2_client, self.inst_id_1)
        assert ec2_inst.is_running() is False
        assert ec2_inst.is_stopped() is True

        ec2_inst.start_instance(self.bsm.ec2_client)
        ec2_inst = Ec2Instance.from_id(self.bsm.ec2_client, self.inst_id_1)
        assert ec2_inst.is_stopped() is False
        assert ec2_inst.is_running() is True

    def _test_image(self):
        image_list = Image.query(ec2_client=self.bsm.ec2_client).all()
        assert len(image_list) >= 500
        image_list = Image.query(
            ec2_client=self.bsm.ec2_client,
            owners=[ImageOwnerGroupEnum.self.value],
        ).all()
        assert len(image_list) == 1
        assert self.image_id_1 == image_list[0].id

        image = image_list[0]

        assert image.image_type_is_machine() is True
        assert image.image_type_is_kernel() is False
        assert image.image_type_is_ramdisk() is False
        assert image.is_pending() is False
        assert image.is_available() is True
        assert image.is_invalid() is False
        assert image.is_deregistered() is False
        assert image.is_transient() is False
        assert image.is_failed() is False
        assert image.is_error() is False
        assert image.image_root_device_type_is_ebs() is False
        assert image.image_root_device_type_is_instance_store() is False
        assert image.image_virtualization_type_is_hvm() is True
        assert image.image_virtualization_type_is_paravirtual() is False
        assert image.image_boot_mode_is_legacy_bios() is False
        assert image.image_boot_mode_is_uefi() is False
        assert image.image_boot_mode_is_uefi_preferred() is False

        image_list_1 = Image.from_image_name(self.bsm.ec2_client, "my-image-1").all()
        image_list_2 = Image.from_image_name(
            self.bsm.ec2_client,
            ["my-image-1"],
        ).all()
        for image_list in [image_list_1, image_list_2]:
            assert len(image_list) == 1
            image = image_list[0]
            assert image.id == self.image_id_1
            assert image.name == "my-image-1"

        image_list_1 = Image.from_tag_key_value(
            self.bsm.ec2_client, key="Env", value="dev"
        ).all()
        image_list_2 = Image.from_tag_key_value(
            self.bsm.ec2_client, key="Env", value=["dev"]
        ).all()
        for image_list in [image_list_1, image_list_2]:
            assert len(image_list) == 1
            image = image_list[0]
            assert image.id == self.image_id_1
            assert image.tags["Env"] == "dev"

        image = Image.from_id(self.bsm.ec2_client, self.image_id_1)
        image.name = "ubuntu"
        image.description = "Ubuntu"
        assert image.os_type is ImageOSTypeEnum.Ubuntu
        assert "ubuntu" in image.users

    def _test_wait_for_status(self):
        ec2_inst = Ec2Instance.from_id(self.bsm.ec2_client, self.inst_id_1)
        assert ec2_inst.is_running() is True
        with pytest.raises(StatusError):
            ec2_inst.wait_for_stopped(
                ec2_client=self.bsm.ec2_client,
                verbose=False,
            )
        with pytest.raises(StatusError):
            ec2_inst.wait_for_terminated(
                ec2_client=self.bsm.ec2_client,
                verbose=False,
            )

        ec2_inst.stop_instance(self.bsm.ec2_client)
        new_ec2_inst = ec2_inst.wait_for_status(
            ec2_client=self.bsm.ec2_client,
            stop_status=EC2InstanceStatusEnum.stopped,
            verbose=False,
        )
        assert new_ec2_inst.is_stopped() is True
        with pytest.raises(StatusError):
            new_ec2_inst.wait_for_running(
                ec2_client=self.bsm.ec2_client,
                verbose=False,
            )

    def test(self):
        self._test_ec2()
        self._test_ec2_start_and_stop()
        self._test_wait_for_status()
        self._test_image()


if __name__ == "__main__":
    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
