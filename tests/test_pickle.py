#!/usr/bin/env python

import unittest
import graphitesend


class TestPickle(unittest.TestCase):
    """ Basic tests ( better than nothing ) """

    def setUp(self):
        """ reset graphitesend """
        # Drop any connections or modules that have been setup from other tests
        graphitesend.reset()

    def testCreateGraphiteClient(self):
        g = graphitesend.GraphitePickleClient(connect_on_create=False)
        self.assertEqual(type(g).__name__, 'GraphitePickleClient')

    def test_default_port(self):
        graphitesend.GraphitePickleClient(connect_on_create=False)
        #self.assertEqual(g.addr, ('graphite', 2004))

    def test_str2listtuple(self):
        g = graphitesend.GraphitePickleClient(connect_on_create=False)

        # must have args
        with self.assertRaises(TypeError):
            g.str2listtuple()

        with self.assertRaises(TypeError):
            g.str2listtuple([])

        with self.assertRaises(ValueError):
            g.str2listtuple("x")

        with self.assertRaises(ValueError):
            g.str2listtuple("")

        with self.assertRaises(ValueError):
            g.str2listtuple("x x")

        with self.assertRaises(ValueError):
            g.str2listtuple("x x x")

        g.str2listtuple("x 1 1")


if __name__ == '__main__':
    unittest.main()
