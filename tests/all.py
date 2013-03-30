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
        graphitesend.graphite_server = 'graphite.dansysadm.com'

    def test_create_graphitesend_instance(self):
        g = graphitesend.init()
        expected_type = type(graphitesend.GraphiteClient())
        g_type = type(g)
        self.assertEqual(g_type, expected_type)

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

if __name__ == '__main__':
    unittest.main()
    
