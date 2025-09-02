import os
import sys
import socket
import platform
from .layer import Layer
import atatus
from atatus.utils.stacks import get_lines_from_file
from atatus.utils.package_version_utils import get_plugins

class Builder(object):
    def __init__(self, config, metadata):
        self._config = config
        self._metadata = metadata
        self._hostid = None
        if "hwinfo" in self._metadata:
            if "bootid" in self._metadata["hwinfo"]:
                self._hostid = self._metadata["hwinfo"]["bootid"]

        self._real_hostname = socket.gethostname()

        if not self._hostid:
            self._hostid = self._real_hostname

        self._containerid = None
        if "system" in self._metadata:
            if "container" in self._metadata["system"]:
                if "id" in self._metadata["system"]["container"]:
                    self._containerid = self._metadata["system"]["container"]["id"]

    def _common(self):
        common = {
            "appName": self._config.app_name,
            "licenseKey": self._config.license_key,
            "agent": {
                "name": atatus.PYTHON_AGENT,
                "version": atatus.VERSION
            },
            "hostname": self._config.hostname,
            "hostId": self._hostid,
            "version": self._config.version,
            "metadata": self._metadata
        }
        if self._containerid:
            common["containerId"] = self._containerid

        return common

    def hostinfo(self, start_time):
        payload = self._common()
        payload["timestamp"] = start_time
        payload["environment"] = self._build_hostinfo_obj()
        return payload

    def txns(self, start_time, end_time, data):
        payload = self._common()
        payload["startTime"] = start_time
        payload["endTime"] = end_time
        payload["transactions"] = self._build_txns_obj(data)
        return payload

    def txn_hist(self, start_time, end_time, data):
        payload = self._common()
        payload["startTime"] = start_time
        payload["endTime"] = end_time
        payload["transactions"] = self._build_txn_hist_obj(data)
        return payload

    def traces(self, start_time, end_time, data):
        payload = self._common()
        payload["startTime"] = start_time
        payload["endTime"] = end_time
        payload["traces"] = self._build_traces_obj(data)
        return payload

    def error_metrics(self, start_time, end_time, metrics_data, requests_data):
        payload = self._common()
        payload["startTime"] = start_time
        payload["endTime"] = end_time
        payload["errorMetrics"] = self._build_error_metrics_obj(metrics_data)
        payload["errorRequests"] = self._build_error_requests_obj(requests_data)
        return payload

    def errors(self, start_time, end_time, error_data):
        payload = self._common()
        payload["errors"] = self._build_errors_obj(error_data)
        return payload

    def metrics(self, start_time, end_time, metric_data):
        payload = self._common()
        payload["startTime"] = start_time
        payload["endTime"] = end_time
        payload["python"] = metric_data
        return payload

    def analytics(self, start_time, end_time, analytics_data):
        payload = self._common()
        payload["startTime"] = start_time
        payload["endTime"] = end_time
        payload["requests"] = analytics_data
        return payload

    def _build_hostinfo_obj(self):
        environment = {}
        environment["host"] = self._build_hostinfo_env_host_obj()
        environment["settings"] = self._build_hostinfo_settings()
        environment["python_packages"] = self._build_hostinfo_python_packages()
        return environment

    def _build_hostinfo_env_host_obj(self):
        hostinfo = {}
        hostinfo["hostname"] = self._real_hostname
        if "hwinfo" in self._metadata:
            if "cpu" in self._metadata["hwinfo"]:
                hostinfo["cpu"] = self._metadata["hwinfo"]["cpu"]
            if "mem_size" in self._metadata["hwinfo"]:
                hostinfo["ram"] = self._metadata["hwinfo"]["mem_size"]
            if "bootid" in self._metadata["hwinfo"]:
                hostinfo["bootId"] = self._metadata["hwinfo"]["bootid"]
        hostinfo["hostId"] = self._hostid
        hostinfo["arch"] = platform.machine()
        hostinfo["os"] = platform.system()
        hostinfo["kernel"] = platform.release()

        if self._containerid:
            hostinfo["containerId"] = self._containerid

        # if "system" in self._metadata:
        #     if "kubernetes" in self._metadata["system"]:
        #         hostinfo["kubernetes"] = self._metadata["system"]["kubernetes"]

        return hostinfo

    def _build_hostinfo_settings(self):
        settings = {}
        settings["pythonExecutable"] = sys.executable
        pyversion = platform.python_version_tuple()
        if pyversion:
            settings["pythonVersion"] = '.'.join(pyversion)
        settings["pythonApplication"] = sys.argv[0]
        settings["pythonImplementation"] = platform.python_implementation()

        python_home = os.environ.get("PYTHONHOME", "")
        if python_home:
            settings["envPythonHome"] = python_home

        python_path = os.environ.get("PYTHONPATH", "")
        if python_path:
            settings["envPythonPath"] = python_path

        settings["sysVersion"] = sys.version
        settings["sysPlatform"] = sys.platform
        settings["sysMaxunicode"] = sys.maxunicode

        if "service" in self._metadata:
            if "framework" in self._metadata["service"]:
                if "name" in self._metadata["service"]["framework"]:
                    settings["frameworkName"] = self._metadata["service"]["framework"]["name"]
                if "version" in self._metadata["service"]["framework"]:
                    settings["frameworkVersion"] = self._metadata["service"]["framework"]["version"]

        settings["appName"] = self._config.app_name
        settings["analytics"] = self._config.analytics
        settings["tracing"] = self._config.tracing
        settings["llmobs"] = self._config.llmobs
        settings["performance"] = self._config.performance
        settings["errorLimit"] = self._config.errorLimit
        settings["logBody"] = self._config.capture_body
        settings["traceThreshold"] = (self._config.trace_threshold.total_seconds() * 1000)
        settings["agentVersion"] = atatus.VERSION

        return settings

    def _build_hostinfo_python_packages(self):
        try:
            return get_plugins()
        except Exception as e:
            self._error_logger.debug("An error occurred while getting plugins: %r" % e)
            return {}

    def _build_metric(self, name, value, background=False):
        if not name or not value:
            return {}

        metric = {
            "name": name,
            "type": value.type,
            "kind": value.kind,
            "durations": [value.count, value.total, value.min, value.max]
        }

        if background == True:
            metric["background"] = background

        return metric

    def _build_hist_metric(self, name, value):
        if not name or not value:
            return {}

        hist_metric = {
            "name": name,
            "type": value.type,
            "kind": value.kind,
            "histogram": value.hist
        }

        return hist_metric

    def _build_request(self, context):
        request = {}
        if "request" in context:
            r = context["request"]
            request["method"] = r.get("method", "")
            if "headers" in r:
                h = r["headers"]
                request["accept"] = h.get("accept", "")
                request["accept-encoding"] = h.get("accept-encoding", "")
                request["accept-language"] = h.get("accept-language", "")
                request["userAgent"] = h.get("user-agent", "")

            if "url" in r:
                u = r["url"]
                request["host"] = u.get("hostname", "")
                request["port"] = int(u.get("port", 0))
                request["path"] = u.get("pathname", "")

        if "response" in context:
            if "status_code" in context["response"]:
                request["statusCode"] = context["response"]["status_code"]

        return request

    def _build_custom_data(self, context):
        custom_data = {}
        if "custom" in context and isinstance(context["custom"], dict):
            for key, value in context["custom"].items():
                try:
                    custom_data[str(key)] = str(value)
                except Exception as e:
                    continue

        return custom_data

    def _build_user(self, context):
        user = {}
        if "user" in context:
            if "id" in context["user"]:
                user["id"] = str(context["user"]["id"])

            if "username" in context["user"]:
                user["username"] = context["user"]["username"]

            if "email" in context["user"]:
                user["email"] = context["user"]["email"]

        return user

    def _build_txns_obj(self, data):
        txns = []
        for t, v in data.items():
            txn = self._build_metric(t, v, v.background)
            txn["traces"] = []
            for l, u in v.spans.items():
                txn["traces"].append(self._build_metric(l, u))
            txns.append(txn)
        return txns

    def _build_txn_hist_obj(self, data):
        txn_hists = []
        for t, v in data.items():
            hist = self._build_hist_metric(t, v)
            if hist:
                txn_hists.append(hist)

        return txn_hists

    def _build_traces_obj(self, traces_data):
        traces = []

        for txn in traces_data:
            if not all(k in txn for k in ("name", "id", "timestamp", "duration")):
                continue

            trace = {}
            trace["name"] = txn["name"]
            trace["type"] = self._config.framework_name or atatus.PYTHON_AGENT
            trace["kind"] = atatus.PYTHON_AGENT
            if "background" in txn:
                trace["background"] = txn["background"]
            trace["start"] = (txn["timestamp"] // 1000)
            trace["duration"] = txn["duration"]
            if "context" in txn:
                trace["request"] = self._build_request(txn["context"])
                trace["customData"] = self._build_custom_data(txn["context"])
                trace["user"] = self._build_user(txn["context"])

            trace["txnId"] = txn["id"]
            if "trace_id" in txn:
                trace["traceId"] = txn["trace_id"]
            trace["entries"] = []
            trace["funcs"] = []

            i = 0

            if "spans" in txn:
                for span in txn["spans"]:
                    if not all(k in span for k in ("timestamp", "duration", "name", "subtype", "type")):
                        continue

                    entry = {}
                    entry["lv"] = 1
                    if span["timestamp"] >= txn["timestamp"]:
                        entry["so"] = ((span["timestamp"] - txn["timestamp"]) / 1000)
                    else:
                        entry["so"] = 0
                    entry["du"] = span["duration"]
                    entry["ly"] = {}
                    entry["ly"]["name"] = span["name"]
                    entry["ly"]["type"] = Layer.types_dict.get(span["subtype"], span["subtype"])
                    entry["ly"]["kind"] = Layer.kinds_dict.get(span["type"], span["type"])
                    if "context" in span:
                        if "db" in span["context"]:
                            if "dt" not in entry:
                                entry["dt"] = {}
                            entry["dt"]["db"] = {}
                            if "statement" in span["context"]["db"]:
                                if span["context"]["db"]["statement"] is not None:
                                    entry["dt"]["db"]["statement"] = span["context"]["db"]["statement"]
                            if "type" in span["context"]["db"]:
                                if span["context"]["db"]["type"] is not None:
                                    entry["dt"]["db"]["type"] = span["context"]["db"]["type"]
                            if "instance" in span["context"]["db"]:
                                if span["context"]["db"]["instance"] is not None:
                                    entry["dt"]["db"]["instance"] = span["context"]["db"]["instance"]
                            if "user" in span["context"]["db"]:
                                if span["context"]["db"]["user"] is not None:
                                    entry["dt"]["db"]["user"] = span["context"]["db"]["user"]
                            if "link" in span["context"]["db"]:
                                if span["context"]["db"]["link"] is not None:
                                    entry["dt"]["db"]["link"] = span["context"]["db"]["link"]
                            if "rows_affected" in span["context"]["db"]:
                                if span["context"]["db"]["rows_affected"] is not None:
                                    entry["dt"]["db"]["rows_affected"] = span["context"]["db"]["rows_affected"]

                        if "http" in span["context"]:
                            if "dt" not in entry:
                                entry["dt"] = {}
                            entry["dt"]["http"] = {}
                            if "url" in span["context"]["http"]:
                                if span["context"]["http"]["url"] is not None:
                                    entry["dt"]["http"]["url"] = span["context"]["http"]["url"]
                            if "status_code" in span["context"]["http"]:
                                if span["context"]["http"]["status_code"] is not None:
                                    entry["dt"]["http"]["status_code"] = span["context"]["http"]["status_code"]

                        if "destination" in span["context"]:
                            if "address" in span["context"]["destination"]:
                                if span["context"]["destination"]["address"] is not None:
                                    if "dt" not in entry:
                                        entry["dt"] = {}
                                    if "destination" not in entry["dt"]:
                                        entry["dt"]["destination"] = {}
                                    entry["dt"]["destination"]["address"] = span["context"]["destination"]["address"]
                            if "port" in span["context"]["destination"]:
                                if span["context"]["destination"]["port"] is not None:
                                    if "dt" not in entry:
                                        entry["dt"] = {}
                                    if "destination" not in entry["dt"]:
                                        entry["dt"]["destination"] = {}
                                    entry["dt"]["destination"]["port"] = span["context"]["destination"]["port"]

                    try:
                        func_index = trace["funcs"].index(span["name"])
                    except ValueError:
                        trace["funcs"].append(span["name"])
                        func_index = i
                        i = i + 1
                    entry["i"] = func_index
                    trace["entries"].append(entry)

            if "python_time" in txn:
                entry = {}
                entry["lv"] = 1
                entry["so"] = 0
                entry["du"] = txn["python_time"]
                entry["ly"] = {}
                entry["ly"]["name"] = atatus.PYTHON_AGENT
                entry["ly"]["type"] = atatus.PYTHON_AGENT
                entry["ly"]["kind"] = atatus.PYTHON_AGENT
                try:
                    func_index = trace["funcs"].index(atatus.PYTHON_AGENT)
                except ValueError:
                    trace["funcs"].append(atatus.PYTHON_AGENT)
                    func_index = i
                    i = i + 1
                entry["i"] = func_index
                trace["entries"].append(entry)

            traces.append(trace)

        return traces

    def _build_error_metrics_obj(self, metrics_data):
        error_metrics = []

        for t, v in metrics_data.items():
            error_metric = {}
            error_metric["name"] = t
            error_metric["type"] = self._config.framework_name or atatus.PYTHON_AGENT
            error_metric["kind"] = atatus.PYTHON_AGENT
            error_metric["statusCodes"] = v
            error_metrics.append(error_metric)

        return error_metrics

    def _build_error_requests_obj(self, requests_data):
        error_requests = []

        for v in requests_data:
            if not all(k in v for k in ("name", "timestamp", "context")):
                continue

            error_request = {}
            error_request["name"] = v["name"]
            error_request["type"] = self._config.framework_name or atatus.PYTHON_AGENT
            error_request["kind"] = atatus.PYTHON_AGENT
            error_request["timestamp"] = (v["timestamp"] // 1000)
            error_request["request"] = self._build_request(v["context"])
            error_request["customData"]  = self._build_custom_data(v["context"])
            error_request["user"]  = self._build_user(v["context"])

            error_requests.append(error_request)

        return error_requests

    def _build_errors_obj(self, errors_data):
        errors = []
        for v in errors_data:
            if "timestamp" not in v:
                continue

            errorObj = {}
            if "exception" in v:
                errorObj = v["exception"]
            elif "log" in v:
                errorObj = v["log"]
            else:
                continue

            if "message" not in errorObj:
                continue

            error = {}
            error["timestamp"] = (v["timestamp"] // 1000)

            if "event_transaction_name" in v:
                error["transaction"] = v["event_transaction_name"]

            if "background" in v:
                error["background"] = v["background"]
            if "transaction_id" in v:
                error["txnId"] = v["transaction_id"]

            if "span_id" in v:
                error["spanId"] = v["span_id"]
            if "trace_id" in v:
                error["traceId"] = v["trace_id"]

            if "context" in v:
                error["request"] = self._build_request(v["context"])
                error["customData"]  = self._build_custom_data(v["context"])
                error["user"]  = self._build_user(v["context"])

            error["exceptions"] = []
            exception = {}
            if "type" in errorObj:
                exception["class"] = errorObj["type"]
            elif "level" in errorObj:
                exception["class"] = errorObj["level"]
            else:
                exception["class"] = "Unknown"

            exception["message"] = errorObj["message"]
            exception["stacktrace"] = []
            if "stacktrace" in errorObj:
                for f in errorObj["stacktrace"]:
                    if not all(k in f for k in ("filename", "function", "lineno", "library_frame")):
                        continue

                    frame = {}
                    frame["f"] = f["filename"]
                    frame["m"] = f["function"]
                    frame["ln"] = f["lineno"]
                    if f["library_frame"] is False:
                        frame["inp"] = True

                    if "context_metadata" in f:
                        fname, lineno, context_lines, loader, module_name = f.pop("context_metadata")
                        pre_context, context_line, post_context = get_lines_from_file(
                            fname, lineno, context_lines, loader, module_name
                        )
                        if context_line:
                            f["pre_context"] = pre_context
                            f["context_line"] = context_line
                            f["post_context"] = post_context

                        if "context_line" in f:
                            frame["code"] = []

                            if "pre_context" in f:
                                psize = len(f["pre_context"])
                                lineno = 0
                                if f["lineno"] - psize > 0:
                                    lineno = f["lineno"] - psize
                                for c in f["pre_context"]:
                                    frame["code"].append([str(lineno), c])
                                    lineno += 1

                            frame["code"].append([str(f["lineno"]), f["context_line"]])

                            if "post_context" in f:
                                psize = len(f["post_context"])
                                lineno = f["lineno"] + 1
                                for c in f["post_context"]:
                                    frame["code"].append([str(lineno), c])
                                    lineno += 1

                    exception["stacktrace"].append(frame)

            error["exceptions"].append(exception)
            errors.append(error)
        return errors
