import socket
import threading
import struct

class Socks4ProxyServer:
    def __init__(self, host='0.0.0.0', port=1080):
        self.host = host
        self.port = port
        self.running = False
    
    def OnClientConnect(self, client_socket):
        try:
            # SOCKS4协议握手
            data = client_socket.recv(1024)
            if data==b"" or data[0] != 0x04:  # 检查SOCKS4版本
                client_socket.close()
                return
            
            command = data[1]
            port = struct.unpack('>H', data[2:4])[0]
            ip = socket.inet_ntoa(data[4:8])
            
            # 处理CONNECT命令
            if command == 0x01:
                remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                remote_socket.connect((ip, port))
                client_socket.sendall(b'\x00\x5a\x00\x00\x00\x00\x00\x00')  # 成功响应
                
                # 开始双向数据转发
                self.RelayData(client_socket, remote_socket)
                
        except Exception as e:
            print(f"Error: {e}")
            client_socket.sendall(b'\x00\x5b\x00\x00\x00\x00\x00\x00')  # 失败响应
        finally:
            client_socket.close()

    def RelayData(self, sock1, sock2):
        def forward(src, dst):
            while self.running:
                data = src.recv(4096)
                if not data:
                    break
                dst.sendall(data)
        
        t1 = threading.Thread(target=forward, args=(sock1, sock2))
        t2 = threading.Thread(target=forward, args=(sock2, sock1))
        t1.start()
        t2.start()
        t1.join()
        t2.join()
        sock1.close()
        sock2.close()

    def Start(self):
        self.running = True
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            server_socket.bind((self.host, self.port))
            server_socket.listen(5)
            print(f"SOCKS4代理服务器已启动 {self.host}:{self.port}, 按Ctrl+C键停止服务")
            
            while self.running:
                try:
                    client_socket, addr = server_socket.accept()
                    print(f"新连接来自: ({addr[0]}, '{addr[1]}')")
                    threading.Thread(target=self.OnClientConnect, args=(client_socket,)).start()
                except KeyboardInterrupt:
                    self.running = False
                    break

    def Stop(self):
        self.running = False

if __name__ == "__main__":
    proxy = Socks4ProxyServer()
    proxy.Start()
