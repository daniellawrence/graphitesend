#!/usr/bin/env python

from graphitesend import graphitesend
import unittest2 as unittest
import socket
import os


class TestAll(unittest.TestCase):
    """ Basic tests ( better than nothing ) """

    def setUp(self):
        """ reset graphitesend """
        # Drop any connections or modules that have been setup from other tests
        graphitesend.reset()
        # Monkeypatch the graphitesend so that it points at a graphite service
        # running on one of my (dannyla@linux.com) systems.
        # graphitesend.default_graphite_server = 'graphite.dansysadm.com'
        graphitesend.default_graphite_server = 'localhost'
        self.hostname = os.uname()[1]
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind(('localhost', 2003))
        self.server.listen(5)

    def tearDown(self):
        """ reset graphitesend """
        # Drop any connections or modules that have been setup from other tests
        graphitesend.reset()
        try:
            self.server.shutdown(socket.SHUT_RD)
            self.server.close()
        except Exception:
            pass
        self.server = None

    def test_connect_exception_on_badhost(self):
        bad_graphite_server = 'missinggraphiteserver.example.com'
        graphitesend.default_graphite_server = bad_graphite_server
        with self.assertRaises(graphitesend.GraphiteSendException):
            graphitesend.init()

    def test_set_lowercase_metric_names(self):
        g = graphitesend.init(lowercase_metric_names=True)
        self.assertEqual(g.lowercase_metric_names, True)

    def test_lowercase_metric_names(self):
        g = graphitesend.init(lowercase_metric_names=True)
        send_data = g.send('METRIC', 1)
        self.assertEqual('metric' in send_data, True)
        self.assertEqual('METRIC' in send_data, False)

    def test_create_graphitesend_instance(self):
        g = graphitesend.init()
        expected_type = type(graphitesend.GraphiteClient())
        g_type = type(g)
        self.assertEqual(g_type, expected_type)

    def test_monkey_patch_of_graphitehost(self):
        g = graphitesend.init()
        custom_prefix = g.addr[0]
        self.assertEqual(custom_prefix, 'localhost')

    def test_fqdn_squash(self):
        g = graphitesend.init(fqdn_squash=True)
        custom_prefix = g.prefix
        expected_results = 'systems.%s.' % self.hostname.replace('.', '_')
        self.assertEqual(custom_prefix, expected_results)

    def test_fqdn_squash_socket(self):
        uname_backup = os.uname
        g = graphitesend.init(fqdn_squash=True)
        custom_prefix = g.prefix
        expected_results = 'systems.%s.' % self.hostname.replace('.', '_')
        self.assertEqual(custom_prefix, expected_results)
        os.uname = uname_backup

    def test_noprefix(self):
        g = graphitesend.init()
        custom_prefix = g.prefix
        self.assertEqual(custom_prefix, 'systems.%s.' % self.hostname)

    def test_system_name(self):
        g = graphitesend.init(system_name='remote_host')
        custom_prefix = g.prefix
        expected_prefix = 'systems.remote_host.'
        self.assertEqual(custom_prefix, expected_prefix)

    def test_empty_system_name(self):
        g = graphitesend.init(system_name='')
        custom_prefix = g.prefix
        expected_prefix = 'systems.'
        self.assertEqual(custom_prefix, expected_prefix)

    def test_no_system_name(self):
        g = graphitesend.init(group='foo')
        custom_prefix = g.prefix
        expected_prefix = 'systems.%s.foo.' % self.hostname
        self.assertEqual(custom_prefix, expected_prefix)

    def test_prefix(self):
        g = graphitesend.init(prefix='custom_prefix')
        custom_prefix = g.prefix
        self.assertEqual(custom_prefix, 'custom_prefix.%s.' % self.hostname)

    def test_prefix_double_dot(self):
        g = graphitesend.init(prefix='custom_prefix.')
        custom_prefix = g.prefix
        self.assertEqual(custom_prefix, 'custom_prefix.%s.' % self.hostname)

    def test_prefix_remove_spaces(self):
        g = graphitesend.init(prefix='custom prefix')
        custom_prefix = g.prefix
        self.assertEqual(custom_prefix, 'custom_prefix.%s.' % self.hostname)

    def test_set_prefix_group(self):
        g = graphitesend.init(prefix='prefix', group='group')
        custom_prefix = g.prefix
        expected_prefix = 'prefix.%s.group.' % self.hostname
        self.assertEqual(custom_prefix, expected_prefix)

    def test_set_prefix_group_system(self):
        g = graphitesend.init(prefix='prefix', system_name='system',
                              group='group')
        custom_prefix = g.prefix
        expected_prefix = 'prefix.system.group.'
        self.assertEqual(custom_prefix, expected_prefix)

    def test_set_suffix(self):
        g = graphitesend.init(suffix='custom_suffix')
        custom_suffix = g.suffix
        self.assertEqual(custom_suffix, 'custom_suffix')

    def test_set_group_prefix(self):
        g = graphitesend.init(group='custom_group')
        expected_prefix = "systems.%s.custom_group." % self.hostname
        custom_prefix = g.prefix
        self.assertEqual(custom_prefix, expected_prefix)

    def test_default_prefix(self):
        g = graphitesend.init()
        expected_prefix = "systems.%s." % self.hostname
        custom_prefix = g.prefix
        self.assertEqual(custom_prefix, expected_prefix)

    def test_leave_suffix(self):
        g = graphitesend.init()
        default_suffix = g.suffix
        self.assertEqual(default_suffix, '')

    def test_clean_metric(self):
        g = graphitesend.init()
        #
        metric_name = g.clean_metric_name('test(name)')
        self.assertEqual(metric_name, 'test_name')
        #
        metric_name = g.clean_metric_name('test name')
        self.assertEqual(metric_name, 'test_name')
        #
        metric_name = g.clean_metric_name('test  name')
        self.assertEqual(metric_name, 'test__name')

    def test_reset(self):
        graphitesend.init()
        graphitesend.reset()
        graphite_instance = graphitesend._module_instance
        self.assertEqual(graphite_instance, None)

    def test_force_failure_on_send(self):
        graphite_instance = graphitesend.init()
        graphite_instance.disconnect()
        with self.assertRaises(graphitesend.GraphiteSendException):
            graphite_instance.send('metric', 0)

    def test_force_unknown_failure_on_send(self):
        graphite_instance = graphitesend.init()
        graphite_instance.socket = None
        with self.assertRaises(graphitesend.GraphiteSendException):
            graphite_instance.send('metric', 0)

    def test_send_list_metric_value(self):
        graphite_instance = graphitesend.init(prefix='test', system_name='local')
        response = graphite_instance.send_list([('metric', 1)])
        self.assertEqual('long message: test.local.metric 1' in response, True)
        self.assertEqual('1.00000' in response, True)

    def test_send_list_metric_value_single_timestamp(self):
        # Make sure it can handle custom timestamp
        graphite_instance = graphitesend.init(prefix='test')
        response = graphite_instance.send_list([('metric', 1)], timestamp=1)
        # self.assertEqual('sent 23 long message: test.metric' in response,
        # True)
        self.assertEqual('1.00000' in response, True)
        self.assertEqual(response.endswith('1\n'), True)

    def test_send_list_metric_value_timestamp(self):
        graphite_instance = graphitesend.init(prefix='test')

        # Make sure it can handle custom timestamp
        response = graphite_instance.send_list([('metric', 1, 1)])
        # self.assertEqual('sent 23 long message: test.metric' in response,
        # True)
        self.assertEqual('1.00000' in response, True)
        self.assertEqual(response.endswith('1\n'), True)

    def test_send_list_metric_value_timestamp_2(self):
        graphite_instance = graphitesend.init(prefix='test', system_name='')
        # Make sure it can handle custom timestamp
        response = graphite_instance.send_list(
            [('metric', 1, 1), ('metric', 1, 2)])
        # self.assertEqual('sent 46 long message:' in response, True)
        self.assertEqual('test.metric 1.000000 1' in response, True)
        self.assertEqual('test.metric 1.000000 2' in response, True)

    def test_send_list_metric_value_timestamp_3(self):
        graphite_instance = graphitesend.init(prefix='test', system_name='')
        # Make sure it can handle custom timestamp, fill in the missing with
        # the current time.
        response = graphite_instance.send_list(
            [
                ('metric', 1, 1),
                ('metric', 2),
            ]
        )

        # self.assertEqual('sent 46 long message:' in response, True)
        self.assertEqual('test.metric 1.000000 1' in response, True)
        self.assertEqual('test.metric 2.000000 2' not in response, True)

    def test_send_list_metric_value_timestamp_default(self):
        graphite_instance = graphitesend.init(prefix='test', system_name='bar')
        # Make sure it can handle custom timestamp, fill in the missing with
        # the current time.
        response = graphite_instance.send_list(
            [
                ('metric', 1, 1),
                ('metric', 2),
            ],
            timestamp='4'
        )
        # self.assertEqual('sent 69 long message:' in response, True)
        self.assertEqual('test.bar.metric 1.000000 1' in response, True)
        self.assertEqual('test.bar.metric 2.000000 4' in response, True)

    def test_send_list_metric_value_timestamp_default_2(self):
        graphite_instance = graphitesend.init(prefix='test', system_name='foo')
        # Make sure it can handle custom timestamp, fill in the missing with
        # the current time.
        (c, addr) = self.server.accept()
        response = graphite_instance.send_list(
            [
                ('metric', 1),
                ('metric', 2, 2),
            ],
            timestamp='4'
        )
        # self.assertEqual('sent 69 long message:' in response, True)
        self.assertEqual('test.foo.metric 1.000000 4' in response, True)
        self.assertEqual('test.foo.metric 2.000000 2' in response, True)
        sent_on_socket = c.recv(69)
        self.assertEqual('test.foo.metric 1.000000 4' in sent_on_socket, True)
        self.assertEqual('test.foo.metric 2.000000 2' in sent_on_socket, True)
        # self.server.shutdown(socket.SHUT_RD)
        # self.server.close()

    def test_send_value_as_string(self):
        # Make sure it can handle custom timestamp
        graphite_instance = graphitesend.init(prefix='')
        response = graphite_instance.send("metric", "1", "1")
        self.assertEqual('1.00000' in response, True)
        print response
        self.assertEqual(response.endswith('1\n'), True)


if __name__ == '__main__':
    unittest.main()
