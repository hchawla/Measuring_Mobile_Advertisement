#!/usr/bin/env python
# Turns a pcap file with http gzip compressed data into plain text, making it
# easier to follow.

import dpkt
import zlib
import socket
import tables

def parse_pcap_file(filename):
	# Open the pcap file
	f = open(filename, 'rb')
	pcap = dpkt.pcap.Reader(f)
	# I need to reassmble the TCP flows before decoding the HTTP
	conn = dict() # Connections with current buffer
	frame_counter = 0
	for ts, buf in pcap:
		frame_counter+=1
		'''eth = dpkt.ethernet.Ethernet(buf)
		if eth.type != dpkt.ethernet.ETH_TYPE_IP:
			continue'''
	
		ip = dpkt.ip.IP(buf)
		if ip.p != dpkt.ip.IP_PROTO_TCP:
			continue
	
		tcp = ip.data
	
		tupl = (socket.inet_ntoa(ip.src), socket.inet_ntoa(ip.dst), tcp.sport, tcp.dport)
		#print tupl, tcp_flags(tcp.flags)
		print "Frame Number:", frame_counter
		# Ensure these are in order! TODO change to a defaultdict
		if(len(tcp.data)>0):	
			if tupl in conn:
				conn[ tupl ] = conn[ tupl ] + tcp.data
			else:
				conn[ tupl ] = tcp.data
	
			# TODO Check if it is a FIN, if so end the connection
	
			# Try and parse what we have
			try:
				stream = conn[ tupl ]
				if tcp.sport==80 and len(tcp.data)>0:
					http = dpkt.http.Response(stream)
					if 'content-encoding' in http.headers.keys():
						#print "Encoded using ", http.headers['content-encoding']
						print tcp.ack
						if http.headers['content-encoding']=="gzip":
							print zlib.decompress(http.body, 16+zlib.MAX_WBITS)
						else:
							print http.body.decode(http.headers['content-encoding'],'strict')
					#print http.status
				elif tcp.dport==80 and len(tcp.data)>0:
					http = dpkt.http.Request(stream)
					print tcp.seq
					print len(tcp.data)
					#print http.method, http.uri
					print conn[tupl]

				# If we reached this part an exception hasn't been thrown
				'''stream = stream[len(http):]
				if len(stream) == 0:
					del conn[ tupl ]
				else:
					conn[ tupl ] = stream'''
			except  dpkt.UnpackError, e:
		  		print "dpkt raised an unpack error %s" % (e)
				
				print "Frame Number:", frame_counter
				pass
			except dpkt.NeedData,e:
		  		print "dpkt raised an Need error %s" % (e)
				print "Frame Number:", frame_counter
				pass

	f.close()

if __name__ == '__main__':
	import sys
	if len(sys.argv) <= 1:
		print "%s <pcap filename>" % sys.argv[0]
		sys.exit(2)

	parse_pcap_file(sys.argv[1])
