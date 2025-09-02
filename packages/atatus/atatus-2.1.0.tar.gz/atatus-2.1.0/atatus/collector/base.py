import time
import json
import sched
import random
import threading
import traceback
from atatus.utils.logging import get_logger
from atatus.utils import encoding
from .transport import BaseTransport
from .layer import Layer
from .hist import TxnHist

import urllib.parse
from atatus.utils.module_import import import_string
from atatus.conf.constants import ERROR, SPAN, TRANSACTION, METRICSET

import atatus
from collections import namedtuple
SpanTiming = namedtuple('SpanTiming', 'start end')
ERROR_LIMIT = 200

class Txn(Layer):
    def __init__(self, type, kind, duration, background):
        super(Txn, self).__init__(type, kind, duration)
        self.spans = {}
        self.background = background


class Collector(object):
    def __init__(self, client, transport_kwargs):

        metadata = None
        if "metadata" in transport_kwargs:
            metadata = transport_kwargs["metadata"]

        analytics_processors = None
        if "analytics_processors" in transport_kwargs:
            analytics_processors = transport_kwargs["analytics_processors"]

        self._client = client
        self._config = self._client.config
        self._config.llm_active = False
        cls = self.__class__
        self._error_logger = get_logger("atatus.errors")
        self._logger = get_logger("%s.%s" % (cls.__module__, cls.__name__))

        if not self._config.app_name and not self._config.license_key:
            self._error_logger.error("Error: Atatus configuration app_name and license_key are missing!")
        elif not self._config.license_key:
            self._error_logger.error("Error: Atatus configuration license_key is missing!")
        elif not self._config.app_name:
            self._error_logger.error("Error: Atatus configuration app_name is missing!")

        self._spans = {}
        self._txns_lock = threading.Lock()
        self._txns_agg = {}
        self._txn_hist_agg = {}
        self._traces_agg = []
        self._error_metrics_agg = {}
        self._error_requests_agg = []

        self._errors_lock = threading.Lock()
        self._errors_agg = []

        self._metrics_lock = threading.Lock()
        self._metrics_agg = []

        self._analytics = self._config.analytics
        self._analytics_lock = threading.Lock()
        self._analytics_agg = []

        self._hostinfo_response = {}
        self._hostinfo_response["analytics"] = True

        self._transport = BaseTransport(self._config, metadata)
        self._collect_counter = 0

        self._scheduler = None
        self._start_time = int(time.time() * 1000)
        self._worker = None
        self._closed = False
        # self._pid = None
        self._thread_starter_lock = threading.Lock()
        self._analytics_processors = analytics_processors if analytics_processors is not None else []

        self._tracing = self._config.tracing
        self._error_limit = self._config.errorLimit if self._config.errorLimit else ERROR_LIMIT
        self._hostinfo_response["tracing"] = True

        if self._hostinfo_response["tracing"] == True and self._tracing is True:
            dt_endpoint_url = urllib.parse.urljoin(
                self._config.notify_host,
                "/track/traces/spans",
            )        
            transport_class = import_string(self._config.transport_class)
            self._dt_transport = transport_class(url=dt_endpoint_url, client=self._client, **transport_kwargs)
            self._config.transport = self._dt_transport
            self._client._thread_managers["transport"] = self._dt_transport        


    def _start_collector_thread(self):
        if (not self._worker or not self._worker.is_alive()) and not self._closed:
            try:
                self._worker = threading.Thread(target=self._worker_thread, name="Atatus Collector Worker")
                self._worker.setDaemon(True)
                self._worker_exit = threading.Event()
                self._worker.start()
            except RuntimeError:
                pass

    def _ensure_collector_running(self):
        with self._thread_starter_lock:
            self._start_collector_thread()
            # check if self._pid is the same as os.getpid(). If they are not the same, it means that our
            # process was forked at some point, so we need to start another processor thread
            # if self._pid != os.getpid():
            #     self._start_collector_thread()
            #     self._pid = os.getpid()

    def close(self):
        if self._closed:
            return
        if not self._worker or not self._worker.is_alive():
            return
        self._closed = True
        self._worker_exit.set()
        if self._worker.is_alive():
            self._worker.join(10)

    def _worker_timefunc(self):
        if self._worker_exit.isSet():
            return float("inf")
        return time.time()

    def _worker_thread(self):
        self._scheduler = sched.scheduler(self._worker_timefunc, self._worker_exit.wait)
        self._start_time = int(time.time() * 1000)
        self._scheduler.enter(60.0, 1, self._collect, ())
        try:
            self._scheduler.run()
        except Exception as e:
            self._error_logger.error("Atatus worker failed with exception: %r", e)
            self._error_logger.error(traceback.format_exc())

    def _collect(self):
        start_time = self._start_time

        if not self._worker_exit.isSet():
            self._start_time = int(time.time() * 1000)
            self._scheduler.enter(60.0, 1, self._collect, ())

        end_time = int(time.time() * 1000)

        if not self._config.app_name or not self._config.license_key:
            if not self._config.app_name and not self._config.license_key:
                self._error_logger.error("Error: Atatus configuration app_name and license_key are missing!")
            elif not self._config.license_key:
                self._error_logger.error("Error: Atatus configuration license_key is missing!")
            elif not self._config.app_name:
                self._error_logger.error("Error: Atatus configuration app_name is missing!")
            return

        with self._txns_lock:
            txns_data = self._txns_agg
            self._txns_agg = {}

            txn_hist_data = self._txn_hist_agg
            self._txn_hist_agg = {}

            traces_data = self._traces_agg
            self._traces_agg = []

            error_metrics_data = self._error_metrics_agg
            self._error_metrics_agg = {}

            error_requests_data = self._error_requests_agg
            self._error_requests_agg = []

        with self._errors_lock:
            errors_data = self._errors_agg
            self._errors_agg = []

        with self._metrics_lock:
            metrics_data = self._metrics_agg
            self._metrics_agg = []

        with self._analytics_lock:
            analytics_data = self._analytics_agg
            self._analytics_agg = []

        try:
            if self._collect_counter % 30 == 0:
                self._hostinfo_response = self._transport.hostinfo(start_time)
                self._collect_counter = 0
            self._collect_counter += 1
            
            if txns_data:
                self._transport.txns(start_time, end_time, txns_data)

            if txn_hist_data:
                self._transport.txn_hist(start_time, end_time, txn_hist_data)

            if traces_data:
                for trace in traces_data:
                    individual_trace_data = [trace]
                    self._transport.traces(start_time, end_time, individual_trace_data)

            if error_metrics_data:
                self._transport.error_metrics(start_time, end_time, error_metrics_data, error_requests_data)

            if errors_data:
                self._transport.errors(start_time, end_time, errors_data)

            if metrics_data:
                self._transport.metrics(start_time, end_time, metrics_data)

            if analytics_data:
                if "analytics" in self._hostinfo_response:
                    if self._hostinfo_response["analytics"] == True and self._analytics == True:
                        analytics_sanitized_data = []
                        analytics_payload_len = 0
                        for event in analytics_data:
                            sevent = self._process_analytics_event(event)
                            if sevent != None:
                                analytics_sanitized_data.append(sevent)
                                if "body_len" in sevent:
                                    analytics_payload_len += sevent["body_len"]
                                if analytics_payload_len > 6 * 1024 * 1024:
                                    self._transport.analytics(start_time, end_time, analytics_sanitized_data)
                                    analytics_sanitized_data = []
                                    analytics_payload_len = 0
                        if len(analytics_sanitized_data) > 0:
                            self._transport.analytics(start_time, end_time, analytics_sanitized_data)

        except Exception as e:
            self._error_logger.debug("Atatus collect failed with exception: %r" % e)
            self._error_logger.debug(traceback.format_exc())

    def _process_analytics_event(self, data):
        # Run the data through processors
        for processor in self._analytics_processors:
            try:
                data = processor(self._client, data)
                if not data:
                    return None
            except Exception:
                return None
        return data

    def add_error(self, error):
        self._ensure_collector_running()

        skip_event = False
        if self._config.skip_processor is not None:
            error_txn_name = ""
            if "event_transaction_name" in error:
                error_txn_name = error["event_transaction_name"]

            error_url = ""
            if "context" in error and \
                "request" in error["context"] and \
                "url" in error["context"]["request"] and \
                "full" in error["context"]["request"]["url"]:
                    error_url = error["context"]["request"]["url"]["full"]
            try:
                skip_event_dict = {}
                skip_event_dict["name"] = error_txn_name
                skip_event_dict["url"] = error_url
                skip_event = self._config.skip_processor(skip_event_dict)
            except Exception as e:
                self._error_logger.debug("error skip function failed with exception: %r" % e)
                pass

        if skip_event == True:
            if "event_transaction_name" in error:
                self._error_logger.debug("skipping error event: %r" % error["event_transaction_name"])
            return

        with self._errors_lock:
            limit = self._hostinfo_response["errorLimit"] if "errorLimit" in self._hostinfo_response else self._error_limit
            if len(self._errors_agg) < limit:
                self._errors_agg.append(error)
            else:
                self._errors_agg = self._errors_agg[:limit]
                i = random.randrange(limit)
                self._errors_agg[i] = error

    def add_metricset(self, metricset):
        self._ensure_collector_running()

        if "samples" not in metricset:
            return
        s = metricset["samples"]

        if not all(k in s for k in ("system.cpu.total.norm.pct", "system.memory.actual.free", "system.memory.total", "system.process.cpu.total.norm.pct", "system.process.memory.size", "system.process.memory.rss.bytes")):
            return

        if not all("value" in s[k] for k in ("system.cpu.total.norm.pct", "system.memory.actual.free", "system.memory.total", "system.process.cpu.total.norm.pct", "system.process.memory.size", "system.process.memory.rss.bytes")):
            return

        metric = {
            "system.cpu.total.norm.pct": s["system.cpu.total.norm.pct"]["value"],
            "system.memory.actual.free": s["system.memory.actual.free"]["value"],
            "system.memory.total": s["system.memory.total"]["value"],
            "system.process.cpu.total.norm.pct": s["system.process.cpu.total.norm.pct"]["value"],
            "system.process.memory.size": s["system.process.memory.size"]["value"],
            "system.process.memory.rss.bytes": s["system.process.memory.rss.bytes"]["value"]
        }

        with self._metrics_lock:
            self._metrics_agg.append(metric)

    def add_analytics(self, txn):
        analytics_txn = {}

        if not all(k in txn for k in ("name", "id", "timestamp", "duration")):
            return

        analytics_txn["timestamp"] = (txn["timestamp"] // 1000)
        analytics_txn["txnId"] = txn["id"]
        if "trace_id" in txn:
            analytics_txn["traceId"] = txn["trace_id"]
        
        analytics_txn["name"] = txn["name"]
        analytics_txn["duration"] = txn["duration"]

        requestBodyLen = 0
        responseBodyLen = 0
        if "context" in txn and \
            "request" in txn["context"]:

            if "method" in txn["context"]["request"]:
                analytics_txn["method"] = txn["context"]["request"]["method"]

            if "headers" in txn["context"]["request"]:
                analytics_txn["requestHeaders"] = txn["context"]["request"]["headers"]
                if "User-Agent" in analytics_txn["requestHeaders"]:
                    analytics_txn["userAgent"] = analytics_txn["requestHeaders"]["User-Agent"]
                elif "user-agent" in analytics_txn["requestHeaders"]:
                    analytics_txn["userAgent"] = analytics_txn["requestHeaders"]["user-agent"]

            if "body" in txn["context"]["request"]:
                if txn["context"]["request"]["body"] != "[REDACTED]":
                    if txn["context"]["request"]["body"] != "":
                        instance_dict_convert = False
                        string_body = ""
                        if isinstance(txn["context"]["request"]["body"], dict):
                            try:
                                string_body = json.dumps(txn["context"]["request"]["body"])
                                instance_dict_convert = True
                            except Exception:
                                pass
                        if instance_dict_convert == False:
                            string_body = str(txn["context"]["request"]["body"])

                        analytics_txn["requestBody"] = encoding.body_field(string_body)
                        requestBodyLen = len(analytics_txn["requestBody"])

            if "url" in txn["context"]["request"]:
                if "full" in txn["context"]["request"]["url"]:
                    analytics_txn["url"] = txn["context"]["request"]["url"]["full"]

            if "socket" in txn["context"]["request"]:
                if "remote_address" in txn["context"]["request"]["socket"]:
                    analytics_txn["ip"] = txn["context"]["request"]["socket"]["remote_address"]

        if "context" in txn and \
            "response" in txn["context"]:
                if "body" in txn["context"]["response"]:
                    analytics_txn["responseBody"] = txn["context"]["response"]["body"]
                    responseBodyLen = len(analytics_txn["responseBody"])

        if "context" in txn and \
            "custom_response" in txn["context"]:
                if "body" in txn["context"]["custom_response"]:
                    analytics_txn["responseBody"] = txn["context"]["custom_response"]["body"]
                    responseBodyLen = len(analytics_txn["responseBody"])

        if "context" in txn and \
            "response" in txn["context"]:

            if "headers" in txn["context"]["response"]:
                analytics_txn["responseHeaders"] = txn["context"]["response"]["headers"]

            if "status_code" in txn["context"]["response"]:
                analytics_txn["statusCode"] = txn["context"]["response"]["status_code"]

            # analytics_txn["customData"] = txn.context.custom

        if "context" in txn and \
            "custom" in txn["context"] and \
            isinstance(txn["context"]["custom"], dict):
            custom_data = {}
            for k, v in txn["context"]["custom"].items():
                try:
                    custom_data[str(k)] = str(v)
                except Exception as e:
                    continue
            analytics_txn["customData"] = custom_data

        if "context" in txn and \
            "user" in txn["context"]:
            
            if "id" in txn["context"]["user"]:
                analytics_txn["userId"] = str(txn["context"]["user"]["id"])

            if "username" in txn["context"]["user"]:
                analytics_txn["userName"] = txn["context"]["user"]["username"]

            if "email" in txn["context"]["user"]:
                analytics_txn["userEmail"] = txn["context"]["user"]["email"]

        if "context" in txn and \
            "company" in txn["context"]:

            if "id" in txn["context"]["company"]:
                analytics_txn["companyId"] = str(txn["context"]["company"]["id"])

        analytics_txn["body_len"] = requestBodyLen + responseBodyLen
        analytics_txn["direction"] = "incoming"
        with self._analytics_lock:
            if len(self._analytics_agg) < 10000:
                skip_event = False

                if self._config.analytics_skip_processor is not None:
                    try:
                        skip_event = self._config.analytics_skip_processor(analytics_txn)
                    except Exception as e:
                        self._error_logger.debug("analytics skip function failed with exception: %r" % e)
                        pass

                if skip_event == False:
                    if self._config.analytics_mask_processor is not None:
                        try:
                            self._config.analytics_mask_processor(analytics_txn)
                        except Exception as e:
                            self._error_logger.debug("mask function failed with exception: %r" % e)
                            pass
                    self._analytics_agg.append(analytics_txn)
                else:
                    if "name" in analytics_txn:
                        self._error_logger.debug("skipping analytics event: %r" % analytics_txn["name"])

    def add_analytics_outgoing(self, txn, span):
        analytics_txn = {}

        if not all(k in txn for k in ("name", "id", "timestamp", "duration")):
            return

        if not all(k in span for k in ("name", "timestamp", "duration", "context")):
            return

        if "analytics_captured" not in span["context"]:
            return

        analytics_txn["timestamp"] = (txn["timestamp"] // 1000)
        analytics_txn["txnId"] = txn["id"]
        if "trace_id" in txn:
            analytics_txn["traceId"] = txn["trace_id"]
        
        analytics_txn["name"] = span["name"]
        analytics_txn["duration"] = span["duration"]

        requestBodyLen = 0
        responseBodyLen = 0
        if "context" in span and \
            "http" in span["context"] and \
            "request" in span["context"]["http"]:

            if "method" in span["context"]["http"]["request"]:
                analytics_txn["method"] = span["context"]["http"]["request"]["method"]

            if "headers" in span["context"]["http"]["request"]:
                analytics_txn["requestHeaders"] = span["context"]["http"]["request"]["headers"]
                if "User-Agent" in analytics_txn["requestHeaders"]:
                    analytics_txn["userAgent"] = analytics_txn["requestHeaders"]["User-Agent"]
                elif "user-agent" in analytics_txn["requestHeaders"]:
                    analytics_txn["userAgent"] = analytics_txn["requestHeaders"]["user-agent"]

            if "body" in span["context"]["http"]["request"]:
                if span["context"]["http"]["request"]["body"] != "[REDACTED]":
                    if span["context"]["http"]["request"]["body"] != "":
                        instance_dict_convert = False
                        string_body = ""
                        if isinstance(span["context"]["http"]["request"]["body"], dict):
                            try:
                                string_body = json.dumps(span["context"]["http"]["request"]["body"])
                                instance_dict_convert = True
                            except Exception:
                                pass
                        if instance_dict_convert == False:
                            string_body = str(span["context"]["http"]["request"]["body"])

                        analytics_txn["requestBody"] = encoding.body_field(string_body)
                        requestBodyLen = len(analytics_txn["requestBody"])

        if "context" in span and \
            "http" in span["context"] and \
            "response" in span["context"]["http"]:
                if "headers" in span["context"]["http"]["response"]:
                     analytics_txn["responseHeaders"] = span["context"]["http"]["response"]["headers"]

                if "body" in span["context"]["http"]["response"]:
                    analytics_txn["responseBody"] = span["context"]["http"]["response"]["body"]
                    responseBodyLen = len(analytics_txn["responseBody"])

        if "context" in span and \
            "http" in span["context"]:
            
            if "url" in span["context"]["http"]:
                analytics_txn["url"] = span["context"]["http"]["url"]
            if "status_code" in span["context"]["http"]:
                analytics_txn["statusCode"] = span["context"]["http"]["status_code"]

        if "context" in txn and \
            "user" in txn["context"]:
            
            if "id" in txn["context"]["user"]:
                analytics_txn["userId"] = str(txn["context"]["user"]["id"])

            if "username" in txn["context"]["user"]:
                analytics_txn["userName"] = txn["context"]["user"]["username"]

            if "email" in txn["context"]["user"]:
                analytics_txn["userEmail"] = txn["context"]["user"]["email"]

        if "context" in txn and \
            "company" in txn["context"]:

            if "id" in txn["context"]["company"]:
                analytics_txn["companyId"] = str(txn["context"]["company"]["id"])

        analytics_txn["body_len"] = requestBodyLen + responseBodyLen
        analytics_txn["direction"] = "outgoing"
        with self._analytics_lock:
             if len(self._analytics_agg) < 10000:
                skip_event = False
                if self._config.analytics_skip_processor is not None:
                    try:
                        skip_event = self._config.analytics_skip_processor(analytics_txn)
                    except Exception as e:
                        self._error_logger.debug("analytics outgoing skip function failed with exception: %r" % e)
                        pass

                if skip_event == False:
                    if self._config.analytics_mask_processor is not None:
                        try:
                            self._config.analytics_mask_processor(analytics_txn)
                        except Exception as e:
                            self._error_logger.debug("mask function failed with exception: %r" % e)
                            pass
                    self._analytics_agg.append(analytics_txn)
                else:
                    if "name" in analytics_txn:
                        self._error_logger.debug("skipping analytics event: %r" % analytics_txn["name"])

    def add_span(self, span):

        if "tracing" in self._hostinfo_response and self._hostinfo_response["tracing"] == True and self._tracing is True:
            if not self._config.llm_active and span['type'] == 'llmobs':
                self._config.llm_active = True
            self._dt_transport.queue(SPAN, span)

        if not all(k in span for k in ("transaction_id", "name", "type", "subtype", "duration")):
            return

        span_id = span["transaction_id"]
        if span_id not in self._spans:
            self._spans[span_id] = [span]
        else:
            self._spans[span_id].append(span)

    def add_txn(self, txn):
        if "tracing" in self._hostinfo_response and self._hostinfo_response["tracing"] == True and self._tracing is True:
            if not self._config.llm_active and txn['type'] == 'llmobs':
                self._config.llm_active = True
            self._dt_transport.queue(TRANSACTION, txn)

        self._ensure_collector_running()

        if not all(k in txn for k in ("name", "id", "timestamp", "duration")):
            return
        txn_name = txn["name"]
        if not txn_name:
            txn_id = txn["id"]
            if txn_id:
                if txn_id in self._spans:
                    del self._spans[txn_id]
            return

        if txn["duration"] <= 0:
            return

        skip_event = False
        if self._config.skip_processor is not None:
            txn_url = ""
            if "context" in txn and \
                "request" in txn["context"] and \
                "url" in txn["context"]["request"] and \
                "full" in txn["context"]["request"]["url"]:
                    txn_url = txn["context"]["request"]["url"]["full"]
            try:
                skip_event_dict = {}
                skip_event_dict["name"] = txn_name
                skip_event_dict["url"] = txn_url
                skip_event = self._config.skip_processor(skip_event_dict)
            except Exception as e:
                self._error_logger.debug("txn skip function failed with exception: %r" % e)
                pass

        if skip_event == True:
            self._error_logger.debug("skipping txn event: %r" % txn_name)
            txn_id = txn["id"]
            if txn_id in self._spans:
                del self._spans[txn_id]
            return

        with self._txns_lock:
            if self._config.framework_name:
                txn_type = self._config.framework_name
            else:
                txn_type = atatus.PYTHON_AGENT

            background = False
            if "type" in txn:
                if txn["type"] == 'celery':
                    background=True

            if txn_name not in self._txns_agg:
                self._txns_agg[txn_name] = Txn(txn_type, atatus.PYTHON_AGENT, txn["duration"], background=background)
            else:
                self._txns_agg[txn_name].aggregate(txn["duration"])

            if background is False and txn["duration"] <= 150*1000.0:
                if txn_name not in self._txn_hist_agg:
                    self._txn_hist_agg[txn_name] = TxnHist(txn_type, atatus.PYTHON_AGENT, txn["duration"])
                else:
                    self._txn_hist_agg[txn_name].aggregate(txn["duration"])

            spans_present = False

            txn_id = txn["id"]
            python_time = 0
            spans_tuple = []
            if txn_id in self._spans:
                spans_present = True
                for span in self._spans[txn_id]:
                    if not all(k in span for k in ("name", "type", "subtype", "timestamp", "duration")):
                        continue
                    span_name = span["name"]
                    if not span_name:
                        continue
                    if span["timestamp"] >= txn["timestamp"]:
                        timestamp = ((span["timestamp"] - txn["timestamp"]) / 1000)
                        spans_tuple.append(SpanTiming(timestamp, timestamp + span["duration"]))

                        if self._config.analytics_capture_outgoing is True:
                            if span["type"] == "external" and span["subtype"] == "http":
                                if "analytics" in self._hostinfo_response:
                                    if self._hostinfo_response["analytics"] == True and self._analytics == True:
                                        if background == False:
                                            self.add_analytics_outgoing(txn, span)

                        if span_name not in self._txns_agg[txn_name].spans:
                            kind = Layer.kinds_dict.get(span["type"], span["type"])
                            type = Layer.types_dict.get(span["subtype"], span["subtype"])
                            self._txns_agg[txn_name].spans[span_name] = Layer(type, kind, span["duration"])
                        else:
                            self._txns_agg[txn_name].spans[span_name].aggregate(span["duration"])

            if len(spans_tuple) == 0:
                python_time = txn["duration"]
            else:
                spans_tuple.sort(key=lambda x: x.start)
                python_time = spans_tuple[0].start
                span_end = spans_tuple[0].end
                j = 0
                while j < len(spans_tuple):
                    if spans_tuple[j].start > span_end:
                        python_time += spans_tuple[j].start - span_end
                        span_end = spans_tuple[j].end
                    else:
                        if spans_tuple[j].end > span_end:
                            span_end = spans_tuple[j].end
                    j += 1
                if txn["duration"] > span_end:
                    python_time += txn["duration"] - span_end

            if python_time > 0:
                self._txns_agg[txn_name].spans[atatus.PYTHON_AGENT] = Layer(
                    atatus.PYTHON_AGENT, atatus.PYTHON_AGENT, python_time)

            if spans_present is True or python_time > 0:
                if txn["duration"] >= (self._config.trace_threshold.total_seconds() * 1000):
                    trace_txn = txn.copy()
                    if spans_present is True:
                        trace_txn["spans"] = self._spans[txn_id]
                    if python_time > 0:
                        trace_txn["python_time"] = python_time
                    trace_txn["background"] = background

                    if len(self._traces_agg) < 5:
                        self._traces_agg.append(trace_txn)
                    else:
                        i = random.randrange(5)
                        self._traces_agg[i] = trace_txn

            if spans_present:
                del self._spans[txn_id]

            if "context" in txn and \
               "response" in txn["context"] and \
               "status_code" in txn["context"]["response"]:

                status_code = txn["context"]["response"]["status_code"]

                if status_code >= 400 and status_code != 404:
                    if txn_name not in self._error_metrics_agg:
                        self._error_metrics_agg[txn_name] = {status_code: 1}
                    else:
                        if status_code not in self._error_metrics_agg[txn_name]:
                            self._error_metrics_agg[txn_name][status_code] = 1
                        else:
                            self._error_metrics_agg[txn_name][status_code] += 1

                    if len(self._error_requests_agg) < ERROR_LIMIT:
                        self._error_requests_agg.append({"name": txn_name, "timestamp": txn["timestamp"], "context": txn["context"]})
                    else:
                        i = random.randrange(ERROR_LIMIT)
                        self._error_requests_agg[i] = {"name": txn_name, "timestamp": txn["timestamp"], "context": txn["context"]}

            if "analytics" in self._hostinfo_response:
                if self._hostinfo_response["analytics"] == True and self._analytics == True:
                    if background == False:
                        self.add_analytics(txn)
