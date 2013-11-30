#!/usr/bin/env python

import unittest
import graphitesend
import os


class TestDryRun(unittest.TestCase):
    """ Tests to make sure that a dryrun is just that. """

    def setUp(self):
        """ reset graphitesend """
        # Drop any connections or modules that have been setup from other tests
        graphitesend.reset()
        graphitesend.default_graphite_server = 'localhost'
        self.hostname = os.uname()[1]

    def testEmptyAddr(self):
        g = graphitesend.init(prefix='', dryrun=True)
        self.assertEqual(g.addr, None)

    def testCreateGraphiteClient(self):
        g = graphitesend.init(prefix='', dryrun=True)
        self.assertEqual(type(g).__name__, 'GraphiteClient')
        dryrun_message = g.send('metric', 1, 1)
        self.assertEqual(dryrun_message, "%s.metric 1.000000 1\n" % self.hostname)

    def testDryrunConnectFailure(self):
        g = graphitesend.init(prefix='', dryrun=True)
        self.assertEqual(type(g).__name__, 'GraphiteClient')
        with self.assertRaises(graphitesend.GraphiteSendException):
            g.connect()

    def testBadGraphtieServer(self):
        graphitesend.default_graphite_server = "BADGRAPHITESERVER"
        g = graphitesend.init(prefix='', dryrun=True)
        self.assertEqual(type(g).__name__, 'GraphiteClient')
        dryrun_message = g.send('metric', 1, 1)
        self.assertEqual(dryrun_message, "%s.metric 1.000000 1\n" % self.hostname)
