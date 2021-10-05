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
