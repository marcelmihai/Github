from splunk_instrumentation.indexing.instrumentation_index import InstrumentationIndex
from splunk_instrumentation.metrics.metrics_collection_manager import MetricsCollectionManager
from splunk_instrumentation.packager import Packager
import time
from splunk_instrumentation.report import report


class EventIndexer(object):
    '''
    a mock list to send events to be indexed through a socket
    '''
    def __init__(self):
        self.indexer = InstrumentationIndex()
        self._count = 0

    def append(self, item):
        '''
        on append send the event to the index through open socket
        :param item:
        :return:
        '''
        self._count = self._count + 1
        self.indexer.pipe_json(item)

    def close_connection(self):
        self.indexer.close_connection()

    def count(self):
        return self._count


class ScheduleManager(object):
    '''
    manager for application.

    '''
    def __init__(self, schema, factory):
        self.schema = schema
        self.factory = factory
        self.event_indexer = None

    def collect(self, dateRange):
        '''
        collects events based on schema and indexes through EventIndexer
        :return:
        '''
        self.event_indexer = EventIndexer()
        self._run_collection(dateRange, self.append_via_socket)
        report.report("events_indexed", self.event_indexer.count())
        time.sleep(2)

    def send(self, dateRange=None):
        '''
        sends events to splunkX
        :return:
        '''
        p = Packager(schema=self.schema, factory=self.factory)
        p.package_send(dateRange)

    def _run_collection(self, dateRange, callback=None):
        mcm = MetricsCollectionManager(self.schema, self.factory)
        mcm.collect_data(dateRange, False, callback)

    def append_via_socket(self, results):
        '''
        callback to process the event:
            - sending the data to event_indexer (via socket)
        '''
        for event in results:
            self.event_indexer.append(event)
        self.event_indexer.close_connection()
