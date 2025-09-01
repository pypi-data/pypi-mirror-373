import unittest
from ipio import IPIO, AuthenticationException
import socket


class ExampleTest(unittest.TestCase):
    def setUp(self) -> None:
        pass

    def test_no_connection(self):
        self.assertRaises(
            socket.timeout,
            IPIO._establish_socket_connection,
            "192.168.10.100",
            int(65535),
        )
