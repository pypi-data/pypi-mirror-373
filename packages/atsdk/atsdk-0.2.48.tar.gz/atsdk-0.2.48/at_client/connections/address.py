class Address:
    def __init__(self, host, port):
        self._host = host
        self._port = port
    
    @property
    def host(self):
        return self._host
    
    @property
    def port(self):
        return self._port

    def __str__(self):
        return self._host + ":" + str(self._port)
    
    @staticmethod
    def from_string(host_and_port):
        split = host_and_port.split(":")
        if len(split) != 2:
            raise ValueError("Cannot construct Address from malformed host:port string '" + host_and_port + "'")
        host = split[0]
        try:
            port = int(split[1])
        except ValueError:
            raise ValueError("Cannot construct Address from malformed host:port string '" + host_and_port + "'")
        return Address(host, port)
