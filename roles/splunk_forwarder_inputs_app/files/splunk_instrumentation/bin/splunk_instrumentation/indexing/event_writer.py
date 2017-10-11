import json
import logging

from splunk_instrumentation.splunkd import Splunkd
from splunk_instrumentation.constants import SPLUNKRC
from splunk_instrumentation.datetime_util import json_serial
from splunk_instrumentation.constants import INSTRUMENTATION_SOURCETYPE


class EventWriter(object):
    """ Event Writer class
    This class handles writing to the index.
    It grabs a splunkd object according to the splunkrc params provided:
        - If splunkrc is a dictionary, it will create a new splunkd object.
        - If given other object type, it will do do Dependency Injection on _splunkd

    """
    def __init__(self, splunkrc=None, index_name=None):
        self.splunkrc = splunkrc or SPLUNKRC
        self.socket = None
        self._index = None

        if type(self.splunkrc) is dict:
            self._splunkd = Splunkd(**self.splunkrc)
        else:
            self._splunkd = splunkrc

        if index_name:
            if self._splunkd.has_index(index_name):
                self._index = self._splunkd.get_index(index_name)
            else:
                logging.error('ERROR: INDEX IS NOT AVAILABLE')
                raise(Exception("ERROR INDEX UNAVAILABLE"))

    def submit(self, event, host=None, source=None, sourcetype=None):
        """Submit a new event directly to the index."""
        if self._index:
            self._index.submit(
                event, host=host, source=source, sourcetype=sourcetype)
        else:
            logging.error('ERROR: INDEX IS NOT AVAILABLE')
            raise Exception("ERROR INDEX UNAVAILABLE")

    def open_socket(self, host=None, source=None, sourcetype=None):
        '''
        Opens a socket to stream events to be indexed
        :param host:
        :param source:
        :return:
        '''
        self.socket = self._index.attach(host=host, source=source, sourcetype=INSTRUMENTATION_SOURCETYPE)
        return self.socket

    def close_socket(self):
        '''
        Closes socket and set it to none
        '''
        if self.socket:
            self.socket.close()
        self.socket = None

    def submit_via_socket(self, event):
        """
        Submit the event provided using socket connection.
        """
        if not isinstance(event, str):
            event = json.dumps(event, default=json_serial)
        if not self.socket:
            self.open_socket()
        self.socket.send(event)
