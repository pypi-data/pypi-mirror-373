# remote_pb2

[![PyPI version](https://badge.fury.io/py/remote-pb2.svg?icon=si%3Apython)](https://badge.fury.io/py/remote-pb2)

Python package containing **Protobuf-generated classes** for the Remote service.  
This package includes the protobuf bindings (`remote_pb2`, `types_pb2`) along with the required `gogoproto` definitions.

## 📦 Installation

You can install it directly from PyPI:

```bash
pip install remote_pb2
```

## Usage

```bash
from remote_pb2 import remote_pb2
```


## Package Structure

```bash
remote_pb2/
├── remote_pb2.py        # Protobuf definitions for Remote service
├── types_pb2.py         # Common type definitions
└── gogoproto/
    └── gogo_pb2.py      # Gogo proto definitions
```
