.. _release_history:

Release and Version History
==============================================================================


Backlog (TODO)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Features and Improvements**

**Minor Improvements**

**Bugfixes**

**Miscellaneous**


0.8.1 (2024-06-15)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Features and Improvements**

- Add the following public API:
    - :class:`simple_aws_ec2.StatusError <simple_aws_ec2.exc.StatusError>`
    - :class:`simple_aws_ec2.Eip <simple_aws_ec2.ec2.Eip>`
    - :meth:`simple_aws_ec2.Eip.from_dict <simple_aws_ec2.ec2.Eip.from_dict>`
    - :meth:`simple_aws_ec2.Eip.is_associated <simple_aws_ec2.ec2.Eip.is_associated>`
    - :meth:`simple_aws_ec2.Eip.query <simple_aws_ec2.ec2.Eip.query>`
    - :meth:`simple_aws_ec2.Eip.from_id <simple_aws_ec2.ec2.Eip.from_id>`
    - :meth:`simple_aws_ec2.Eip.from_public_ip <simple_aws_ec2.ec2.Eip.from_public_ip>`
    - :class:`simple_aws_ec2.EipIterProxy <simple_aws_ec2.ec2.EipIterProxy>`


0.7.3 (2024-06-14)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Bugfixes**

- Fix a bug that :meth:`~simple_aws_ec2.ec2.Image.deregister` method may fail when trying to delete snapshot immediately. Now it wait for the image got deregistered then start deleting snapshot.


0.7.2 (2024-06-13)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Bugfixes**

- Fix a bug that :meth:`~simple_aws_ec2.ec2.Ec2Instance.wait_for_status` and :meth:`~simple_aws_ec2.ec2.Image.wait_for_status` failed to respect the list of provided ``stop_status`` and ``error_status``.


0.7.1 (2024-06-13)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Features and Improvements**

- add :meth:`~simple_aws_ec2.ec2.Image.wait_for_status` waiter method.
- add :meth:`~simple_aws_ec2.ec2.Image.wait_for_available` waiter method.
- add :meth:`~simple_aws_ec2.ec2.Image.wait_for_deregistered` waiter method.
- add :meth:`~simple_aws_ec2.ec2.Image.is_disabled` method.
- add :meth:`~simple_aws_ec2.ec2.Image.deregister` method.
- add ``simple_aws_ec2.ec2.ImageStateEnum.disabled`` status code.


0.6.2 (2023-06-28)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Bugfixes**

- fix a bug that ``EC2MetadataCache.get_xyz()`` methods always return ``None``.


0.6.1 (2023-06-28)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Features and Improvements**

- add :class:`~simple_aws_ec2.ec2_metadata_cache.EC2MetadataCache`.


0.5.2 (2023-06-21)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Features and Improvements**

- add a few ec2 metadata api methods for :meth:`~simple_aws_ec2.ec2.Ec2Instance`.


0.5.1 (2023-06-19)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Features and Improvements**

- add :meth:`~simple_aws_ec2.ec2.Ec2Instance.terminate_instance` method.


0.4.1 (2023-06-15)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Features and Improvements**

- add :meth:`~simple_aws_ec2.ec2.Ec2Instance.wait_for_status` waiter method.
- add :meth:`~simple_aws_ec2.ec2.Ec2Instance.wait_for_running` waiter method.
- add :meth:`~simple_aws_ec2.ec2.Ec2Instance.wait_for_stopped` waiter method.
- add :meth:`~simple_aws_ec2.ec2.Ec2Instance.wait_for_terminated` waiter method.


0.3.2 (2023-06-14)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Bugfixes**

- Fix a bug that :meth:`~simple_aws_ec2.ec2.Image.os_type` returns ``None`` when it fails to guess, however, it should raise an exception.


0.3.1 (2023-06-14)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Features and Improvements**

- add lots of EC2 instance attributes
- add helper methods to call EC2 metadata API from EC2 instance inside.
- add method :meth:`~simple_aws_ec2.ec2.Image.os_type` to guess the AMI OS type, and then get the user name.


0.2.1 (2023-06-14)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Breaking change**

- all method now take ec2_client as the first argument. no longer need ``boto_session_manager``.

**Features and Improvements**

- add :class:`~simple_aws_ec2.ec2.Image` class.

**Minor Improvements**

- :meth`~simple_aws_ec2.ec2.Ec2Instance.from_tag_key_value` now take list of values.


0.1.4 (2023-05-06)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Bugfixes**

- fix a bug that the :meth:`~simple_aws_ec2.ec2.Ec2Instance._yield_dict_from_describe_instances_response` method failed to yield instances objects.


0.1.3 (2023-05-03)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Bugfixes**

- fix a bug that when you describe ec2 instances with instance ids, we should not use any paginator configuration.


0.1.2 (2023-05-04)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Miscellaneous**

- rename ``Ec2InstanceIterproxy`` to ``Ec2InstanceIterProxy``.


0.1.1 (2023-05-03)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Features and Improvements**

- First release
- Add ``EC2Instance`` data class
