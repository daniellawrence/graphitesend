import unittest
from graphitesend import graphitesend
import os
import socket


class TestCli(unittest.TestCase):
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

        self.pserver = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.pserver.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.pserver.bind(('localhost', 2004))
        self.pserver.listen(5)

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

        try:
            self.pserver.shutdown(socket.SHUT_RD)
            self.pserver.close()
        except Exception:
            pass
        self.pserver = None

    def test_cli(self):
        with self.assertRaises(SystemExit):
            graphitesend.cli()
        import sys
        sys.argv = ['graphitesend_cli_test', 'test_cli_metric', '50']
        graphitesend.cli()
        (c, addr) = self.server.accept()
        sent_on_socket = c.recv(1024)
        self.assertIn('test_cli_metric 50.000000', sent_on_socket)

    def test_send_list(self):
        with self.assertRaises(graphitesend.GraphiteSendException):
            graphitesend.send_list([('test_metric', 50), ])

        graphitesend.init(system_name='')
        graphitesend.send_list([('test_send_list', 50), ])
        (c, addr) = self.server.accept()
        sent_on_socket = c.recv(69)
        self.assertIn('test_send_list 50.000000', sent_on_socket)

    def test_send_dict(self):
        with self.assertRaises(graphitesend.GraphiteSendException):
            graphitesend.send_dict({'test_metric': 50})

        graphitesend.init(system_name='')
        graphitesend.send_dict({'test_send_dict': 50})
        (c, addr) = self.server.accept()
        sent_on_socket = c.recv(69)
        self.assertIn('test_send_dict 50.000000', sent_on_socket)

    def test_send_dict_with_timestamp(self):
        graphitesend.init(system_name='')
        graphitesend.send_dict({'test_send_dict': 50}, 1)
        (c, addr) = self.server.accept()
        sent_on_socket = c.recv(69)
        self.assertIn('test_send_dict 50.000000 1\n', sent_on_socket)

    def test_send(self):
        with self.assertRaises(graphitesend.GraphiteSendException):
            graphitesend.send('test_metric', 50)

        graphitesend.init(system_name='')
        graphitesend.send('test_send', 50)
        (c, addr) = self.server.accept()
        sent_on_socket = c.recv(69)
        self.assertIn('test_send 50.000000', sent_on_socket)

    def test_init_as_pickel(self):
        g = graphitesend.init()
        self.assertEqual(type(g), type(graphitesend.GraphiteClient()))

        for init_type in ['plaintext_tcp', 'plaintext', 'plain']:
            g = graphitesend.init(init_type=init_type, dryrun=True)
            self.assertEqual(type(g), type(graphitesend.GraphiteClient()))

        for init_type in ['pickle', 'pickle_tcp']:
            g = graphitesend.init(init_type=init_type, dryrun=True)
            self.assertEqual(type(g),
                             type(graphitesend.GraphitePickleClient()))

    def test_init_bad_type(self):
        with self.assertRaises(graphitesend.GraphiteSendException):
            graphitesend.init(init_type="bad_type", dryrun=True)

    def test_socket_timeout(self):
        with self.assertRaises(graphitesend.GraphiteSendException):
            graphitesend.init(timeout_in_seconds=.0000000000001)

    def test_send_prefix_empty(self):
        graphitesend.init(prefix='', system_name='')
        graphitesend.send('test_send', 50)
        (c, addr) = self.server.accept()
        sent_on_socket = c.recv(69)
        self.assertTrue(sent_on_socket.startswith('test_send 50.000000'))

    def test_send_reconnect_send_again(self):
        g = graphitesend.init(prefix='', system_name='')
        g.send('test_send', 50)
        (c, addr) = self.server.accept()
        sent_on_socket = c.recv(69)
        self.assertTrue(sent_on_socket.startswith('test_send 50.000000'))
        g.reconnect()
        g.send('test_send', 50)
        (c, addr) = self.server.accept()
        sent_on_socket = c.recv(69)
        self.assertTrue(sent_on_socket.startswith('test_send 50.000000'))

    def test_dryrun(self):
        g = graphitesend.init(dryrun=True)
        dryrun_messsage_send = 'testing dryrun'
        dryrun_messsage_recv = g._dispatch_send(dryrun_messsage_send)
        self.assertEqual(dryrun_messsage_recv, dryrun_messsage_send)

    def test_send_gaierror(self):
        g = graphitesend.init()
        g.socket = True
        with self.assertRaises(graphitesend.GraphiteSendException):
            g._dispatch_send('test')

    def test_str2listtuple_bad(self):
        g = graphitesend.init(init_type='pickle')
        with self.assertRaises(TypeError):
            g.str2listtuple(54)
        with self.assertRaises(TypeError):
            g.str2listtuple([])
        with self.assertRaises(TypeError):
            g.str2listtuple({})
        with self.assertRaises(ValueError):
            g.str2listtuple("metric")

        with self.assertRaises(ValueError):
            g.str2listtuple("metric value timestamp extra")

    def test_str2listtuple_good(self):
        g = graphitesend.init(init_type='pickle')
        pickle_response = g.str2listtuple("path metric 1")
        self.assertEqual(
            pickle_response,
            "\x00\x00\x00.(lp0\n(S'path'\np1\n" +
            "(F1.0\nS'metric'\np2\ntp3\ntp4\na."
        )

    def test_send_list_str_to_int(self):
        graphitesend.init(system_name='')
        graphitesend.send_list([('test_send_list', '50'), ])
        (c, addr) = self.server.accept()
        sent_on_socket = c.recv(69)
        self.assertIn('test_send_list 50.000000', sent_on_socket)

    def test_send_dict_str_to_int(self):
        graphitesend.init(system_name='')
        graphitesend.send_dict({'test_send_dict': '50'})
        (c, addr) = self.server.accept()
        sent_on_socket = c.recv(69)
        self.assertIn('test_send_dict 50.000000', sent_on_socket)

    def test_pickle_send(self):
        g = graphitesend.init(init_type='pickle', system_name='', prefix='')
        (c, addr) = self.pserver.accept()
        g.send('test_pickle', 50, 0)
        sent_on_socket = c.recv(69)
        self.assertEqual(
            sent_on_socket,
            "\x00\x00\x008(lp0\n(S'test_pickle'\np1\n(F0.0\nS'50.000000'\np2\ntp3\ntp4\na."
        )
