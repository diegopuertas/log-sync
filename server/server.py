#!/usr/bin/env python3
import socket
import os

HOST = os.getenv('BACKUP_SERVER_LISTENS_TO', '0.0.0.0')
PORT = os.getenv('BACKUP_SERVER_PORT', '65432')
BUFFER_SIZE = os.getenv('BLOCK_SIZE', '1024')
DIRECTORY = os.getenv('BACKUP_DIRECTORY', '/backup')

def receive_bytes(connection, bytes):
    """Receive an exact number of bytes from the socket"""
    data = b''
    while len(data) < bytes:
        chunk = connection.recv(bytes - len(data))
        if not chunk:
            raise ConnectionError("Client disconnected")
        data += chunk
    return data

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Only use in DEV
        s.bind((HOST, PORT))
        s.listen(1)
        print(f"Server listening on {HOST}:{PORT}")

        while True:
            connection, address = s.accept()
            # Create a directory per client, to store the logs
            address = address[0].replace('.', '_')
            os.makedirs(os.path.join(DIRECTORY, address), exist_ok=True)

            with connection:
                print(f"Connection from {address}")

                # 1: Receive request for filename
                # Get filename length (4 bytes is enough)
                filename_len_bytes = receive_bytes(connection, 4)
                filename_len = int.from_bytes(filename_len_bytes, byteorder='big')
                # Get filename
                filename_bytes = receive_bytes(connection, filename_len)
                filename = os.path.join(DIRECTORY, address,
                                        filename_bytes.decode('utf-8'))
                print(f"Requested file: {filename}")

                # 2: Send The file size. 0 if it doesn't exist
                # Check file size and send it to client
                if os.path.exists(filename):
                    filesize = os.path.getsize(filename)
                else:
                    filesize = 0
                connection.sendall(filesize.to_bytes(8, byteorder='big'))
                print(f"Sent filesize: {filesize}")

                # 3: Receive multiple blocks until client disconnects
                with open(filename, 'a', encoding='utf-8') as f:
                    while True:
                        try:
                            # Attempt to read length of transmission
                            data_len_bytes = receive_bytes(connection, 8)
                        except ConnectionError:
                            print("Client finished sending.")
                            break
                        data_len = int.from_bytes(data_len_bytes, byteorder='big')
                        if data_len <= 0:
                            print("No more data.")
                            break
                        try:
                            data = receive_bytes(connection, data_len)
                        except ConnectionError:
                            print("Client finished sending.")
                            break
                        content = data.decode('utf-8')
                        f.write(content)
                        print(f"Appended {data_len} bytes to {filename}")

if __name__ == "__main__":
    start_server()
