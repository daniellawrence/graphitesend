#!/usr/bin/env python

import unittest
import graphitesend


class TestAll(unittest.TestCase):
    """ Basic tests ( better than nothing ) """


    def setUp(self):
        """ reset graphitesend """
        # Drop any connections or modules that have been setup from other tests
        graphitesend.reset()
        # Monkeypatch the graphitesend so that it points at a graphite service
        # running on one of my (dannyla@linux.com) systems.
        graphitesend.default_graphite_server = 'graphite.dansysadm.com'

    def tearDown(self):
        """ reset graphitesend """
        # Drop any connections or modules that have been setup from other tests
        graphitesend.reset()

    def test_connect_exception_on_badhost(self):
        """ TCP only. """
        graphitesend.default_graphite_server = 'missinggraphiteserver.example.com'
        with self.assertRaises(graphitesend.GraphiteSendException):
            graphite_instance = graphitesend.init()

    def test_create_graphitesend_instance(self):
        g = graphitesend.init()
        expected_type = type(graphitesend.GraphiteSendUDP())
        g_type = type(g)
        self.assertEqual(g_type, expected_type)

    def test_monkey_patch_of_graphitehost(self):
        g = graphitesend.init()
        custom_prefix = g.addr[0]
        self.assertEqual(custom_prefix, 'graphite.dansysadm.com') 

    def test_prefix(self):
        g = graphitesend.init(prefix='custom_prefix')
        custom_prefix = g.prefix
        self.assertEqual(custom_prefix, 'custom_prefix.') 

    def test_prefix_double_dot(self):
        g = graphitesend.init(prefix='custom_prefix.')
        custom_prefix = g.prefix
        self.assertEqual(custom_prefix, 'custom_prefix.') 

    def test_prefix_remove_spaces(self):
        g = graphitesend.init(prefix='custom prefix')
        custom_prefix = g.prefix
        self.assertEqual(custom_prefix, 'custom_prefix.') 

    def test_set_suffix(self):
        g = graphitesend.init(suffix='custom_suffix')
        custom_suffix = g.suffix
        self.assertEqual(custom_suffix, 'custom_suffix') 

    def test_set_group_prefix(self):
        g = graphitesend.init(group='custom_group')
        import os
        hostname = os.uname()[1]
        expected_prefix = "systems.%(hostname)s.custom_group." % locals()
        custom_prefix = g.prefix
        self.assertEqual(custom_prefix, expected_prefix)

    def test_default_prefix(self):
        g = graphitesend.init()
        import os
        hostname = os.uname()[1]
        expected_prefix = "systems.%(hostname)s." % locals()
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
        """ TCP only """
        graphite_instance = graphitesend.init()
        graphite_instance.disconnect()
        with self.assertRaises(graphitesend.GraphiteSendException):
            graphite_instance.send('metric', 0)

    def test_force_unknown_failure_on_send(self):
        """ TCP only """
        graphite_instance = graphitesend.init()
        graphite_instance.socket = None
        with self.assertRaises(graphitesend.GraphiteSendException):
            graphite_instance.send('metric', 0)
        
if __name__ == '__main__':
    unittest.main()
    
