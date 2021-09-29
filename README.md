# aws-satella
[![PyPI](https://img.shields.io/pypi/pyversions/aws-satella.svg)](https://pypi.python.org/pypi/aws-satella)
[![PyPI version](https://badge.fury.io/py/aws-satella.svg)](https://badge.fury.io/py/aws-satella)
[![PyPI](https://img.shields.io/pypi/implementation/aws-satella.svg)](https://pypi.python.org/pypi/aws-satella)
[![Documentation Status](https://readthedocs.org/projects/aws-satella/badge/?version=latest)](http://aws-satella.readthedocs.io/en/latest/?badge=latest)
[![License](https://img.shields.io/pypi/l/aws-satella)](https://github.com/Dronehub/aws-satella)

A library to export Satella's metrics to AWS CloudWatch

# Installation

```bash
pip install aws-satella
```

# Usage

```python
from aws_satella import AWSSatellaExporterThread

aws = AWSSatellaExporterThread('AppNamespace')
aws.start()
```

This spawns a daemonic thread. For details,
refer to the [docs](aws_satella/exporter.py).

You can additionally use
```python
from aws_satella import start_if_not_started

start_if_not_started(*args, **kwargs)
```
Both `args` and `kwargs` will be passed to constructor.
This will initialize such thread, if one does not exist already.

# Change log

## v1.1

* fixed maximum number of metrics uploaded
* metrics with dimension count above 10 will be discarded
    with a warning
