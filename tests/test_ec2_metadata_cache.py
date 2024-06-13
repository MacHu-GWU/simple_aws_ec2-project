# -*- coding: utf-8 -*-

import os
import pytest

from simple_aws_ec2.ec2_metadata_cache import (
    EC2MetadataCache,
    path_ec2_metadata_cache_json,
)


class TestEC2MetadataCache:
    def test(self):
        if path_ec2_metadata_cache_json.exists():
            path_ec2_metadata_cache_json.unlink()

        ec2_metadata = EC2MetadataCache.load()
        ec2_metadata.dump()
        assert ec2_metadata.is_expired() is True

        ec2_metadata = EC2MetadataCache.load()
        ec2_metadata.dump()


if __name__ == "__main__":
    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
