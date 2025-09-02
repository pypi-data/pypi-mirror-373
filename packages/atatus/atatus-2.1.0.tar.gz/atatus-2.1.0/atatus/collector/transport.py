
import json
import gzip
import requests
from .builder import Builder
from atatus.utils import compat
from atatus.utils.logging import get_logger
import atatus
import time

class BaseTransport(object):
    def __init__(self, config, metadata):
        self._config = config
        self._performance = self._config.performance
        self._error_logger = get_logger("atatus.errors")
        self._notify_host = config.notify_host if config.notify_host.endswith("/") else config.notify_host + "/"
        self._analytics_notify_host = config.analytics_notify_host if config.analytics_notify_host.endswith("/") else config.analytics_notify_host + "/"
        self._builder = Builder(config, metadata)
        # self._session = requests.Session()
        self._blocked = False
        self._capture_percentiles = False
        self._hostinfo_response = {}
        self._post_params = {
            'license_key': self._config.license_key,
            'agent_name': atatus.PYTHON_AGENT,
            "version": atatus.VERSION
        }

    def _get_host_info(self):
        return self._builder._common()

    def _post(self, endpoint, data):
        if endpoint != 'track/apm/analytics/txn':
            if (self._blocked is True) and (endpoint != 'track/apm/hostinfo'):
                return

        try:
            time.sleep(0.01)

            notify_host = self._notify_host
            if endpoint == 'track/apm/analytics/txn':
                notify_host = self._analytics_notify_host

            try:
                compressed_data = gzip.compress(json.dumps(data).encode("utf-8"))
                # Set the headers with 'Content-Encoding: gzip'
                headers = {
                    "Content-Encoding": "gzip",
                    "Content-Type": "application/json",
                }
                
                r = requests.post(notify_host + endpoint, params=self._post_params, timeout=30, data=compressed_data, headers=headers)
            except Exception:
                headers = {
                    "Content-Type": "application/json",
                }                
                r = requests.post(notify_host + endpoint, params=self._post_params, timeout=30, data=data, headers=headers)
                pass


            if r.status_code == 200:
                if endpoint != 'track/apm/analytics/txn':
                    self._blocked = False

                if endpoint == 'track/apm/hostinfo':
                    self._capture_percentiles = False
                    c = r.content
                    if not c:
                        return

                    c = c.decode('UTF-8')

                    resp = json.loads(c)
                    if resp:
                        if "blocked" in resp:
                            self._blocked = resp["blocked"]

                        if "tracing" in resp:
                            self._hostinfo_response["tracing"] = resp["tracing"]

                        if "analytics" in resp:
                            self._hostinfo_response["analytics"] = resp["analytics"]

                        if "capturePercentiles" in resp:
                            self._capture_percentiles = resp["capturePercentiles"]
                            self._hostinfo_response["capturePercentiles"] = self._capture_percentiles

                        if "extRequestPatterns" in resp:
                            self._hostinfo_response["extRequestPatterns"] = resp["extRequestPatterns"]

                        if "ignoreTxnNamePatterns" in resp:
                            self._hostinfo_response["ignoreTxnNamePatterns"] = resp["ignoreTxnNamePatterns"]

                        if "ignoreHTTPFailurePatterns" in resp:
                            self._hostinfo_response["ignoreHTTPFailurePatterns"] = resp["ignoreHTTPFailurePatterns"]

                        if "ignoreExceptionPatterns" in resp:
                            self._hostinfo_response["ignoreExceptionPatterns"] = resp["ignoreExceptionPatterns"]

                        if "errorLimit" in resp:
                            self._hostinfo_response["errorLimit"] = resp["errorLimit"]

                        if "performance" in resp:
                            self._hostinfo_response["performance"] = resp["performance"]

                return

            if r.status_code == 400:
                c = r.content
                if not c:
                    self._error_logger.error("Atatus transport status 400, failed without content")
                    return

                if compat.PY3:
                    c = c.decode('UTF-8')

                print_message = True
                hostinfo_analytics = False
                resp = json.loads(c)
                if resp:
                    if "tracing" in resp:
                        self._hostinfo_response["tracing"] = resp["tracing"]

                    if "analytics" in resp:
                        self._hostinfo_response["analytics"] = resp["analytics"]

                    if "blocked" in resp:
                        self._blocked = resp["blocked"]

                    if "analytics" in self._hostinfo_response:
                        hostinfo_analytics = self._hostinfo_response["analytics"]
                    
                    if self._blocked and hostinfo_analytics and (endpoint != 'track/apm/analytics/txn'):
                        print_message = False
                    
                    if print_message and "errorMessage" in resp:
                        self._error_logger.error(
                            "Atatus blocked from sending data as: %s ", resp["errorMessage"])

                if print_message:
                    self._error_logger.error("Atatus transport status 400, failed with content: %r", c)
                return

            if r.status_code != 200:
                self._error_logger.error(
                    "Atatus transport unexpected non-200 response [%s] [status_code: %r]." % (self._notify_host + endpoint, r.status_code))

        except Exception as e:
            self._error_logger.debug(
                "Atatus transport [%r] failed with exception: %r", self._notify_host + endpoint, e)
            raise

    def is_performance_disabled(self):
        return "performance" in self._hostinfo_response and self._hostinfo_response["performance"] == False

    def hostinfo(self, start_time):
        payload = self._builder.hostinfo(start_time)
        self._post('track/apm/hostinfo', payload)
        return self._hostinfo_response

    def txns(self, start_time, end_time, data):
        payload = self._builder.txns(start_time, end_time, data)
        disable_performance = self.is_performance_disabled()
        if not disable_performance and self._performance:
            self._post('track/apm/txn', payload)

    def txn_hist(self, start_time, end_time, data):
        if self._capture_percentiles is True:
            payload = self._builder.txn_hist(start_time, end_time, data)
            disable_performance = self.is_performance_disabled()
            if not disable_performance and self._performance:
                self._post('track/apm/txn/histogram', payload)

    def traces(self, start_time, end_time, data):
        payload = self._builder.traces(start_time, end_time, data)
        self._post('track/apm/trace', payload)

    def error_metrics(self, start_time, end_time, metrics_data, requests_data):
        payload = self._builder.error_metrics(start_time, end_time, metrics_data, requests_data)
        disable_performance = self.is_performance_disabled()
        if not disable_performance and self._performance:
            self._post('track/apm/error_metric', payload)

    def errors(self, start_time, end_time, error_data):
        payload = self._builder.errors(start_time, end_time, error_data)
        self._post('track/apm/error', payload)

    def metrics(self, start_time, end_time, metrics_data):
        payload = self._builder.metrics(start_time, end_time, metrics_data)
        disable_performance = self.is_performance_disabled()
        if not disable_performance and self._performance:
            self._post('track/apm/metric', payload)

    def analytics(self, start_time, end_time, analytics_data):
        payload = self._builder.analytics(start_time, end_time, analytics_data)
        disable_performance = self.is_performance_disabled()
        if not disable_performance and self._performance:
            self._post('track/apm/analytics/txn', payload)
