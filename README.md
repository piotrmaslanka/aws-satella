# aws-satella
[![PyPI](https://img.shields.io/pypi/pyversions/aws-satella.svg)](https://pypi.python.org/pypi/aws-satella)
[![PyPI version](https://badge.fury.io/py/aws-satella.svg)](https://badge.fury.io/py/aws-satella)
[![PyPI](https://img.shields.io/pypi/implementation/aws-satella.svg)](https://pypi.python.org/pypi/aws-satella)
[![License](https://img.shields.io/pypi/l/aws-satella)](https://github.com/piotrmaslanka/aws-satella)
[![Build Status](https://app.travis-ci.com/piotrmaslanka/aws-satella.svg?branch=master)](https://travis-ci.com/piotrmaslanka/aws-satella)
[![Test Coverage](https://api.codeclimate.com/v1/badges/d460105ad44269de543b/test_coverage)](https://codeclimate.com/github/piotrmaslanka/aws-satella/test_coverage)
[![Maintainability](https://api.codeclimate.com/v1/badges/d460105ad44269de543b/maintainability)](https://codeclimate.com/github/piotrmaslanka/aws-satella/maintainability)
[![Issue Count](https://codeclimate.com/github/piotrmaslanka/aws-satella/badges/issue_count.svg)](https://codeclimate.com/github/piotrmaslanka/aws-satella)

A library to export Satella's metrics to AWS CloudWatch

# Installation

```bash
pip install aws-satella
```

# Usage

```python
import sys
from aws_satella import AWSSatellaExporterThread, InitializationError


try:
    aws = AWSSatellaExporterThread('AppNamespace')
    aws.start()
except InitializationError:
    print('Could not initialize the boto3 client')
    sys.exit(1)

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

## v2.0 (first working release)

* dimensions will be checked for before the dict-convert

## v1.5 (to be released)

* added Travis and CodeClimate

## v1.4

* added handler for metric fail uploads
* removed the boto_client parameter
* added InitializationError
* fixed a critical bug

## v1.3

* fixed exception handling

## v1.2

* critical bugfix

## v1.1

* fixed maximum number of metrics uploaded
* metrics with dimension count above 10 will be discarded
    with a warning

