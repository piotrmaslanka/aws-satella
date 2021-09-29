# aws-satella
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
