# aws-satella
A library to export Satella's metrics to AWS CloudWatch

# Installation

```bash
pip install aws-satella
```

# Usage

```python
from aws_satella import AWSSatellaExporterThread

aws = AWSSatellaExporterThread(60, 'AppNamespace')
aws.start()
```

This spawns a daemonic thread. For details,
refer to the [docs](aws_satella/exporter.py).
