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

import sys

from atatus.utils.module_import import import_string

_cls_register = {
    "atatus.instrumentation.packages.botocore.BotocoreInstrumentation",
    "atatus.instrumentation.packages.httpx.sync.httpx.HttpxClientInstrumentation",
    "atatus.instrumentation.packages.jinja2.Jinja2Instrumentation",
    "atatus.instrumentation.packages.psycopg.PsycopgInstrumentation",
    "atatus.instrumentation.packages.psycopg2.Psycopg2Instrumentation",
    "atatus.instrumentation.packages.psycopg2.Psycopg2ExtensionsInstrumentation",
    "atatus.instrumentation.packages.mysql.MySQLInstrumentation",
    "atatus.instrumentation.packages.mysql_connector.MySQLConnectorInstrumentation",
    "atatus.instrumentation.packages.pymysql.PyMySQLConnectorInstrumentation",
    "atatus.instrumentation.packages.pylibmc.PyLibMcInstrumentation",
    "atatus.instrumentation.packages.pymongo.PyMongoInstrumentation",
    "atatus.instrumentation.packages.pymongo.PyMongoBulkInstrumentation",
    "atatus.instrumentation.packages.pymongo.PyMongoCursorInstrumentation",
    "atatus.instrumentation.packages.python_memcached.PythonMemcachedInstrumentation",
    "atatus.instrumentation.packages.pymemcache.PyMemcacheInstrumentation",
    "atatus.instrumentation.packages.redis.RedisInstrumentation",
    "atatus.instrumentation.packages.redis.RedisPipelineInstrumentation",
    "atatus.instrumentation.packages.redis.RedisConnectionInstrumentation",
    "atatus.instrumentation.packages.requests.RequestsInstrumentation",
    "atatus.instrumentation.packages.sqlite.SQLiteInstrumentation",
    "atatus.instrumentation.packages.urllib3.Urllib3Instrumentation",
    "atatus.instrumentation.packages.elasticsearch.ElasticsearchConnectionInstrumentation",
    "atatus.instrumentation.packages.elasticsearch.ElasticsearchTransportInstrumentation",
    "atatus.instrumentation.packages.cassandra.CassandraInstrumentation",
    "atatus.instrumentation.packages.pymssql.PyMSSQLInstrumentation",
    "atatus.instrumentation.packages.pyodbc.PyODBCInstrumentation",
    "atatus.instrumentation.packages.django.template.DjangoTemplateInstrumentation",
    "atatus.instrumentation.packages.django.template.DjangoTemplateSourceInstrumentation",
    "atatus.instrumentation.packages.urllib.UrllibInstrumentation",
    "atatus.instrumentation.packages.graphql.GraphQLExecutorInstrumentation",
    "atatus.instrumentation.packages.graphql.GraphQLBackendInstrumentation",
    "atatus.instrumentation.packages.httpx.sync.httpcore.HTTPCoreInstrumentation",
    "atatus.instrumentation.packages.httplib2.Httplib2Instrumentation",
    "atatus.instrumentation.packages.azure.AzureInstrumentation",
    "atatus.instrumentation.packages.kafka.KafkaInstrumentation",
    "atatus.instrumentation.packages.grpc.GRPCClientInstrumentation",
    "atatus.instrumentation.packages.grpc.GRPCServerInstrumentation",
    "atatus.instrumentation.packages.opentelemetry.OtelTracerInstrumentation",
}

if sys.version_info >= (3, 7):
    _cls_register.update(
        [
            "atatus.instrumentation.packages.asyncio.sleep.AsyncIOSleepInstrumentation",
            "atatus.instrumentation.packages.asyncio.aiohttp_client.AioHttpClientInstrumentation",
            "atatus.instrumentation.packages.httpx.async.httpx.HttpxAsyncClientInstrumentation",
            "atatus.instrumentation.packages.asyncio.elasticsearch.ElasticSearchAsyncConnection",
            "atatus.instrumentation.packages.asyncio.elasticsearch.ElasticsearchAsyncTransportInstrumentation",
            "atatus.instrumentation.packages.asyncio.aiopg.AioPGInstrumentation",
            "atatus.instrumentation.packages.asyncio.asyncpg.AsyncPGInstrumentation",
            "atatus.instrumentation.packages.tornado.TornadoRequestExecuteInstrumentation",
            "atatus.instrumentation.packages.tornado.TornadoHandleRequestExceptionInstrumentation",
            "atatus.instrumentation.packages.tornado.TornadoRenderInstrumentation",
            "atatus.instrumentation.packages.httpx.async.httpcore.HTTPCoreAsyncInstrumentation",
            "atatus.instrumentation.packages.asyncio.aioredis.RedisConnectionPoolInstrumentation",
            "atatus.instrumentation.packages.asyncio.aioredis.RedisPipelineInstrumentation",
            "atatus.instrumentation.packages.asyncio.aioredis.RedisConnectionInstrumentation",
            "atatus.instrumentation.packages.asyncio.aiomysql.AioMySQLInstrumentation",
            "atatus.instrumentation.packages.asyncio.aiobotocore.AioBotocoreInstrumentation",
            "atatus.instrumentation.packages.asyncio.starlette.StarletteServerErrorMiddlewareInstrumentation",
            "atatus.instrumentation.packages.asyncio.redis_asyncio.RedisAsyncioInstrumentation",
            "atatus.instrumentation.packages.asyncio.redis_asyncio.RedisPipelineInstrumentation",
            "atatus.instrumentation.packages.asyncio.psycopg_async.AsyncPsycopgInstrumentation",
            "atatus.instrumentation.packages.grpc.GRPCAsyncServerInstrumentation",
        ]
    )

# These instrumentations should only be enabled if we're instrumenting via the
# wrapper script, which calls register_wrapper_instrumentations() below.
_wrapper_register = {
    "atatus.instrumentation.packages.flask.FlaskInstrumentation",
    "atatus.instrumentation.packages.django.DjangoAutoInstrumentation",
    "atatus.instrumentation.packages.starlette.StarletteInstrumentation",
}


def register(cls) -> None:
    _cls_register.add(cls)


def register_wrapper_instrumentations() -> None:
    _cls_register.update(_wrapper_register)


_instrumentation_singletons = {}


def get_instrumentation_objects():
    for cls_str in _cls_register:
        if cls_str not in _instrumentation_singletons:
            cls = import_string(cls_str)
            _instrumentation_singletons[cls_str] = cls()

        obj = _instrumentation_singletons[cls_str]
        yield obj
