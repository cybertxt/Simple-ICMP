import socket
import time
import threading
import random
import string
import struct
import os
import sys

dst = '188.235.130.116'
dst = '1.2.3.4'

def checksum(msg):
   s = 0
   for i in range(0, len(msg), 2):
       w = ord(msg[i]) + (ord(msg[i+1]) << 8)
       s = ((s + w) & 0xffff) + ((s + w) >> 16)
   return socket.htons(~s & 0xffff)
   
def ip2i(ip):
    return struct.unpack("!I", socket.inet_aton(ip))[0]
    
def ip_packet(VERIHL, TOS, LEN, ID, FLAGFRAG, TTL, PROTO, CHECKSUM, SRC, DST):
    return struct.pack("!BBHHHBBHII", VERIHL, TOS, LEN, ID, FLAGFRAG, TTL, PROTO, CHECKSUM, SRC, DST)
    
def icmp_packet(TYPE, CODE, CHECKSUM, ID, SEQ):
    return struct.pack("!BBHHH", TYPE, CODE, CHECKSUM, ID, SEQ)
    
def icmp_time_exceeded(ip):
    dst_ip = ip2i('3.3.3.3')
    src_ip = ip2i(ip)
    icmp1 = icmp_packet(11, 0, 0, 0, 0)
    ip2 = ip_packet(0x45, 0, 28, 1, 0, 1, 1, 0, dst_ip, src_ip)
    icmp2 = icmp_packet(8, 0, 0, 1, 0)
    icmp2 = icmp_packet(8, 0, checksum(icmp2), 1, 0)
    ip2 = ip_packet(0x45, 0, 28, 1, 0, 1, 1, checksum(ip2), dst_ip, src_ip)
    icmp1 = icmp_packet(11, 0, checksum(icmp1 + ip2 + icmp2), 0, 0)
    return icmp1 + ip2 + icmp2

 
def icmp_request():
    icmp = icmp_packet(8, 0, 0, 1, 0)
    icmp = icmp_packet(8, 0, checksum(icmp), 1, 0)
    return icmp
 
sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
#for i in range(0, 20):
#    time.sleep(0.25)
#    sock.sendto(icmp_time_exceeded(dst), (dst, 1))
sock.sendto(icmp_request(), (dst, 0))
data = sock.recv(1024)
ip_header = data[:20]
ips = ip_header[-8:-4]
print 'Ping from ' + '%i.%i.%i.%i' % (ord(ips[0]), ord(ips[1]), ord(ips[2]), ord(ips[3]))
sock.close()

