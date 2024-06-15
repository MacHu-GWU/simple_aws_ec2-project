# -*- coding: utf-8 -*-

from simple_aws_ec2.ec2_metadata_cache import (
    Ec2MetadataCache,
    path_ec2_metadata_cache_json,
)


class TestEC2MetadataCache:
    def test(self):
        if path_ec2_metadata_cache_json.exists():
            path_ec2_metadata_cache_json.unlink()

        ec2_metadata = Ec2MetadataCache.load()
        ec2_metadata.dump()
        assert ec2_metadata.is_expired() is True

        ec2_metadata = Ec2MetadataCache.load()
        ec2_metadata.dump()


if __name__ == "__main__":
    from simple_aws_ec2.tests import run_cov_test

    run_cov_test(__file__, "simple_aws_ec2.ec2_metadata_cache", preview=False)
