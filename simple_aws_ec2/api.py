# -*- coding: utf-8 -*-

"""
Public API.
"""

from .exc import StatusError
from .ec2 import CannotDetectOSTypeError
from .ec2 import EC2InstanceStatusEnum
from .ec2 import EC2InstanceStatusGroupEnum
from .ec2 import EC2InstanceArchitectureEnum
from .ec2 import Ec2InstanceHypervisorEnum
from .ec2 import Ec2Instance
from .ec2 import Ec2InstanceIterProxy
from .ec2 import ImageTypeEnum
from .ec2 import ImageStateEnum
from .ec2 import ImageRootDeviceTypeEnum
from .ec2 import ImageVirtualizationTypeEnum
from .ec2 import ImageBootModeEnum
from .ec2 import ImageOwnerGroupEnum
from .ec2 import ImageOSTypeEnum
from .ec2 import Image
from .ec2 import ImageIterProxy
from .ec2 import Eip
from .ec2 import EipIterProxy
from .ec2_metadata_cache import Ec2MetadataCache

EC2MetadataCache = Ec2MetadataCache  # for backward compatibility
