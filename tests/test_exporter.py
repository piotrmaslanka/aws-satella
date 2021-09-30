import time
import unittest
from unittest import mock

from boto3.exceptions import Boto3Error
from satella.coding.structures import DictObject
from satella.instrumentation.metrics import getMetric

from aws_satella import AWSSatellaExporterThread, start_if_not_started


class TestExporter(unittest.TestCase):
    @mock.patch('boto3.client')
    def test_autostart(self, client):
        start_if_not_started('Celery', interval=1)
        from aws_satella.exporter import worker_thread
        worker_thread.terminate().join()

    @mock.patch('boto3.client')
    def test_exporter(self, client):
        client2 = mock.MagicMock()
        metric = getMetric('metric', 'counter')
        metric2 = getMetric('metric', 'counter')
        metric.runtime(+1)
        metric2.runtime(+1, tag='value')
        do = DictObject(put_metric_data=client2)
        start_if_not_started('Celery', interval=1)
        aws = AWSSatellaExporterThread('Celery', interval=1)
        aws.cloudwatch = do
        aws.start()
        time.sleep(2)
        client.assert_called_once_with('cloudwatch')
        self.assertTrue(client2.called)
        aws.terminate().join()

    @mock.patch('boto3.client')
    def test_exporter_raising(self, client):
        client2 = mock.MagicMock()
        metric = getMetric('metric', 'counter')
        metric2 = getMetric('metric', 'counter')
        metric.runtime(+1)
        metric2.runtime(+1, tag='value')

        def put_metric_data(**data):
            raise Boto3Error()

        do = DictObject(put_metric_data=put_metric_data)
        start_if_not_started('Celery', interval=1)
        failload = mock.MagicMock()
        aws = AWSSatellaExporterThread('Celery', interval=1, call_on_metric_upload_fails=failload)
        aws.cloudwatch = do
        aws.start()
        time.sleep(2)
        aws.terminate().join()
        self.assertTrue(failload.called)

    @mock.patch('boto3.client')
    def test_exporter_too_many_labels(self, client):
        client2 = mock.MagicMock()
        d = {}
        for i in range(11):
            d[str(i)] = str(i)
        metric = getMetric('metric3', 'counter')
        metric.runtime(+1, **d)
        do = DictObject(put_metric_data=client2)
        start_if_not_started('Celery', interval=1)
        aws = AWSSatellaExporterThread('Celery', interval=1)
        aws.cloudwatch = do
        aws.start()
        time.sleep(2)
        client.assert_called_once_with('cloudwatch')
        self.assertTrue(client2.called)
        aws.terminate().join()

    @mock.patch('boto3.client')
    def test_exporter_many_metrics(self, client):
        client2 = mock.MagicMock()
        for i in range(21):
            getMetric('i%s' % (i, ), 'counter').runtime(1)
        do = DictObject(put_metric_data=client2)
        start_if_not_started('Celery', interval=1)
        aws = AWSSatellaExporterThread('Celery', interval=1)
        aws.cloudwatch = do
        aws.start()
        time.sleep(2)
        client.assert_called_once_with('cloudwatch')
        self.assertTrue(client2.called)
        aws.terminate().join()
