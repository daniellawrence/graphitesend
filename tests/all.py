#!/usr/bin/env python

import unittest
import graphitesend


class TestAll(unittest.TestCase):
    """ Basic tests ( better than nothing ) """


    def setUp(self):
        """ reset graphitesend """
        graphitesend.reset()

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
    
