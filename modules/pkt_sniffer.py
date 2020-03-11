import socket
import os
import struct
from time import time
from ctypes import *


####
## "Don't tell me I'm not good enough"
##   Faydee & Miracle @ Unbreakable
####

"""
    Packet sniffer modules:
	arguments: runtime => time in seconds to run for.
"""

class Protocol(Structure):
    def __new__(self, buf):
        return self.from_buffer_copy(buf[:sizeof(self)])

    def __init__(self, buf):
        self.payload = buf[sizeof(self):]

    def __str__(self):
        str_ = "%s: {" % self.__class__.__name__
        for field in self._fields_:
            field_name, *_ = field
            value = getattr(self, field_name)
            str_ += "\n\t %s: %s" %(field_name, str(value))
        if self.payload:
            str_ += "\n\t pkt_blob:\n%s" % str(self.payload)
        str_ += "\n}\n"
        return str_

        
class IP(Structure):
    _fields_ = [
        ("ihl",       c_ubyte, 4),
        ("version",   c_ubyte, 4),
        ("tos",       c_ubyte),
        ("len",       c_ushort),
        ("id",        c_ushort),
        ("offset",    c_ushort),
        ("ttl",       c_ubyte),
        ("proto",     c_ubyte),
        ("sum",       c_ushort),
        ("src",       c_ulong),
        ("dst",       c_ulong)
    ]

    def __new__(self, socket_buffer):
        ihl = (int(socket_buffer[0])&0x0F) * 4
        return self.from_buffer_copy(socket_buffer[:ihl])

    def __init__(self, socket_buffer):
        self.pkt = socket_buffer[self.ihl*4:]
        self.protocol_map = {1:ICMP, 6:TCP, 17:UDP}
        self.src_address = socket.inet_ntoa(struct.pack("<L", self.src))
        self.dst_address = socket.inet_ntoa(struct.pack("<L", self.dst))
        if self.proto in self.protocol_map:
            self.payload = self.protocol_map[self.proto](self.pkt)
        else:
            self.payload = None

    def __str__(self):
        str_ = "IP: {"
        for field in self._fields_:
            field_name, *_ = field
            value = getattr(self, field_name)
            str_ += "\n\t%s: %s" %(field_name, str(value))
            if field_name in ("src", "dst"):
                ip_addr = getattr(self, "%s_address" % field_name)
                str_ += "\n\t%s_ip_format : %s" %(field_name, ip_addr)
                str_ += "\n\t%s_hostname  : %s" %(field_name, socket.getfqdn(ip_addr))
        str_ += "\n\t"
        if self.payload:
            str_ += "\n\t".join(str(self.payload).split("\n"))
        else:
            str_ += "\n\t pkt_blob:\n%s" % str(self.pkt)
        str_ += "\n}\n"
        return str_
                                   
        
        
class ICMP(Protocol):
    _fields_ = [
        ("type",        c_ubyte),
        ("code",        c_ubyte),
        ("chcksum",     c_ushort),
        ("unused",      c_ushort),
        ("nxt_hop_mtu", c_ushort)
    ]


class UDP(Protocol):
    _fields_ = [
        ("sport",   c_ushort),
        ("dport",   c_ushort),
        ("len",     c_ushort),
        ("chcksum", c_ushort)
    ]

    
class TCP(Protocol):
    _fields_ = [
        ("sport",    c_ushort),
        ("dport",    c_ushort),
        ("seq",      c_uint),
        ("ack",      c_uint),
        ("doffset",  c_ushort, 4),
        ("reserved", c_ushort, 6),
        ("urg",      c_ushort, 1),
        ("ack",      c_ushort, 1),
        ("psh",      c_ushort, 1),
        ("rst",      c_ushort, 1),
        ("syn",      c_ushort, 1),
        ("fin",      c_ushort, 1),
        ("wsz",      c_ushort),
        ("chcksum",  c_ushort),
        ("uptr",     c_ushort)
        
    ]

    def __init__(self, buf):
        self.options = buf[:self.doffset*4]
        self.payload = buf[self.doffset*4:]

    def __str__(self):
        return super().__str__().split("\n}\n")[0] + "\n\theader_options:\n%s+\n}\n"%str(self.options)
    

def run(**args):
    if 'runtime' not in args:
        return
    host = socket.gethostbyname(socket.gethostname())
    if os.name == "nt":
        proto = socket.IPPROTO_IP
    else:
        proto = socket.IPPROTO_ICMP

    sniffer = socket.socket(socket.AF_INET, socket.SOCK_RAW, proto)
    sniffer.bind((host, 0))
    sniffer.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

    if os.name == "nt":
        sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)
    pkts, strttm, mxtm = [], time(), args['runtime']
    while (time() - strttm) <= mxtm:
        pkts.append(str(IP(sniffer.recvfrom(65565)[0])))
    if os.name == "nt":
        sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)
    return pkts

