#!/usr/bin/env python

from graphitesend import graphitesend
import unittest


class TestAsync(unittest.TestCase):
    """ Basic tests ( better than nothing ) """

    def setUp(self):
        """ reset graphitesend """
        self.server = None

    def test_set_async_default(self):
        g = graphitesend.init(dryrun=True)
        self.assertEqual(g.asynchronous, False)

    def test_set_async_true(self):
        g = graphitesend.init(dryrun=True, asynchronous=True)
        self.assertEqual(g.asynchronous, True)

    def test_set_async_false(self):
        g = graphitesend.init(dryrun=True, asynchronous=False)
        self.assertEqual(g.asynchronous, False)
