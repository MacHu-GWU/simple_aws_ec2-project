# -*- coding: utf-8 -*-

from ._version import __version__

__short_description__ = "Simple AWS EC2 devtool."
__license__ = "MIT"
__author__ = "Sanhe Hu"
__author_email__ = "husanhe@gmail.com"
__github_username__ = "MacHu-GWU"

try:
    from .api import (
        EC2InstanceStatusEnum,
        Ec2Instance,
        Ec2InstanceIterproxy,
    )
except ImportError as e:
    pass
