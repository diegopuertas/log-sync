# Log Backup System

Small log backup system to illustrate the basic concepts of the client-server
model.

The system consists of two daemons, `client.py` and `server.py`, to set running
on the respective hosts. They are configured via environment variables, as seen
on the text file `environment`.

## Quick test run

To quickly test it, a Docker Compose set-up is provided. To start the system
simply run `docker compose up` and two containers will run on the default
Compose network.

```
.
├── backups
├── client
│   ├── client.py
│   ├── Dockerfile
│   └── requirements.txt
├── docker-compose.yaml
├── environment
├── logs
│   └── dpkg.log
├── README.md
└── server
    ├── Dockerfile
    ├── requirements.txt
    └── server.py
```

The `./backups` directory is mounted as a volume in the server. The `./logs`
directory is mounted as a volume in the client. Once the system is started,
changes in the `logs` directory should be updated in the `backup`, either
putting new files in `logs`or increasing the size of the files in it.

Notice that the files don't go directly under `backup`, but under a directory
representing the IP address of the client. This allows the server to take care
of multiple clients.

## How it works

The client daemon will be checking the files in `$LOG_DIRECTORY` every
`$SLEEP_INTERVAL` seconds. It will then talk with the server daemon in
`$BACKUP_SERVER_HOSTNAME` about each individual file. The server daemon will
respond with the file size (0 if the file doesn't exist).

With the size information, the client daemon will set the file size at the
server as offset, and start transmitting for each file only the new content not
present in the server version of the file.

Files are sent in `$BLOCK_SIZE` bundles, to illustrate the segmented
transmission paradigm present in networking, allowing for flow control and
bounded memory usage. The user can play with this parameter in the environment
file and see the effect in file transmission.

TCP is used, as seen on the creation of the socket:

```
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
```

Something else you need to pay attention to is that sometimes it is necessary to
send and receive a specific amount of data through the network, sending a
filename is one of those cases. Filenames will vary depending on the filesystem
in question, but a 4-bytes length integer should be enough to store the length
any reasonable filename. If we send 4 bytes from one host:

```
s.sendall(len(filename_bytes).to_bytes(4, byteorder='big'))
```

We should be expecting 4 bytes on the other side:

```
filename_len_bytes = receive_bytes(connection, 4)
```

For this purpose, we have the `receive_bytes` function in the server code:

```
def receive_bytes(connection, bytes):
    """Receive an exact number of bytes from the socket"""
    data = b''
    while len(data) < bytes:
        chunk = connection.recv(bytes - len(data))
        if not chunk:
            raise ConnectionError("Client disconnected")
        data += chunk
    return data
```

This function allows the receiving end to consume exactly the amount of data
specified by `bytes` and no more. It accumulates the data in the `chunk`
variable and then returns it to its caller. This is important because it allows
its caller, the server daemon, two things:

1. To partition the incoming network data in segments that make sense, so we can
   isolate meaningful information like filenames, lengths, or data.
2. In the case of lengthy data transmissions, it allows to process the incoming
   data and write it to the disk at the desired interval size. If we set a big
   value for `bytes` it will be good for transmission speed. If we set it small
   it would be better for memory consumption and for using this systems in poor
   quality networks prone to disconnection. Tuning this value we can adjust to
   code to work best for an specific use case.
