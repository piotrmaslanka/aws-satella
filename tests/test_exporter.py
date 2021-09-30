import time
import unittest
from unittest import mock

from satella.coding.structures import DictObject
from satella.instrumentation.metrics import getMetric

from aws_satella import AWSSatellaExporterThread


class TestExporter(unittest.TestCase):
    @mock.patch('boto3.client')
    def test_exporter(self, client):
        client2 = mock.MagicMock()
        metric = getMetric('metric', 'counter')
        metric.runtime(+1)
        do = DictObject(put_metric_data=client2)
        aws = AWSSatellaExporterThread('Celery', interval=1)
        aws.cloudwatch = do
        aws.start()
        time.sleep(2)
        client.assert_called_once_with('cloudwatch')
        self.assertTrue(client2.called)
