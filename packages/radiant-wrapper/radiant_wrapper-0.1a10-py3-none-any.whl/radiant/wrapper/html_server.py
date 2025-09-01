import http.server
import socketserver
import sys
import time
import traceback
import signal
import socket

class _Handler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, fmt, *args):
        sys.stdout.write("[HTTP] " + (fmt % args) + "\n")
        sys.stdout.flush()

class _TCPServer(socketserver.TCPServer):
    allow_reuse_address = True

_alive = True

def _stop(_sig, _frm):
    global _alive
    _alive = False

signal.signal(signal.SIGTERM, _stop)
signal.signal(signal.SIGINT, _stop)

def _wait_port(host, port, timeout=2.0):
    t0 = time.time()
    while time.time() - t0 < timeout:
        try:
            with socket.create_connection((host, port), timeout=0.5):
                return True
        except OSError:
            time.sleep(0.1)
    return False


def serve(ip, port):
    try:
        with _TCPServer(("", port), _Handler) as httpd:
            print(f"Serving at http://{ip}:{port}")
            sys.stdout.flush()
            _wait_port(ip, port, 2.0)
            while _alive:
                httpd.handle_request()
    except OSError as e:
        print(f"[FATAL] HTTP server failed on port {port}: {e}", file=sys.stderr)
        traceback.print_exc()
        while _alive:
            time.sleep(0.5)
    except Exception:
        print("[FATAL] Uncaught exception in server", file=sys.stderr)
        traceback.print_exc()
        while _alive:
            time.sleep(0.5)


def main(ip='localhost', port=5000):
    serve(ip=ip, port=port)
    while _alive:
        time.sleep(0.2)