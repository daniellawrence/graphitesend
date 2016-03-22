#!/usr/bin/env python

from graphitesend import graphitesend
import unittest2 as unittest
import socket


class TestAutoreconnect(unittest.TestCase):

    def setUp(self):
        """ reset graphitesend """
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

    def test_set_autoreconnect_default(self):
        g = graphitesend.init(dryrun=True)
        self.assertEqual(g._autoreconnect, False)

    def test_set_autoreconnect_true(self):
        g = graphitesend.init(dryrun=True, autoreconnect=True)
        self.assertEqual(g._autoreconnect, True)

    def test_set_autoreconnect_false(self):
        g = graphitesend.init(dryrun=True, autoreconnect=False)
        self.assertEqual(g._autoreconnect, False)

    def test_autoreconnect(self):
        g = graphitesend.GraphiteClient(autoreconnect=True)
        g.send("metric", 42)
        self.tearDown()
        with self.assertRaises(graphitesend.GraphiteSendException):
            g.send("metric", 2)
        self.setUp()
        g.send("metric", 3)
