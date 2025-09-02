class Layer(object):
    kinds_dict = {
        'db': 'Database',
        'cache': 'Database',
        'external': 'Remote',
        'aws': 'Remote',
        'websocket': 'Remote',
        'template': 'Template',
        'compression': 'Compression',
        'code.custom': 'Custom'
    }

    types_dict = {
        'mysql': 'MySQL',
        'mysql2': 'MySQL',
        'postgresql': 'Postgres',
        'mssql': 'MS SQL',
        'mongodb': 'MongoDB',
        'memcached': 'Memcached',
        'redis': 'Redis',
        'graphql': 'GraphQL',
        'elasticsearch': 'Elasticsearch',
        'cassandra': 'Cassandra',
        'sqlite': 'SQLite',
        'http': 'External Requests',
        'django': 'Django',
        'jinja2': 'Jinja 2',
        'zlib': 'zlib'
    }

    def __init__(self, type, kind, duration):
        self.type = type
        self.kind = kind
        self.count = 1
        self.min = duration
        self.max = duration
        self.total = duration

    def aggregate(self, duration):
        self.count += 1
        if duration < self.min:
            self.min = duration
        if duration > self.max:
            self.max = duration
        self.total += duration
