#!/usr/bin/env python

import dpkt
import zlib
f = open('test.pcap','r')
pcap = dpkt.pcap.Reader(f)
Response=0
# load HTTP pcap file n' link to dpkt attributes
frame_counter = 0
for ts,buf in pcap:
	#print "Loop Request"
	frame_counter+=1
        ip = dpkt.ip.IP(buf)
        tcp = ip.data
	try:
		if tcp.dport == 80 and len(tcp.data) > 0:
		        http_req = dpkt.http.Request(tcp.data)
			Response=0
			print "\r\n"
			# HTTP request parser
			print "Frame Number:", frame_counter
			print tcp.data
			frame_counter1=0
			for ts1,buf1 in pcap:
				frame_counter1+=1
				ip1 = dpkt.ip.IP(buf1)
				tcp1 = ip1.data
				if tcp1.sport == 80 and len(tcp1.data) > 0 and tcp1.ack==tcp.seq+len(tcp.data):
		        		http_res = dpkt.http.Response(tcp1.data)
					Response=1
					print "Frame Number:", frame_counter1
					if 'content-encoding' in http_res.headers.keys():
						print "Encoded using ", http_res.headers['content-encoding'] 
						if http_res.headers['content-encoding']=="gzip":
							print zlib.decompress(http_res.body, 16+zlib.MAX_WBITS)
						else:
							print http_res.body.decode(http_res.headers['content-encoding'],'strict')
					break
			if Response==0:
				print "No Response Packet Found"
	except dpkt.NeedData,e:
          		#print "dpkt raised an Need error %s" % (e)
			print "Frame Number:", frame_counter
			pass
	except dpkt.UnpackError,e:
          		#print "dpkt raised an unpack error %s" % (e)
			print "Frame Number:", frame_counter
			pass
f.close()

