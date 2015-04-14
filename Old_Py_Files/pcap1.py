#!/usr/bin/env python


import dpkt

counter=0
ipcounter=0
tcpcounter=0
udpcounter=0

filename='test.2015-01-27-12-57-46+0000.pcap'

for ts, pkt in dpkt.pcap.Reader(open(filename,'r')):

    counter+=1
    eth=dpkt.ethernet.Ethernet(pkt) 
    if eth.type!=dpkt.ethernet.ETH_TYPE_IP:
       continue

    ip=eth.data
    ipcounter+=1

    if ip.p==dpkt.ip.IP_PROTO_TCP: 
       tcpcounter+=1

    if ip.p==dpkt.ip.IP_PROTO_UDP:
       udpcounter+=1
     
    tcp=ip.data
    if tcp.dport==80 and len(tcp.data)>0:
	http = dpkt.http.Request(tcp.data)
	print http.uri
print ("Total number of packets in the pcap file: ", counter)
print ("Total number of ip packets: ", ipcounter)
print ("Total number of tcp packets: ", tcpcounter)
print ("Total number of udp packets: ", udpcounter)
