import socket
import os
from time import time

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
        pkts.append(sniffer.recvfrom(65565))
    if os.name == "nt":
        sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)
    return pkts
