#  BSD 3-Clause License
#
#  Copyright (c) 2019, Elasticsearch BV
#  All rights reserved.
#
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions are met:
#
#  * Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
#
#  * Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
#  * Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
#  AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#  IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#  DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
#  FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
#  DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
#  SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
#  CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
#  OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
#  OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from atatus.instrumentation.packages.base import AbstractInstrumentedModule
from atatus.traces import execution_context
from atatus.traces import capture_span
from atatus.utils import get_host_from_url, sanitize_url, get_external_headers, external_body_decode
from atatus.utils.encoding import long_field
from atatus.conf import constants


class RequestsInstrumentation(AbstractInstrumentedModule):
    name = "requests"

    instrument_list = [("requests.sessions", "Session.send")]

    def call(self, module, method, wrapped, instance, args, kwargs):
        capture_req_body = False
        capture_res_body = False
        analytics = False
        analytics_capture_outgoing = False
        transaction = execution_context.get_transaction()
        log_body_content_types = []
        if transaction:
            analytics = transaction.tracer.config.analytics
            log_body_content_types = transaction.tracer.config.log_body_content_types
            analytics_capture_outgoing = transaction.tracer.config.analytics_capture_outgoing
            if analytics is True and analytics_capture_outgoing is True:
                capture_req_body = transaction.tracer.config.capture_body in ("all", "request")
                capture_res_body = transaction.tracer.config.capture_body in ("all", "response")

        if "request" in kwargs:
            request = kwargs["request"]
        else:
            request = args[0]

        req_method = request.method.upper()
        if req_method not in constants.HTTP_WITH_BODY:
            capture_req_body = False
        signature = req_method
        signature += " " + get_host_from_url(request.url)
        url = sanitize_url(request.url)

        req_headers = {}
        req_body = ""
        
        if analytics is True and analytics_capture_outgoing is True:
            req_headers = get_external_headers(request.headers)

            if capture_req_body is True:
                if request.body:
                    data = ""
                    try:
                        if isinstance(request.body, bytes):
                            data = external_body_decode(request.body)
                        else:
                            data = request.body
                    except Exception as e:
                        data = "<unavailable>"

                    if data is not None:
                        # Can we apply this as a processor instead?
                        # https://github.com/elastic/apm-agent-python/issues/305
                        req_body = long_field(data)

        with capture_span(
            signature,
            span_type="external",
            span_subtype="http",
            extra={"http": {"url": url}},
            leaf=True,
        ) as span:
            response = wrapped(*args, **kwargs)
            # requests.Response objects are falsy if status code > 400, so we have to check for None instead
            if response is not None:
                res_headers = {}
                res_body = ""

                captureContent = False
                if analytics is True and analytics_capture_outgoing is True:
                    res_headers = get_external_headers(response.headers)
                    if "Content-Type" in res_headers:
                        contentType = res_headers["Content-Type"]
                        for ct in log_body_content_types:
                            if ct in contentType:
                                captureContent = True
                                break

                    if capture_res_body is True and captureContent is True:
                        if response.content:
                            data = ""
                            try:
                                if isinstance(response.content, bytes):
                                    data = external_body_decode(response.content)
                                else:
                                    data = response.content
                            except Exception as e:
                                data = "<unavailable>"
                            if data is not None:
                                # Can we apply this as a processor instead?
                                # https://github.com/elastic/apm-agent-python/issues/305
                                res_body = long_field(data)

                if span.context:
                    span.context["http"]["status_code"] = response.status_code
                    if analytics is True and analytics_capture_outgoing is True:
                        span.context["analytics_captured"] = True

                        span.context["http"]["request"] = {}
                        span.context["http"]["request"]["method"] = req_method
                        span.context["http"]["request"]["headers"] = req_headers
                        if capture_req_body is True:
                            span.context["http"]["request"]["body"] = req_body
                    
                        span.context["http"]["response"] = {}
                        span.context["http"]["response"]["headers"] = res_headers
                        if capture_res_body is True and captureContent is True:
                            span.context["http"]["response"]["body"] = res_body

                span.set_success() if response.status_code < 400 else span.set_failure()
            return response
