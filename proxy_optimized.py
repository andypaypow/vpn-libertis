import socket
import threading
import select
import sys
import time

class ProxyServer:
    def __init__(self, listen_port=8888, target_host='127.0.0.1', target_port=443, max_threads=200):
        self.listen_port = listen_port
        self.target_host = target_host
        self.target_port = target_port
        self.max_threads = max_threads
        self.running = True
        self.active_threads = 0
        self.lock = threading.Lock()
        
    def handle_client(self, client_socket, client_address):
        with self.lock:
            self.active_threads += 1
            
        try:
            # Connect to target
            target_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            target_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            target_socket.connect((self.target_host, self.target_port))
            target_socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            
            # Use larger buffers for better performance (64KB)
            BUFFER_SIZE = 65536
            
            sockets = [client_socket, target_socket]
            
            while self.running:
                readable, _, exceptional = select.select(sockets, [], sockets, 1)
                
                if exceptional:
                    break
                    
                for sock in readable:
                    try:
                        data = sock.recv(BUFFER_SIZE)
                        if not data:
                            return
                        # Send to the other socket
                        target_socket if sock == client_socket else client_socket
                        (target_socket if sock == client_socket else client_socket).sendall(data)
                    except (ConnectionResetError, BrokenPipeError, OSError):
                        return
                        
        finally:
            client_socket.close()
            target_socket.close()
            with self.lock:
                self.active_threads -= 1
                
    def start(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(('0.0.0.0', self.listen_port))
        server_socket.listen(100)
        
        print(f"Proxy server listening on port {self.listen_port}")
        
        while self.running:
            try:
                client_socket, client_address = server_socket.accept()
                
                with self.lock:
                    if self.active_threads >= self.max_threads:
                        client_socket.close()
                        continue
                        
                thread = threading.Thread(
                    target=self.handle_client,
                    args=(client_socket, client_address),
                    daemon=True
                )
                thread.start()
                
            except Exception as e:
                if self.running:
                    print(f"Error: {e}")
                    
    def stop(self):
        self.running = False

if __name__ == "__main__":
    proxy = ProxyServer(listen_port=8888, target_host='127.0.0.1', target_port=443)
    try:
        proxy.start()
    except KeyboardInterrupt:
        proxy.stop()
