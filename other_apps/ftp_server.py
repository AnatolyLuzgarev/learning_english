from pyftpdlib import servers
from pyftpdlib.handlers import FTPHandler



address = ("0.0.0.0", 8003)  # listen on every IP on my machine on port 8003
server = servers.FTPServer(address, FTPHandler)
server.serve_forever()