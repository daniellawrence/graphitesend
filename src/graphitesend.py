#!/usr/bin/env python

import time
import socket
import os
_module_instance = None
__version__ = "0.0.1"


class GraphiteClient(object):
    """ Graphite Client that will setup a TCP connection to your graphite
    instance on port 2003. It will then send any metrics that you give it via
    the .send() or .send_dict().
    You can also take advantage of the prefix, group and system_name options
    that allow you to setup default locations where your whisper files will
    be kept.
    eg.
    ( where linuxserver is the name of the localhost)
    >>> init().prefix
    systems.linuxserver.
    >>> init(system_name='remote_host').prefix
    systems.thumper.
    >>> init(group='cpu').prefix
    systems.linuxserver.cpu.
    >>> init(prefix='apache').prefix
    apache.

    """
    def __init__(self, host="graphite", port=2003, prefix=None,
                 debug=False, group=None, system_name=None, suffix=None):
        """ setup the connection to the graphite server and work out the
        prefix.
        This allows for very simple syntax when sending messages to the
        graphite server. """
        self.addr = (host, port)
        self.socket = self.connect()
        self.debug = debug

        if system_name is None:
            system_name = os.uname()[1]

        if prefix is None:
            prefix = "systems.%(system_name)s" % locals()

        if group:
            prefix = prefix + "." + group

        if prefix:
            prefix = prefix + "."
       
        if suffix:
            self.suffix = suffix
        else:
            self.suffix = ""

        self.prefix = prefix

    def connect(self):
        """ Make a TCP connection to the graphite server on port self.port """
        local_socket = socket.socket()
        local_socket.settimeout(1)
        local_socket.connect(self.addr)
        return local_socket

    def clean_metric_name(metric_name):
        """ Make sure the metric is free of control chars, spaces, tabs, etc.
        TODO: Need to work out the best way to do the following:
        """
        metric_name = metric_name.replace('(','_').replace(')','')
        metric_name = metric_name.replace(' ','_').replace('-','_')
        return metric_name


    def disconnect(self):
        """ close the TCP connection. """
        self.socket.shutdown(1)

    def _send(self, message):
        """ Given a message send it to the graphite server. """
        self.socket.sendall(message)
        return "sent %d long message" % len(message)

    def send(self, metric, value, timestamp=None):
        """ Format a single metric/value pair, and send it to the graphite server.
        """
        if timestamp is None:
            timestamp = int(time.time())
        else:
            timestamp = int(timestamp)

        message = "%s%s%s %f %d\n" % (self.prefix, metric, self.suffix, value, timestamp)

        return self._send(message)

    def send_dict(self, data, timestamp=None):
        """ Format a dict of metric/values pairs, and send them all to the graphite
        server.
        """
        if timestamp is None:
            timestamp = int(time.time())
        else:
            timestamp = int(timestamp)

        metric_list = []

        for metric, value in data.items():
            tmp_message = "%s%s%s %f %d\n" % (self.prefix,  metric, self.suffix, value, timestamp)
            metric_list.append(tmp_message)

        message = "".join(metric_list)
        return self._send(message)


def init(*args, **kwargs):
    """ Create the module instance of the GraphiteClient. """
    global _module_instance
    reset()
    _module_instance = GraphiteClient(*args, **kwargs)
    return _module_instance


def send(*args, **kwargs):
    """ Make sure that we have an instance of the GraphiteClient.
    Then send the metrics to the graphite server.
    User consumable method.
    """
    if not _module_instance:
        raise Exception("Must call graphitesend.init() before sending")

    print args

    _module_instance.send(*args, **kwargs)
    return _module_instance


def send_dict(*args, **kwargs):
    """ Make sure that we have an instance of the GraphiteClient.
    Then send the metrics to the graphite server.
    User consumable method.
    """
    if not _module_instance:
        raise Exception("Must call graphitesend.init() before sending")
    _module_instance.send_dict(*args, **kwargs)
    return _module_instance


def reset():
    """ disconnect from the graphite server and destroy the module instance.
    """
    global _module_instance
    if not _module_instance:
        return False
    _module_instance.disconnect()
    _module_instance = None
