"""
Message Protocol

- Use of [header][payload] format
- u16 for header
"""

import struct
import socket
from abc import ABC, abstractmethod


class Protocol(ABC):

    _ENDIAN_ORDER = '>H'
    _MAX_PAYLOAD = 4096

    @classmethod
    @abstractmethod
    def unpack_len(cls, header:bytes) -> int:
        """ decodes length header from bytes """
        pass

    @classmethod
    @abstractmethod
    def pack_len(cls, length:int) -> bytes :
        """ Encodes payload length into header """
        pass

    @classmethod
    @abstractmethod
    def recv_exact(cls, client:socket.socket, n:int) -> bytes | None:
        """ Reads bytes upto length n """
        pass

    @classmethod
    @abstractmethod
    def read_frame(cls, client:socket.socket) -> bytes | None:
        """ Reads the whole frame """
        pass

    @classmethod
    @abstractmethod
    def write_frame(cls, client:socket.socket, payload_bytes: bytes) -> None:
        """ Write the whole frame """
        pass


class MessageProtocol(Protocol):
    """
    Echo Length Predefined Protocol
    """

    @classmethod
    def unpack_len(cls, header) -> int:
        return struct.unpack(cls._ENDIAN_ORDER, header)[0]
    
    @classmethod
    def pack_len(cls, n) -> bytes:
        return struct.pack(cls._ENDIAN_ORDER, n)
    
    @classmethod
    def recv_exact(cls, client, n) -> bytes | None:
        try:
            chunks = []
            received = 0
            while received < n:
                chunk = client.recv(n - received)
                if not chunk:
                    return None
                chunks.append(chunk)
                received += len(chunk)

            return b"".join(chunks)
        
        except socket.error as e:
            print(f"ERROR : MP (recieve exact): {e}")
            return None
        

    @classmethod
    def read_frame(cls, client:socket.socket) -> bytes | None:
        """ Reads the frame and returns payload """
        try:
            ## 1. Read length header
            hdr = cls.recv_exact(client=client, n=2)
            if hdr is None:
                return None
            
            ## 2. Unpack Length
            length = cls.unpack_len(header=hdr)
            if length > cls._MAX_PAYLOAD:
                print(f"Message Exceeds the max size of {cls._MAX_PAYLOAD}")
                return None

            ## 2. Extract payload
            payload = cls.recv_exact(client=client, n=length)
            return payload
        
        except socket.error as e:
            print(f"ERROR : MP (read frame): {e}")
            return None
        
    @classmethod
    def write_frame(cls, client, payload_bytes) -> None:
        """ writes frame and sends it to the client """
        try:
            packet = cls.pack_len(len(payload_bytes)) + payload_bytes
            client.sendall(packet)

        except socket.error as e:
            print(f"ERROR : MP (read frame): {e}")
            return None