import logging
import platform
import time

log = logging.getLogger("graphitesend")


class GraphiteStructuredFormatter(object):
    '''Default formatter for GraphiteClient.

    Provides structured metric naming based on a prefix, system name, group, etc

    :param prefix: string added to the start of all metrics
    :type prefix: Default: "systems."
    :param group: string added to after system_name and before metric name
    :param system_name: FDQN of the system generating the metrics
    :type system_name: Default: current FDQN
    :param suffix: string added to the end of all metrics
    :param lowercase_metric_names: Toggle the .lower() of all metric names
    :param fqdn_squash: Change host.example.com to host_example_com
    :type fqdn_squash: True or False
    :param clean_metric_name: Does GraphiteClient needs to clean metric's name
    :type clean_metric_name: True or False

    Feel free to implement your own formatter as any callable that accepts
    def __call__(metric_name, metric_value, timestamp)

    and emits text appropriate to send to graphite's text socket.
    '''

    cleaning_replacement_list = [
        ('(', '_'),
        (')', ''),
        (' ', '_'),
        ('-', '_'),
        ('/', '_'),
        ('\\', '_')
    ]

    def __init__(self, prefix=None, group=None, system_name=None, suffix=None,
                 lowercase_metric_names=False, fqdn_squash=False, clean_metric_name=True):

        prefix_parts = []

        if prefix != '':
            prefix = prefix or "systems"
            prefix_parts.append(prefix)

        if system_name != '':
            system_name = system_name or platform.uname()[1]
            if fqdn_squash:
                system_name = system_name.replace('.', '_')
            prefix_parts.append(system_name)

        if group is not None:
            prefix_parts.append(group)

        prefix = '.'.join(prefix_parts)
        prefix = prefix.replace('..', '.')  # remove double dots
        prefix = prefix.replace(' ', '_')  # Replace ' 'spaces with _
        if prefix:
            prefix += '.'
        self.prefix = prefix

        self.suffix = suffix or ""
        self.lowercase_metric_names = lowercase_metric_names
        self._clean_metric_name = clean_metric_name

    def clean_metric_name(self, metric_name):
        """
        Make sure the metric is free of control chars, spaces, tabs, etc.
        """
        if not self._clean_metric_name:
            return metric_name
        for _from, _to in self.cleaning_replacement_list:
            metric_name = metric_name.replace(_from, _to)
        return metric_name

    '''Format a metric, value, and timestamp for use on the carbon text socket.'''
    def __call__(self, metric_name, metric_value, timestamp=None):
        if timestamp is None:
            timestamp = time.time()
        timestamp = int(timestamp)

        if type(metric_value).__name__ in ['str', 'unicode']:
            metric_value = float(metric_value)

        log.debug("metric: '{}'".format(metric_name))
        metric_name = self.clean_metric_name(metric_name)
        log.debug("metric: '{}'".format(metric_name))

        message = "{}{}{} {} {}\n".format(self.prefix, metric_name,
                                          self.suffix, metric_value, timestamp)

        # An option to lowercase the entire message
        if self.lowercase_metric_names:
            message = message.lower()

        return message
