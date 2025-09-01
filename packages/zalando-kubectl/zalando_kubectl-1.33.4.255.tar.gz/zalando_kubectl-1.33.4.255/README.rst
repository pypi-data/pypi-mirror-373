===============
Zalando Kubectl
===============

.. image:: https://img.shields.io/pypi/dw/zalando-kubectl.svg
   :target: https://pypi.python.org/pypi/zalando-kubectl/
   :alt: PyPI Downloads

.. image:: https://img.shields.io/pypi/v/zalando-kubectl.svg
   :target: https://pypi.python.org/pypi/zalando-kubectl/
   :alt: Latest PyPI version

.. image:: https://img.shields.io/pypi/l/zalando-kubectl.svg
   :target: https://pypi.python.org/pypi/zalando-kubectl/
   :alt: License

Kubernetes CLI (kubectl) wrapper in Python with OAuth token authentication.

This wrapper script ``zkubectl`` serves as a drop-in replacement for the ``kubectl`` binary:

* it downloads the current ``kubectl`` binary from Google
* it generates a new ``~/.kube/config`` with an OAuth Bearer token acquired via `zign`_.
* it passes through commands to the ``kubectl`` binary


Installation
============

Requires Python 3.6+.

.. code-block:: bash

    $ sudo pip3 install --upgrade zalando-kubectl

Usage
=====

You can directly login to a known Kubernetes API server endpoint:

.. code-block:: bash

    $ zkubectl login https://my-api-server.example.org
    $ zkubectl cluster-info

You can also configure a Cluster Registry to look up clusters by ID:

.. code-block:: bash

    $ zkubectl configure --cluster-registry=https://cluster-registry.example.org
    $ zkubectl login my-cluster-id

The Cluster Registry needs to provide the following HTTP API for this to work:

.. code-block:: bash

    $ curl -H "Authorization: Bearer $(zign tok)" https://cluster-registry.example.org/kubernetes-clusters/my-cluster-id
    {
        "api_server_url": "https://my-api-server.example.org"
    }

There is an additional convenience command to open the `kube-web-view` dashboard in the browser:

.. code-block:: bash

    $ zkubectl dashboard
    Opening https://kube-web-view.zalando.net/ ..


Unit Tests
==========

Run unit tests with Tox:

.. code-block:: bash

    $ sudo pip3 install tox
    $ tox

Local Changes
=============

It's recommended to have a `virtualenv` for the project. The project uses `Black`_ for code formatting,
please configure your editor to use it.

Go to the project dir and install dependencies into virtual test environment

.. code-block:: bash

    $ cd <project-path>
    # create new virtual environment if not yet
    $ python -m venv test_environment
    # enter virtual environment
    $ source ./test_environment/bin/activate
    # check pip is executed fron this virtual environment
    (test_environment) $ which pip
    <project-path>/test_environment/bin/pip

    (test_environment) $ pip install -r requirements.txt
    (test_environment) $ pip install --editable .

Now the code change will just be reflected in the `zkubectl` binary

.. code-block:: bash

    (test_environment) $ zkubectl <whatever>

As an alternative for creating an environment you can run local changes from `zalando_kubectl`

.. code-block:: bash

    $ cd <project-path>
    $ python -m zalando_kubectl <whatever>

.. _zign: https://pypi.python.org/pypi/stups-zign
.. _Kubernetes Dashboard web UI: http://kubernetes.io/docs/user-guide/ui/
.. _Black: https://black.readthedocs.io/en/stable/
