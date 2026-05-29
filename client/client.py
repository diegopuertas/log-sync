import socket
import os
import time

HOST = os.getenv('BACKUP_SERVER_HOSTNAME' ,'server')
PORT = os.getenv('BACKUP_SERVER_PORT' ,'65432')
DIRECTORY = os.getenv('LOG_DIRECTORY' ,'/log')
BLOCK_SIZE = os.getenv('BLOCK_SIZE' ,'1024')
SLEEP_INTERVAL = os.getenv('SLEEP_INTERVAL' ,'10')

def send_file(full_path):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        filename = os.path.basename(full_path)
        filename_bytes = filename.encode('utf-8')
        print(f"Connecting to {HOST}:{PORT}")
        s.connect((HOST, PORT))

        # 1: Send filename length and filename
        s.sendall(len(filename_bytes).to_bytes(4, byteorder='big'))
        s.sendall(filename_bytes)

        # 2: Receive current filesize from server
        filesize_bytes = s.recv(8)
        filesize = int.from_bytes(filesize_bytes, byteorder='big')
        print(f"Server reports existing filesize: {filesize}")

        # 3: Send data in BLOCK_SIZE chunks
        with open(full_path, 'r', encoding='utf-8') as f:
            # Move past the offset, don't send what's already there
            f.seek(filesize)
            # Start sending chunks
            while True:
                content = f.read(BLOCK_SIZE)
                if not content:
                    break
                chunk_bytes = content.encode('utf-8')
                # Send the chunk length
                s.sendall(len(chunk_bytes).to_bytes(8, byteorder='big'))
                # Send the chunk itself
                s.sendall(chunk_bytes)
                print(f"Sent {len(chunk_bytes)} bytes from {filename}")

        print("Finished sending")
    
def sync_dir(directory):
    for filename in os.listdir(directory):
        full_path = os.path.join(directory, filename)
        print(f"Processing file: {full_path}")
        if os.path.isfile(full_path):
            send_file(full_path)

if __name__ == "__main__":
    while True:
        sync_dir(DIRECTORY)
        print(f"Sleeping for {SLEEP_INTERVAL} seconds...")
        time.sleep(SLEEP_INTERVAL)