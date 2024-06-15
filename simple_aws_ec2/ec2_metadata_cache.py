# -*- coding: utf-8 -*-

"""
Get EC2 metadata and leverage cache to reduce the number of requests to AWS.
"""

import typing as T
import json
import dataclasses
from pathlib import Path
from datetime import datetime, timezone

try:
    import boto3
except ImportError: # pragma: no cover
    pass

from .ec2 import Ec2Instance

dir_home = Path.home()
path_ec2_metadata_cache_json = dir_home / ".ec2_metadata_cache.json"

EPOCH = datetime(1970, 1, 1).replace(tzinfo=timezone.utc)
EXPIRE = 24 * 60 * 60  # 24 hours


@dataclasses.dataclass
class Ec2MetadataCache:
    """
    A data container for EC2 metadata with cache backend.

    Usage example:

    .. code-block:: python

        >>> ec2_metadata = Ec2MetadataCache.load()
        >>> ec2_metadata.get_instance_id
        >>> ec2_metadata.get_instance_type
        >>> ec2_metadata.get_region
        >>> ec2_metadata.get_public_ipv4
        >>> ec2_metadata.get_iam_info
        >>> ec2_metadata.get_boto_ses_from_ec2_inside
    """

    _update_time: datetime = dataclasses.field()
    _instance_id: T.Optional[str] = dataclasses.field(default=None)
    _instance_type: T.Optional[str] = dataclasses.field(default=None)
    _region: T.Optional[str] = dataclasses.field(default=None)
    _public_ipv4: T.Optional[str] = dataclasses.field(default=None)
    _iam_info: T.Optional[dict] = dataclasses.field(default=None)

    @classmethod
    def from_dict(cls, data: dict):
        """
        Deserialize the data to the class instance.
        """
        return cls(**data)

    def to_dict(self):
        """
        Serialize the data to a dictionary.
        """
        return dataclasses.asdict(self)

    @classmethod
    def load(cls):
        """
        Load the data from the cache file. If cache file does not exist,
        initialize the cache file.
        """
        if path_ec2_metadata_cache_json.exists():
            data = json.loads(path_ec2_metadata_cache_json.read_text())
            data["_update_time"] = datetime.fromisoformat(data["_update_time"])
            return cls.from_dict(data)
        else:
            ec2_metadata = cls(_update_time=EPOCH)
            ec2_metadata.dump()
            return ec2_metadata

    def dump(self):
        """
        Dump the data to the cache file.
        """
        data = self.to_dict()
        data["_update_time"] = data["_update_time"].isoformat()
        path_ec2_metadata_cache_json.write_text(json.dumps(data))

    def is_expired(self) -> bool:
        """
        Check if the in-memory cache is expired.
        """
        utc_now = datetime.utcnow().replace(tzinfo=timezone.utc)
        return (utc_now - self._update_time).total_seconds() > EXPIRE

    def get_instance_id(
        self,
        refresh_cache: bool = True,
        ignore_cache: bool = False,
    ) -> str:  # pragma: no cover
        """
        Get EC2 instance id.
        """
        if ignore_cache is True or self._instance_id is None or self.is_expired():
            self._instance_id = Ec2Instance.get_instance_id()
            if refresh_cache:
                self.dump()
            return self._instance_id
        else:
            return self._instance_id

    def get_instance_type(
        self,
        refresh_cache: bool = True,
        ignore_cache: bool = False,
    ) -> str:  # pragma: no cover
        """
        Get EC2 instance type.
        """
        if ignore_cache is True or self._instance_type is None or self.is_expired():
            self._instance_type = Ec2Instance.get_instance_type()
            if refresh_cache:
                self.dump()
            return self._instance_type
        else:
            return self._instance_type

    def get_region(
        self,
        refresh_cache: bool = True,
        ignore_cache: bool = False,
    ) -> str:  # pragma: no cover
        """
        Get EC2 placement region.
        """
        if ignore_cache is True or self._region is None or self.is_expired():
            self._region = Ec2Instance.get_placement_region()
            if refresh_cache:
                self.dump()
            return self._region
        else:
            return self._region

    def get_public_ipv4(
        self,
        refresh_cache: bool = True,
        ignore_cache: bool = False,
    ) -> str:  # pragma: no cover
        """
        Get EC2 public IPv4 address.
        """
        if ignore_cache is True or self._public_ipv4 is None or self.is_expired():
            self._public_ipv4 = Ec2Instance.get_public_ipv4()
            if refresh_cache:
                self.dump()
            return self._public_ipv4
        else:
            return self._public_ipv4

    def get_iam_info(
        self,
        refresh_cache: bool = True,
        ignore_cache: bool = False,
    ) -> T.Dict[str, str]:  # pragma: no cover
        """
        Get EC2 IAM info. Example response:

        .. code-block:: python

            {
                "Code" : "Success",
                "LastUpdated" : "2023-01-01T00:00:00Z",
                "InstanceProfileId" : "ABCD..."
                "InstanceProfileArn" : "arn:aws:iam::111122223333:instance-profile/profile-name",
            }
        """
        if ignore_cache is True or self._iam_info is None or self.is_expired():
            self._iam_info = Ec2Instance.get_iam_info()
            if refresh_cache:
                self.dump()
            return self._iam_info
        else:
            return self._iam_info

    def get_boto_ses_from_ec2_inside(
        self,
        refresh_cache: bool = True,
        ignore_cache: bool = False,
    ) -> "boto3.session.Session":  # pragma: no cover
        """
        Get the boto3 session of the EC2 instance. On EC2, we use the IAM role
        to get the AWS credentials, and use the EC2 metadata API to get the region.
        """
        aws_region = self.get_region(
            refresh_cache=refresh_cache,
            ignore_cache=ignore_cache,
        )
        return boto3.session.Session(region_name=aws_region)
