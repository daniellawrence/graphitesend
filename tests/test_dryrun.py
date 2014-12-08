#!/usr/bin/env python

import unittest
from graphitesend import graphitesend
import os
import socket


class TestDryRun(unittest.TestCase):
    """ Tests to make sure that a dryrun is just that. """

    def setUp(self):
        """ reset graphitesend """
        # Drop any connections or modules that have been setup from other tests
        graphitesend.reset()
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

    def test_EmptyAddr(self):
        g = graphitesend.init(prefix='', dryrun=True)
        self.assertEqual(g.addr, None)

    def test_CreateGraphiteClient(self):
        g = graphitesend.init(prefix='', dryrun=True)
        self.assertEqual(type(g).__name__, 'GraphiteClient')
        dryrun_message = g.send('metric', 1, 1)
        self.assertEqual(dryrun_message,
                         "%s.metric 1.000000 1\n" % self.hostname)

    def test_DryrunConnectFailure(self):
        g = graphitesend.init(prefix='', dryrun=True)
        self.assertEqual(type(g).__name__, 'GraphiteClient')
        with self.assertRaises(graphitesend.GraphiteSendException):
            g.connect()

    def test_BadGraphtieServer(self):
        graphitesend.default_graphite_server = "BADGRAPHITESERVER"
        g = graphitesend.init(prefix='', dryrun=True)
        self.assertEqual(type(g).__name__, 'GraphiteClient')
        dryrun_message = g.send('metric', 1, 1)
        self.assertEqual(dryrun_message,
                         "%s.metric 1.000000 1\n" % self.hostname)
