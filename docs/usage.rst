AWS Satella
===========

Boto3 configuration
-------------------

Make sure your boto3_ client is configured.

.. _boto3: https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.html

Using aws-satella
-----------------

In any part of your code (but at least once per process) please call

.. autofunction:: aws_satella.start_if_not_started

This will provide all of it's arguments to:

.. autoclass:: aws_satella.AWSSatellaExporterThread

Which in turn may raise an exception during it's construction, namely:

.. autoclass:: aws_satella.InitializationError

If you service preforks, set :code:`add_pid` argument to, for example :code:`pid`.

Usage with Django
==================

To use aws-satella with Django, add the following to your :code:`settings.py:


.. code-block:: python

    MIDDLEWARE = [
        ...,
        'aws_satella.contrib.django.AWSSatellaMiddleware',
        ...
    ]

    AWS_SATELLA_MIDDLEWARE_CONSTRUCTOR = {
        'namespace': 'YourAppNamespace',
        'add_pid': 'pid'
    }

Basically all the parameters here will be passed as kwargs to AWSSatellaExporterThread.

Note that you still need to install and configure django-satella-metrics separately_.

.. _separately: https://github.com/piotrmaslanka/django-satella-metrics
