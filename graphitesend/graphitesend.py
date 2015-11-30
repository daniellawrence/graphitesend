#!/usr/bin/env python

import logging
import os
import pickle
import socket
import struct
import time

VERSION = "0.4.0"
GRAPHITE_PICKLE_PORT = 2004
GRAPHITE_PLAINTEXT_PORT = 2003
GRAPHITE_SERVER = 'graphite'
SOCKET_TIMEOUT = 2
log = logging.getLogger(__name__)


class GraphiteSendException(Exception):
    pass


class DryrunSocket(object):
    def __init__(self):
        pass

    def sendall(self, *args, **kwargs):
        pass


class GraphiteClient(object):

    """
    Graphite Client that will setup a TCP connection to graphite.

    :param prefix: string added to the start of all metrics
    :type prefix: Default: "systems."
    :param graphite_server: hostname or ip address of graphite server
    :type graphite_server: Default: graphite
    :param graphite_port: TCP port we will connect to
    :type graphite_port: Default: 2003
    :param debug: Toggle debug messages
    :type debug: True or False
    :param group: string added to after system_name and before metric name
    :param system_name: FDQN of the system generating the metrics
    :type system_name: Default: current FDQN
    :param suffix: string added to the end of all metrics
    :param lowercase_metric_names: Toggle the .lower() of all metric names
    :param fqdn_squash: Change host.example.com to host_example_com
    :type fqdn_squash: True or False
    :param dryrun: Toggle if it will really send metrics or just return them
    :type dryrun: True or False
    :param timeout_in_seconds: Number of seconds before a connection is timed out.

    It will then send any metrics that you give it via
    the .send() or .send_dict().

    You can also take advantage of the prefix, group and system_name options
    that allow you to setup default locations where your whisper files will
    be kept.
    eg.
    ( where 'linuxserver' is the name of the localhost)

    .. code-block:: python

      >>> init().prefix
      systems.linuxserver.

      >>> init(system_name='remote_host').prefix
      systems.remote_host.

      >>> init(group='cpu').prefix
      systems.linuxserver.cpu.

      >>> init(prefix='apache').prefix
      apache.

    """
    _instance = None

    def __new__(klass, val):
        if GraphiteClient._instance is None:
            GraphiteClient._instance = object.__new__(klass)
        GraphiteClient._instance.val = val
        return GraphiteClient._instance

    def __init__(
            self,
            prefix='systems',
            suffix='',
            graphite_server=GRAPHITE_SERVER,
            graphite_port=GRAPHITE_PLAINTEXT_PORT,
            timeout_in_seconds=SOCKET_TIMEOUT,
            debug=False,
            group=None,
            system_name=os.uname()[1],
            lowercase_metric_names=False,
            connect_on_create=True,
            fqdn_squash=False,
            dryrun=False
    ):
        """
        setup the connection to the graphite server and work out the
        prefix.

        This allows for very simple syntax when sending messages to the
        graphite server.

        """

        self.addr = (graphite_server, graphite_port)

        # If this is a dry run, then we do not want to configure a connection
        # or try and make the connection once we create the object.
        if dryrun:
            self.socket = DryrunSocket()
        else:
            self.socket = socket.socket()

        self.metric_formatters = [self.clean_metric_name]
        if lowercase_metric_names:
            self.metric_formatters.append(self.lowercase_metric_names)

        def connect(self):
            "Make a TCP connection to the graphite server on port self.port"
            self.socket.settimeout(self.timeout_in_seconds)
            try:
                self.socket.connect(self.addr)
            except socket.timeout:
                raise GraphiteSendException(
                    "Took over %d second(s) to connect to %s" %
                    (self.timeout_in_seconds, self.addr))
            except socket.gaierror:
                raise GraphiteSendException(
                    "No address associated with hostname %s:%s" % self.addr)
            except Exception as error:
                raise GraphiteSendException(
                    "unknown exception while connecting to %s - %s" %
                    (self.addr, error)
                )
            return self.socket

    def format_metric_name(self, metric_name, prefix='', group='', suffix=''):
        if prefix:
            prefix = "{0}.".format(prefix)
        if group:
            group = "{0}.".format(group)
        return "{prefix}{group}{metric_name}{suffix}".format(**locals())

    def clean_metric_name(self, metric_name):
        """
        Make sure the metric is free of control chars, spaces, tabs, etc.
        """
        metric_name = metric_name.replace('(', '_').replace(')', '')
        metric_name = metric_name.replace(' ', '_').replace('-', '_')
        metric_name = metric_name.replace('/', '_').replace('\\', '_')
        metric_name = metric_name.replace('..', '.')
        return metric_name

    def disconnect(self):
        """
        Close the TCP connection with the graphite server.
        """
        try:
            self.socket.shutdown(1)

        # If its currently a socket, set it to None
        except AttributeError:
            self.socket = None
        except Exception:
            self.socket = None

        # Set the self.socket to None, no matter what.
        finally:
            self.socket = None

    def _send(self, message):
        """
        Given a message send it to the graphite server.
        """

        if not self.socket:
            raise GraphiteSendException("Socket was not created before send")

        try:
            self.socket.sendall(message)

        # Capture missing socket.
        except socket.gaierror as error:
            raise GraphiteSendException(
                "Failed to send data to %s, with error: %s" %
                (self.addr, error))

        # Capture socket closure before send.
        except socket.error as error:
            raise GraphiteSendException(
                "Socket closed before able to send data to %s, "
                "with error: %s" %
                (self.addr, error)
            )

        except Exception as error:
            raise GraphiteSendException(
                "Unknown error while trying to send data down socket to %s, "
                "error: %s" %
                (self.addr, error)
            )

        return "sent %d long message: %s" % \
            (len(message), "".join(message[:75]))

    def _presend(self, message):
        """
        Complete any message alteration tasks before sending to the graphite
        server.
        """
        # An option to lowercase the entire message
        if self.lowercase_metric_names:
            message = message.lower()
        return message

    def send(self, metric, value, timestamp=None):
        """
        Format a single metric/value pair, and send it to the graphite
        server.

        :param metric: name of the metric
        :type prefix: string
        :param value: value of the metric
        :type prefix: float or int
        :param timestmap: epoch time of the event
        :type prefix: float or int

        .. code-block:: python

          >>> g = init()
          >>> g.send("metric", 54)

        .. code-block:: python

          >>> g = init()
          >>> g.send(metric="metricname", value=73)

        """
        if timestamp is None:
            timestamp = int(time.time())
        else:
            timestamp = int(timestamp)

        if type(value).__name__ in ['str', 'unicode']:
            value = float(value)

        log.debug("metric: '%s'" % metric)
        metric = self.clean_metric_name(metric)
        log.debug("metric: '%s'" % metric)

        message = "%s%s%s %f %d\n" % (self.prefix, metric, self.suffix,
                                      value, timestamp)

        message = self. _presend(message)

        return self._send(message)

    def send_dict(self, data, timestamp=None):
        """
        Format a dict of metric/values pairs, and send them all to the
        graphite server.

        :param data: key,value pair of metric name and metric value
        :type prefix: dict
        :param timestmap: epoch time of the event
        :type prefix: float or int

        .. code-block:: python

          >>> g = init()
          >>> g.send_dict({'metric1': 54, 'metric2': 43, 'metricN': 999})

        """
        if timestamp is None:
            timestamp = int(time.time())
        else:
            timestamp = int(timestamp)

        metric_list = []

        for metric, value in data.items():
            if type(value).__name__ in ['str', 'unicode']:
                value = float(value)
            metric = self.clean_metric_name(metric)
            tmp_message = "%s%s%s %f %d\n" % (self.prefix, metric,
                                              self.suffix, value, timestamp)
            metric_list.append(tmp_message)

        message = "".join(metric_list)
        return self._send(message)

    def send_list(self, data, timestamp=None):
        """

        Format a list of set's of (metric, value) pairs, and send them all
        to the graphite server.

        :param data: list of key,value pairs of metric name and metric value
        :type prefix: list
        :param timestmap: epoch time of the event
        :type prefix: float or int

        .. code-block:: python

          >>> g = init()
          >>> g.send_list([('metric1', 54),('metric2', 43, 1384418995)])

        """
        if timestamp is None:
            timestamp = int(time.time())
        else:
            timestamp = int(timestamp)

        metric_list = []

        for metric_info in data:

            # Support [ (metric, value, timestamp), ... ] as well as
            # [ (metric, value), ... ].
            # If the metric_info provides a timestamp then use the timestamp.
            # If the metric_info fails to provide a timestamp, use the one
            # provided to send_list() or generated on the fly by time.time()
            if len(metric_info) == 3:
                (metric, value, metric_timestamp) = metric_info
            else:
                (metric, value) = metric_info
                metric_timestamp = timestamp

            if type(value).__name__ in ['str', 'unicode']:
                log.debug("metric='%(metric)s'  value='%(value)s'" % locals())
                value = float(value)

            metric = self.clean_metric_name(metric)

            tmp_message = "%s%s%s %f %d\n" % (self.prefix, metric,
                                              self.suffix, value,
                                              metric_timestamp)
            metric_list.append(tmp_message)

        message = "".join(metric_list)
        return self._send(message)


class GraphitePickleClient(GraphiteClient):

    def __init__(self, *args, **kwargs):
        # If the user has not given a graphite_port, then use the default pick
        # port.
        if 'graphite_port' not in kwargs:
            kwargs['graphite_port'] = default_graphite_pickle_port

        # TODO: Fix this hack and use super.
        # self = GraphiteClient(*args, **kwargs)  # noqa
        super(self.__class__, self).__init__(*args, **kwargs)

    def str2listtuple(self, string_message):
        "Covert a string that is ready to be sent to graphite into a tuple"

        if type(string_message).__name__ not in ('str', 'unicode'):
            raise TypeError("Must provide a string or unicode")

        if not string_message.endswith('\n'):
            string_message += "\n"

        tpl_list = []
        for line in string_message.split('\n'):
            line = line.strip()
            if not line:
                continue
            path, metric, timestamp = (None, None, None)
            try:
                (path, metric, timestamp) = line.split()
            except ValueError:
                raise ValueError(
                    "message must contain - metric_name, value and timestamp '%s'"
                    % line)
            try:
                timestamp = float(timestamp)
            except ValueError:
                raise ValueError("Timestamp must be float or int")

            tpl_list.append((path, (timestamp, metric)))

        if len(tpl_list) == 0:
            raise GraphiteSendException("No messages to send")

        payload = pickle.dumps(tpl_list)
        header = struct.pack("!L", len(payload))
        message = header + payload

        return message

    def _send(self, message):
        """ Given a message send it to the graphite server. """

        # An option to lowercase the entire message
        if self.lowercase_metric_names:
            message = message.lower()

        # convert the message into a pickled payload.
        message = self.str2listtuple(message)

        try:
            self.socket.sendall(message)

        # Capture missing socket.
        except socket.gaierror as error:
            raise GraphiteSendException(
                "Failed to send data to %s, with error: %s" %
                (self.addr, error))

        # Capture socket closure before send.
        except socket.error as error:
            raise GraphiteSendException(
                "Socket closed before able to send data to %s, "
                "with error: %s" %
                (self.addr, error))

        except Exception as error:
            raise GraphiteSendException(
                "Unknown error while trying to send data down socket to %s, "
                "error: %s" %
                (self.addr, error))

        return "sent %d long pickled message" % len(message)


def init(init_type='plaintext_tcp', *args, **kwargs):
    """
    Create the module instance of the GraphiteClient.
    """
    global _module_instance
    reset()

    validate_init_types = ['plaintext_tcp', 'plaintext', 'pickle_tcp',
                           'pickle', 'plain']

    if init_type not in validate_init_types:
        raise GraphiteSendException(
            "Invalid init_type '%s', must be one of: %s" %
            (init_type, ", ".join(validate_init_types)))

    # Use TCP to send data to the plain text receiver on the graphite server.
    if init_type in ['plaintext_tcp', 'plaintext', 'plain']:
        _module_instance = GraphiteClient(*args, **kwargs)

    # Use TCP to send pickled data to the pickle receiver on the graphite
    # server.
    if init_type in ['pickle_tcp', 'pickle']:
        _module_instance = GraphitePickleClient(*args, **kwargs)

    return _module_instance


def send(*args, **kwargs):
    """ Make sure that we have an instance of the GraphiteClient.
    Then send the metrics to the graphite server.
    User consumable method.
    """
    if not _module_instance:
        raise GraphiteSendException(
            "Must call graphitesend.init() before sending")

    _module_instance.send(*args, **kwargs)
    return _module_instance


def send_dict(*args, **kwargs):
    """ Make sure that we have an instance of the GraphiteClient.
    Then send the metrics to the graphite server.
    User consumable method.
    """
    if not _module_instance:
        raise GraphiteSendException(
            "Must call graphitesend.init() before sending")
    _module_instance.send_dict(*args, **kwargs)
    return _module_instance


def send_list(*args, **kwargs):
    """ Make sure that we have an instance of the GraphiteClient.
    Then send the metrics to the graphite server.
    User consumable method.
    """
    if not _module_instance:
        raise GraphiteSendException(
            "Must call graphitesend.init() before sending")
    _module_instance.send_list(*args, **kwargs)
    return _module_instance


def reset():
    """ disconnect from the graphite server and destroy the module instance.
    """
    global _module_instance
    if not _module_instance:
        return False
    _module_instance.disconnect()
    _module_instance = None


def cli():
    """ Allow the module to be called from the cli. """
    import argparse

    parser = argparse.ArgumentParser(description='Send data to graphite')

    # Core of the application is to accept a metric and a value.
    parser.add_argument('metric', metavar='metric', type=str,
                        help='name.of.metric')
    parser.add_argument('value', metavar='value', type=int,
                        help='value of metric as int')

    args = parser.parse_args()
    metric = args.metric
    value = args.value

    graphitesend_instance = init()
    graphitesend_instance.send(metric, value)

if __name__ == '__main__':  # pragma: no cover
    cli()
