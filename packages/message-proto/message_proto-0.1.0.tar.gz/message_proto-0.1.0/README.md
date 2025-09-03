# Message Protocol

> Originially developed by [Raj Adhikari](https://github.com/r-adhikari97)

A simple **length-prefixed framing protocol** for TCP sockets, designed
for building echo servers, chat systems, or any application requiring
structured message exchange.

---

## 🔄 Changelog !

> View change log : [here](CHANGELOG.md)

---

## 📦 Overview

Message Protocol (MP) wraps raw TCP streams into discrete messages using
the following structure:

    [ 2-byte header ][ payload ]

- **Header**: Unsigned 16-bit big-endian integer (`u16`, network
  order).Represents the number of bytes in the payload.Max: 4096 bytes (configurable).\
- **Payload**: Raw application data (`bytes`).

This framing ensures each call to `read_frame()` returns **exactly one
complete message**, regardless of how TCP splits or merges packets.

---

## ⚙️ Features

- ✅ Works on both client & server with the same class\
- ✅ Protects against partial reads (`recv_exact` guarantees n bytes)\
- ✅ Guards against oversized messages (`_MAX_PAYLOAD = 4096`)\
- ✅ Clean separation of **framing** and **application payload**

---

## 🖥️ Usage

**NOTE**: Requires socket!

### Installation

```
pip install message-proto
```

### Sending a message

```python
from message_protocol import MessageProtocol

msg = b"hello world"
MessageProtocol.write_frame(sock, msg)
```

### Receiving a message

```python
payload = MessageProtocol.read_frame(sock)
if payload is None:
    print("Connection closed")
else:
    print("Got:", payload.decode())
```

---

## 📑 Protocol Rules

1. All messages MUST be framed using `MessageProtocol.write_frame`.\
2. Payloads MUST NOT include their own headers (the class adds one
   automatically).\
3. Messages longer than `_MAX_PAYLOAD` (default 4096 bytes) will be
   rejected.\
4. Payloads of length `0` are valid (useful for pings/keepalives).

---

## 🧪 Example Wire Format

For `payload = b"ABC"`:

    0003 41424

- `0003` → header = 3 bytes\
- `414243` → payload (`"ABC"`)

---
