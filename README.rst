
.. .. image:: https://readthedocs.org/projects/simple_aws_ec2/badge/?version=latest
    :target: https://simple_aws_ec2.readthedocs.io/index.html
    :alt: Documentation Status

.. image:: https://github.com/MacHu-GWU/simple_aws_ec2-project/workflows/CI/badge.svg
    :target: https://github.com/MacHu-GWU/simple_aws_ec2-project/actions?query=workflow:CI

.. image:: https://codecov.io/gh/MacHu-GWU/simple_aws_ec2-project/branch/main/graph/badge.svg
    :target: https://codecov.io/gh/MacHu-GWU/simple_aws_ec2-project

.. image:: https://img.shields.io/pypi/v/simple_aws_ec2.svg
    :target: https://pypi.python.org/pypi/simple_aws_ec2

.. image:: https://img.shields.io/pypi/l/simple_aws_ec2.svg
    :target: https://pypi.python.org/pypi/simple_aws_ec2

.. image:: https://img.shields.io/pypi/pyversions/simple_aws_ec2.svg
    :target: https://pypi.python.org/pypi/simple_aws_ec2

.. image:: https://img.shields.io/badge/STAR_Me_on_GitHub!--None.svg?style=social
    :target: https://github.com/MacHu-GWU/simple_aws_ec2-project

------


.. .. image:: https://img.shields.io/badge/Link-Document-blue.svg
    :target: https://simple_aws_ec2.readthedocs.io/index.html

.. .. image:: https://img.shields.io/badge/Link-API-blue.svg
    :target: https://simple_aws_ec2.readthedocs.io/py-modindex.html

.. .. image:: https://img.shields.io/badge/Link-Source_Code-blue.svg
    :target: https://simple_aws_ec2.readthedocs.io/py-modindex.html

.. image:: https://img.shields.io/badge/Link-Install-blue.svg
    :target: `install`_

.. image:: https://img.shields.io/badge/Link-GitHub-blue.svg
    :target: https://github.com/MacHu-GWU/simple_aws_ec2-project

.. image:: https://img.shields.io/badge/Link-Submit_Issue-blue.svg
    :target: https://github.com/MacHu-GWU/simple_aws_ec2-project/issues

.. image:: https://img.shields.io/badge/Link-Request_Feature-blue.svg
    :target: https://github.com/MacHu-GWU/simple_aws_ec2-project/issues

.. image:: https://img.shields.io/badge/Link-Download-blue.svg
    :target: https://pypi.org/pypi/simple_aws_ec2#files


Welcome to ``simple_aws_ec2`` Documentation
==============================================================================

Usage:

.. code-block:: python

    from simple_aws_ec2 import Ec2Instance
    from boto_session_manager import BotoSesManager

    bsm = BotoSesManager()

    ec2_inst = Ec2Instance.from_id(bsm, "i-1a2b3c")
    ec2_inst = EC2Instance.from_ec2_inside(bsm)
    ec2_inst = EC2Instance.from_ec2_name(bsm, "my-server).one_or_none()
    ec2_inst = EC2Instance.from_tag_key_value(bsm, key="Env", value="prod").one_or_none()
    ec2_inst = EC2Instance.query(bsm, filters=..., instnace_ids=...).all()

    print(ec2_inst.id)
    print(ec2_inst.status)
    print(ec2_inst.public_ip)
    print(ec2_inst.private_ip)
    print(ec2_inst.vpc_id)
    print(ec2_inst.subnet_id)
    print(ec2_inst.security_groups)
    print(ec2_inst.image_id)
    print(ec2_inst.instance_type)
    print(ec2_inst.key_name)
    print(ec2_inst.tags)
    print(ec2_inst.data)

    print(ec2_inst.is_running()
    print(ec2_inst.is_stopped()
    print(ec2_inst.is_pending())
    print(ec2_inst.is_shutting_down()
    print(ec2_inst.is_stopping()
    print(ec2_inst.is_terminated()

    print(ec2_inst.is_ready_to_start()
    print(ec2_inst.is_ready_to_stop()


.. _install:

Install
------------------------------------------------------------------------------

``simple_aws_ec2`` is released on PyPI, so all you need is:

.. code-block:: console

    $ pip install simple_aws_ec2

To upgrade to latest version:

.. code-block:: console

    $ pip install --upgrade simple_aws_ec2