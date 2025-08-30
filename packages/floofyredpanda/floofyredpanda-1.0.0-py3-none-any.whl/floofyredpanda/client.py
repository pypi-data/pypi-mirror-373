import socket
import ssl
import queue
import threading
from utils import request

def tell_the_server(host, port, message="bonk"):
    try:
        s = socket.create_connection((host, port))
        s.send(message.encode())
        response = s.recv(4096)
        s.close()
        return response.decode()
    except Exception as e:
        print(f"Floofy panic: {e}")
        return None


def secretly_tell_the_server(host, port, message="bonk", ca=None):
    try:
        ctx = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        if ca:
            ctx.load_verify_locations(cadata=ca)

        with socket.create_connection((host, port)) as raw_sock:
            with ctx.wrap_socket(raw_sock, server_hostname=host) as ssl_sock:
                ssl_sock.send(message.encode())
                return ssl_sock.recv(4096).decode()
    except Exception as e:
        print(f"Secret bonk failed: {e}")
        return None


class RedPandaClient:
    def __init__(self, host, port, ca = None):
        self.host = host
        self.port = port
        self.ca = ca
        self.input = queue.Queue()
        self.output = queue.Queue()
        self.conn = None
        self.running = False

    def connect(self):
        if self.ca is None:
         x = request(self.host, self.port-1, "/ca")
         self.ca = x[0]

        try:
            ctx = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
            ctx.load_verify_locations(cadata=self.ca)
            raw_sock = socket.create_connection((self.host, self.port))
            self.conn = ctx.wrap_socket(raw_sock, server_hostname=self.host)
        except Exception as e:
            print(f"Connection failed: {e}")
            try:
             if raw_sock:
                raw_sock.close()
            except:
                pass
    def send(self, message):
        self.input.put(message)

    def recv(self):
        while True:
            msg = self.output.get()
            yield msg

    def start(self):
        if not self.conn:
            raise RuntimeError("Not connected to server.")
        self.running = True

        def sender():
            while self.running:
                try:
                    msg = self.input.get(timeout=1)
                    self.conn.send(msg.encode())
                except queue.Empty:
                    continue
                except Exception as e:
                    print(f"Send error: {e}")
                    break

        def receiver():
            while self.running:
                try:
                    data = self.conn.recv(4096)
                    if not data:
                        break
                    self.output.put(data.decode())
                except Exception as e:
                    print(f"Receive error: {e}")
                    break

        threading.Thread(target=sender, daemon=True).start()
        threading.Thread(target=receiver, daemon=True).start()

    def close(self):
        self.running = False
        if self.conn:
            self.conn.close()
