#!/usr/bin/env python

import dpkt
import zlib
f = open('hello.pcap','r')
pcap = dpkt.pcap.Reader(f)
Response=0
# load HTTP pcap file n' link to dpkt attributes
for ts,buf in pcap:
	#print "Loop Request"
        eth = dpkt.ethernet.Ethernet(buf)
    	if eth.type!=dpkt.ethernet.ETH_TYPE_IP:
       		continue
        ip = eth.data
        tcp = ip.data
	try:
		if tcp.dport == 80 and len(tcp.data) > 0:
		        http_req = dpkt.http.Request(tcp.data)
			Response=0
			print "\r\n"
			# HTTP request parser
			print "HTTP Request\r\n"
			print tcp.dport
			print tcp.seq
			print http_req.method
			print http_req.uri
			print http_req.version
			print http_req.headers
			print "\r\n"
			print "\r\n"
			for ts1,buf1 in pcap:
			       	eth1 = dpkt.ethernet.Ethernet(buf1)
				if eth1.type!=dpkt.ethernet.ETH_TYPE_IP:
			       		continue
				ip1 = eth1.data
				tcp1 = ip1.data
				if tcp1.sport == 80 and len(tcp1.data) > 0 and tcp1.ack==tcp.seq+len(tcp.data):
		        		http_res = dpkt.http.Response(tcp1.data)
					Response=1
					print "HTTP Response\r\n"
					print tcp1.sport
					print tcp.seq+len(tcp.data)
					print tcp1.ack
					print http_res.status
					print http_res.reason
					print http_res.version
					print http_res.headers
					if 'content-encoding' in http_res.headers.keys():
						print "Encoded using ", http_res.headers['content-encoding'] 
						if http_res.headers['content-encoding']=="gzip":
							print zlib.decompress(http_res.body, 16+zlib.MAX_WBITS)
						else:
							print http_res.body.decode(http_res.headers['content-encoding'],'strict')
					break
			if Response==0:
				print "No Response Packet Found"
	except dpkt.NeedData:
		print "Need Data Error"
		continue

f.close()
#
