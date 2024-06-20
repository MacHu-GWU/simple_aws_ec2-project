# -*- coding: utf-8 -*-

import csv
from pathlib import Path
from simple_aws_ec2.os_detector import ImageOSTypeEnum, detect_os_type


def test_detect_os_type():
    path = Path(__file__).absolute().parent / "os_detector_test_data.tsv"
    with open(path, newline="") as csvfile:
        reader = csv.reader(csvfile, delimiter="\t")
        next(reader)
        for name, description, expected_os_type in reader:
            detected_os_type = detect_os_type(name=name, description=description)
            assert detected_os_type is ImageOSTypeEnum[expected_os_type]
            _ = detected_os_type.users


if __name__ == "__main__":
    from simple_aws_ec2.tests import run_cov_test

    run_cov_test(__file__, "simple_aws_ec2.os_detector", preview=False)
