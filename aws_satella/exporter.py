import logging
import typing as tp
import boto3
from boto3.exceptions import Boto3Error
from satella.coding import log_exceptions
from satella.coding.concurrent import IntervalTerminableThread
from satella.instrumentation.metrics import getMetric


logger = logging.getLogger(__name__)


class AWSSatellaExporterThread(IntervalTerminableThread):
    """
    A AWS satella exporter thread

    :param interval: amount of seconds to wait between sending metrics
    :param namespace: AWS namespace to use
    :param extra_dimensions: extra dimensions to add to send metrics
    :param max_send_at_once: maximum amount of metrics to send for a single call to AWS
    """
    def __init__(self, interval: int, namespace: str,
                 extra_dimensions: tp.Optional[tp.Dict[str, str]] = None,
                 max_send_at_once: int = 1000):
        super().__init__(interval, name='aws-satella-metrics', daemon=True)
        self.MAX_SEND_AT_ONCE = max_send_at_once
        self.cloudwatch = boto3.client('cloudwatch')
        self.extra_dimensions = extra_dimensions or {}
        self.namespace = namespace

    def loop(self) -> None:
        md = getMetric().to_metric_data()
        results = []
        for val in md.values:
            dims = val.labels
            dims.update(self.extra_dimensions)
            results.append({'MetricName': val.name,
                            'Dimensions': dims,
                            'Unit': 'None',
                            'Value': val.value})

            if len(results) > self.MAX_SUBMIT_ONCE:
                self.send_metrics(results)
                results = []
        if results:
            self.send_metrics(results)

    @log_exceptions(logger, logging.INFO, 'Failure uploading metrics: {e}',
                    exc_types=Boto3Error)
    def send_metrics(self, data):
        self.cloudwatch.put_metric_data(MetricData=data,
                                        Namespace=self.namespace)
