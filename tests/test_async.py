#!/usr/bin/env python

from graphitesend import graphitesend
import unittest2 as unittest
import socket


class TestAsync(unittest.TestCase):
    """ Basic tests ( better than nothing ) """

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

    def test_set_async_default(self):
        g = graphitesend.init(dryrun=True)
        self.assertEqual(g.asynchronous, False)

    def test_set_async_true(self):
        g = graphitesend.init(dryrun=True, asynchronous=True)
        self.assertEqual(g.asynchronous, True)

    def test_set_async_false(self):
        g = graphitesend.init(dryrun=True, asynchronous=False)
        self.assertEqual(g.asynchronous, False)

    def test_send_reconnect_send_again(self):
        g = graphitesend.init(prefix='', system_name='', asynchronous=True)
        g.send('test_send', 50)
        (c, addr) = self.server.accept()
        sent_on_socket = c.recv(69)
        self.assertTrue(sent_on_socket.startswith('test_send 50.000000'))
