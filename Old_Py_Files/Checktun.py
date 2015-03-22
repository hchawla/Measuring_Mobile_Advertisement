#!/usr/bin/env python

import dpkt
import sys
import socket
import zlib
f = open(sys.argv[1])
pcap = dpkt.pcap.Reader(f)

packet_ctr = 0
for ts, buf in pcap:
    	ip = dpkt.ip.IP(buf)
    	#print ip
    	if len(ip)>0:
    		tcp = ip.data
	try:
		if tcp.dport == 80 and len(tcp.data) > 0 :
		        http_req = dpkt.http.Request(tcp.data)
			Response=0
			print "\r\n"
			# HTTP request parser
			print "HTTP Request\r\n"
			print socket.inet_ntoa(ip.dst)
			print socket.inet_ntoa(ip.src)
			print tcp.dport
			print tcp.seq
			print tcp.flags
			print http_req.method
			print http_req.uri
			print http_req.version
			print http_req.headers
			print "\r\n"
			print "\r\n"
			for ts1,buf1 in pcap:
				ip1 = dpkt.ip.IP(buf1)
				tcp1 = ip1.data
				if tcp1.sport == 80 and len(tcp1.data) > 0 and tcp1.ack==tcp.seq+len(tcp.data) and socket.inet_ntoa(ip.dst)==socket.inet_ntoa(ip1.src):
		        		http_res = dpkt.http.Response(tcp1.data)
					Response=1
					print "HTTP Response\r\n"
					print socket.inet_ntoa(ip1.dst)
					print socket.inet_ntoa(ip1.src)
					print tcp1.sport
					print tcp.seq+len(tcp.data)
					print tcp1.ack
					print tcp1.flags
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
        except  dpkt.UnpackError, e:
          	print "dpkt raised an unpack error %s" % (e)
