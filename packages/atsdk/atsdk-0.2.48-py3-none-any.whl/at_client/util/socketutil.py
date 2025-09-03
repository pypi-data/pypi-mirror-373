from ssl import SSLSocket

LF = b"\x0a"
CRLF = b"\x0d\x0a"


class SocketUtil:

    def __init__(self, sock: SSLSocket):
        self._socket = sock

    def readline(self) -> bytes:
        """
        Read a line from the SSLSocket until a newline character is encountered.

        :param socket: SSLSocket object
        :return: bytes read until newline character
        """

        line = b""
        while True:
            data = self._socket.recv(1)
            if data == b"":
                break  # No more data to read, connection closed
            line += data
            if data == LF:
                break  # Newline character encountered, stop reading
        return line
