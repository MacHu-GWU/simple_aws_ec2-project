# -*- coding: utf-8 -*-

"""
Detect the OS type of an AMI.
"""

import typing as T
import enum

from .exc import CannotDetectOSTypeError


class ImageOSTypeEnum(str, enum.Enum):
    """
    Reference:

    - Default user name for AMI: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/connection-prereqs.html#connection-prereqs-get-info-about-instance
    """

    AmazonLinux = "AmazonLinux"
    CentOS = "CentOS"
    Debian = "Debian"
    Fedora = "Fedora"
    RHEL = "RHEL"
    SUSE = "SUSE"
    Ubuntu = "Ubuntu"
    Oracle = "Oracle"
    Bitnami = "Bitnami"
    Other = "Other"

    @property
    def users(self) -> T.List[str]:
        return os_type_to_users_mapper[self.value]


os_type_to_users_mapper: T.Dict[str, T.List[str]] = {
    ImageOSTypeEnum.AmazonLinux.value: ["ec2-user"],
    ImageOSTypeEnum.CentOS.value: ["centos", "ec2-user"],
    ImageOSTypeEnum.Debian.value: ["admin"],
    ImageOSTypeEnum.Fedora.value: ["fedora", "ec2-user"],
    ImageOSTypeEnum.RHEL.value: ["ec2-user", "root"],
    ImageOSTypeEnum.SUSE.value: ["ec2-user", "root"],
    ImageOSTypeEnum.Ubuntu.value: ["ubuntu"],
    ImageOSTypeEnum.Oracle.value: ["ec2-user"],
    ImageOSTypeEnum.Bitnami.value: ["bitnami"],
    ImageOSTypeEnum.Other.value: ["unknown"],
}

type_to_keyword: T.Dict[str, str] = {
    ImageOSTypeEnum.AmazonLinux.value: ["amazon linux"],
    ImageOSTypeEnum.CentOS.value: ["centos"],
    ImageOSTypeEnum.Debian.value: ["debian"],
    ImageOSTypeEnum.Fedora.value: ["fedora"],
    ImageOSTypeEnum.RHEL.value: ["rhel"],
    ImageOSTypeEnum.SUSE.value: ["suse"],
    ImageOSTypeEnum.Ubuntu.value: ["ubuntu"],
    ImageOSTypeEnum.Oracle.value: ["oracle"],
    ImageOSTypeEnum.Bitnami.value: ["bitnami"],
    ImageOSTypeEnum.Other.value: ["g^M@%U9DL4xu"],  # make it impossible to match
}


def is_os_type(text: str, os_type: ImageOSTypeEnum) -> bool:
    """
    Identify if the text only contains the keyword of the given OS type.
    """
    text = text.lower()
    other_os_type_enum_set = {
        os_type_enum for os_type_enum in ImageOSTypeEnum if os_type_enum is not os_type
    }
    has_keyword = False
    for keyword in type_to_keyword[os_type.value]:
        if keyword in text:
            has_keyword = True
            break
    has_other_keyword = False
    for os_type_enum in other_os_type_enum_set:
        for keyword in type_to_keyword[os_type_enum.value]:
            if keyword in text:
                has_other_keyword = True
                break
    return (has_keyword is True) and (has_other_keyword is False)


def detect_os_type(
    name: str,
    description: T.Optional[str] = None,
) -> ImageOSTypeEnum:
    """
    Try to use the image name and description to determine the OS type.
    If the OS type cannot be determined, raise :class:`CannotDetectOSTypeError`.

    See https://docs.google.com/spreadsheets/d/1m4MNzkUBm5c8RgZLqIcn277jk_AQOUJC71PEQf9ShjE/edit?gid=0#gid=0

    :param name: ami name
    :param description: ami description

    :return: an :class:`ImageOSTypeEnum` object.
    """
    for os_type_enum in ImageOSTypeEnum:
        flag = is_os_type(name, os_type_enum)
        if flag:
            return os_type_enum
        elif description:
            flag = is_os_type(description, os_type_enum)
            if flag:
                return os_type_enum
    raise CannotDetectOSTypeError(
        f"Cannot detect OS type from name: {name}, description: {description}"
    )  # pragma: no cover
