import logging
import os
import typing as tp
import warnings
from threading import Lock

import boto3
from boto3.exceptions import Boto3Error
from botocore.exceptions import BotoCoreError, ClientError
from satella.coding import reraise_as
from satella.coding.concurrent import IntervalTerminableThread
from satella.instrumentation.metrics import getMetric, MetricData
from satella.time import parse_time_string

logger = logging.getLogger(__name__)


class InitializationError(RuntimeError):
    """Exception raised when boto3 client cannot be configured"""


class AWSSatellaExporterThread(IntervalTerminableThread):
    """
    A AWS satella exporter thread. Is daemonic, so you don't need to terminate it when you quit.

    :param namespace: AWS namespace to use
    :param extra_dimensions: extra dimensions to add to sent metrics
    :param interval: amount of seconds to wait between sending metrics. Defaults to 5 minutes.
        Can be also given in a form of expression, like '30m'
    :param add_pid: If this is set to a string this will add an extra dimension called that
        and having the value of this process' PID. This is done to monitor preforking services.
    :param max_send_at_once: maximum amount of metrics to send for a single call to AWS.
        Defaults to 20.
    :param call_on_metric_upload_fails: optional callable, to be called with an Exception
        instance when upload of the metrics fails
    :param call_on_discarded_metric: called with a discarded MetricData. Metrics will be discarded
        for having more than 10 dimensions (after update)
    """

    def __init__(self, namespace: str,
                 extra_dimensions: tp.Optional[tp.Dict[str, str]] = None,
                 interval: tp.Union[str, int] = '300s',
                 max_send_at_once: int = 20,
                 add_pid: tp.Optional[str] = None,
                 call_on_metric_upload_fails: tp.Callable[[Exception], None] = lambda e: None,
                 call_on_discarded_metric: tp.Callable[[MetricData], None] = lambda e: None):
        super().__init__(parse_time_string(interval), name='aws-satella-metrics', daemon=True)
        self.max_send_at_once = max_send_at_once
        with reraise_as((Boto3Error, BotoCoreError, ClientError), InitializationError):
            self.cloudwatch = boto3.client('cloudwatch')
        self.call_on_metric_upload_fails = call_on_metric_upload_fails
        self.extra_dimensions = extra_dimensions or {}
        self.namespace = namespace
        self.add_pid = add_pid
        self.call_on_discarded_metric = call_on_discarded_metric

    def loop(self) -> None:
        md = getMetric().to_metric_data()
        results = []
        for val in md.values:
            dims = dict(val.labels)
            dims.update(self.extra_dimensions)

            if len(dims) > 10:
                warnings.warn('Maximum number of dimensions for AWS is 10, skipping this metric',
                              RuntimeWarning)
                self.call_on_discarded_metric(val)
                continue

            if self.add_pid:
                dims[self.add_pid] = os.getpid()

            dimensions = []
            for key, value in dims.items():
                dimensions.append({'Name': key, 'Value': str(value)})

            results.append({'MetricName': val.name,
                            'Dimensions': dimensions,
                            'Unit': 'None',
                            'Value': val.value})

            if len(results) >= self.max_send_at_once:
                self.send_metrics(results)
                results = []
        if results:
            self.send_metrics(results)

    def send_metrics(self, data):
        try:
            self.cloudwatch.put_metric_data(MetricData=data,
                                            Namespace=self.namespace)
            logger.debug('Successfully published %s metrics to namespace %s',
                         len(data), self.namespace)
        except (BotoCoreError, Boto3Error, ClientError) as e:
            self.call_on_metric_upload_fails(e)
            logger.warning('Failure uploading metrics', exc_info=e)


worker_thread = None

worker_thread_lock = Lock()


def start_if_not_started(*args, **kwargs) -> None:
    """
    Check if exporter thread has been started. If it has not, start it.

    :raises InitializationError: could not initialize AWS Satella exporter
    :param args: will be passed to AWSSatellaExporterThread's constructor
    :param kwargs: will be passed to AWSSatellaExporterThread's constructor
    """
    global worker_thread, worker_thread_lock
    with worker_thread_lock:
        if worker_thread is None:
            worker_thread = AWSSatellaExporterThread(*args, **kwargs)
            worker_thread.start()
