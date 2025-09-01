![JsonRpcExtended Logo](https://mauricelambert.github.io/info/python/code/JsonRpcExtended_small.png "JsonRpcExtended logo")

# JsonRpcExtended

## Description

A remote procedure call (RPC) framework based on JSON-RPC, extended to
support alternative data formats and structures such as CSV, XML,
binary and python calls.

## Requirements

This package require:

 - python3
 - python3 Standard Library
 - PegParser

## Installation

### Pip

```bash
python3 -m pip install JsonRpcExtended
```

### Git

```bash
git clone "https://github.com/mauricelambert/JsonRpcExtended.git"
cd "JsonRpcExtended"
python3 -m pip install .
```

### Wget

```bash
wget https://github.com/mauricelambert/JsonRpcExtended/archive/refs/heads/main.zip
unzip main.zip
cd JsonRpcExtended-main
python3 -m pip install .
```

### cURL

```bash
curl -O https://github.com/mauricelambert/JsonRpcExtended/archive/refs/heads/main.zip
unzip main.zip
cd JsonRpcExtended-main
python3 -m pip install .
```

## Usages

### Python script

```python
from JsonRpcExtended import *
from asyncio import run

server = AsyncServer("127.0.0.1", 8520)
run(server.start())
```

```python

from JsonRpcExtended import *
import socket

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
    server.bind(("127.0.0.1", 8520))
    server.listen()
    conn, addr = server.accept()
    with conn:
        while True:
            first_byte = conn.recv(1)
            protocol = get_rpc_format(first_byte)

            if FORMATS.BINARY == protocol:
                data = conn.recv(1024)
            elif FORMATS.JSON == protocol:
                file = conn.makefile(mode='rwb')
                data = file.readline()
            elif FORMATS.CSV == protocol:
                file = conn.makefile(mode='rwb')
                data = file.readline() + file.readline()
            elif FORMATS.XML == protocol:
                raise NotImplementedError("XML parsing is not implemented yet")

            response = loading_classes[protocol].handle_request_data(first_byte + data, conn.recv)
            conn.sendall(response)
```

## Links

 - [Pypi](https://pypi.org/project/JsonRpcExtended)
 - [Github](https://github.com/mauricelambert/JsonRpcExtended)
 - [Documentation](https://mauricelambert.github.io/info/python/code/JsonRpcExtended.html)

## License

Licensed under the [GPL, version 3](https://www.gnu.org/licenses/).
