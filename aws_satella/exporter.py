import logging
import typing as tp
import warnings
from threading import Lock
import boto3
from boto3.exceptions import Boto3Error
from botocore.exceptions import BotoCoreError
from satella.coding import log_exceptions
from satella.coding.concurrent import IntervalTerminableThread
from satella.coding.transforms import stringify
from satella.instrumentation.metrics import getMetric
from satella.time import parse_time_string

logger = logging.getLogger(__name__)


class AWSSatellaExporterThread(IntervalTerminableThread):
    """
    A AWS satella exporter thread. Is daemonic.

    Can be also used like:

    >>> import boto3
    >>> boto_client = boto3.client('cloudwatch')
    >>> aws_e = AWSSatellaExporterThread('AppNamespace', boto_client)
    >>> aws_e.start()
    >>> ...
    >>> aws_e.terminate().join()

    :param namespace: AWS namespace to use
    :param extra_dimensions: extra dimensions to add to sent metrics
    :param boto3_client: a boto3 client to use. If not given, a default one
        with a resource name of 'cloudwatch' will be created.
    :param interval: amount of seconds to wait between sending metrics. Defaults to 60.
        Can be also given in a form of expression, like '30m'
    :param max_send_at_once: maximum amount of metrics to send for a single call to AWS.
        Defaults to 20.
    :param call_on_metric_upload_fails: optional callable, to be called with an Exception
        instance when upload of the metrics fails
    """
    def __init__(self, namespace: str,
                 extra_dimensions: tp.Optional[tp.Dict[str, str]] = None,
                 boto3_client=None, interval: tp.Union[str, int] = '60s',
                 max_send_at_once: int = 20,
                 call_on_metric_upload_fails: tp.Callable[[Exception], None] = lambda e: None):
        super().__init__(parse_time_string(interval), name='aws-satella-metrics', daemon=True)
        self.MAX_SEND_AT_ONCE = max_send_at_once
        self.call_on_metric_upload_fails = call_on_metric_upload_fails
        self.cloudwatch = boto3_client or boto3.client('cloudwatch')
        self.extra_dimensions = extra_dimensions or {}
        self.namespace = namespace

    def loop(self) -> None:
        md = getMetric().to_metric_data()
        results = []
        for val in md.values:
            dims = val.labels
            dims.update(self.extra_dimensions)
            dims = stringify(dims)
            if len(dims) > 10:
                warnings.warn('Maximum number of dimensions for AWS is 10, skipping this metric',
                              RuntimeWarning)
                continue
            results.append({'MetricName': val.name,
                            'Dimensions': dims,
                            'Unit': 'None',
                            'Value': val.value})

            if len(results) >= self.MAX_SEND_AT_ONCE:
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
        except (BotoCoreError, Boto3Error) as e:
            self.call_on_metric_upload_fails(e)
            logger.warning('Failure uploading metrics', exc_info=e)


worker_thread = None

worker_thread_lock = Lock()


def start_if_not_started(*args, **kwargs):
    global worker_thread, worker_thread_lock
    with worker_thread_lock:
        if worker_thread is None:
            worker_thread = AWSSatellaExporterThread(*args, **kwargs)
            worker_thread.start()

