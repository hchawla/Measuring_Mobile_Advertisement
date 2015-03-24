#!/usr/bin/env python

import dpkt
import zlib
import socket
import MySQLdb
import json

def parse_pcap_file(filename):
	# Open the pcap file
	f = open(filename, 'rb')
	pcap = dpkt.pcap.Reader(f)
	# I need to reassmble the TCP flows before decoding the HTTP
	conn = dict() # Connections with current buffer
	frame_counter = 0
	try:
		db = MySQLdb.connect("localhost","root","password","MMA")
		cursor = db.cursor()
	except:
		print "Connection Error"
	for ts, buf in pcap:
		frame_counter+=1
		ip = dpkt.ip.IP(buf)
		if ip.p != dpkt.ip.IP_PROTO_TCP:
			continue
		tcp = ip.data
		tupl = (socket.inet_ntoa(ip.src), socket.inet_ntoa(ip.dst), tcp.sport, tcp.dport)
		#print tupl, tcp_flags(tcp.flags)
		#print "Frame Number:", frame_counter
		# Ensure these are in order! TODO change to a defaultdict
		if(len(tcp.data)>0):	
			if tupl in conn:
				conn[ tupl ] = conn[ tupl ] + tcp.data
			else:
				conn[ tupl ] = tcp.data
	
			# TODO Check if it is a FIN, if so end the connection
	
			try:
				stream = conn[ tupl ]
				if tcp.sport==80 and len(tcp.data)>0 and  (( tcp.flags & dpkt.tcp.TH_PUSH) != 0):
					http = dpkt.http.Response(stream)
					headers = http.headers
					ack = int(tcp.ack)
					source = socket.inet_ntoa(ip.src)
					dst = socket.inet_ntoa(ip.dst)
					dport = tcp.dport;
					if 'content-encoding' in http.headers.keys():
						#print "Encoded using ", http.headers['content-encoding']
						if http.headers['content-encoding']=="gzip":
							#print zlib.decompress(http.body, 16+zlib.MAX_WBITS)
							body = zlib.decompress(http.body, 16+zlib.MAX_WBITS)
							try:
								# Execute the SQL command
							   	cursor.execute("INSERT INTO Ad_Responses(SOURCE_IP,DESTINATION_IP,RES_STREAM,TCP_ACK,DPORT) VALUES(%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE SOURCE_IP=%s,DESTINATION_IP=%s,RES_STREAM=%s,DPORT=%s", (source,dst,body,ack,dport,source,dst,body,dport))
							  	# Commit your changes in the database
							   	db.commit()
							except MySQLdb.Error as err:
		  						print("Something went wrong: {}".format(err))
							   	# Rollback in case there is any error
							   	db.rollback()
						else:
							#print http.body.decode(http.headers['content-encoding'],'strict')
							body = http.body.decode(http.headers['content-encoding'],'strict')
							try:
								# Execute the SQL command
							   	cursor.execute("INSERT INTO Ad_Responses(SOURCE_IP,DESTINATION_IP,RES_STREAM,TCP_ACK,DPORT) VALUES(%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE SOURCE_IP=%s,DESTINATION_IP=%s,RES_STREAM=%s,DPORT=%s", (source,dst,body,ack,dport,source,dst,body,dport))
							  	# Commit your changes in the database
							   	db.commit()
							except MySQLdb.Error as err:
		  						print("Something went wrong: {}".format(err))
							   	# Rollback in case there is any error
							   	db.rollback()
					else:
						body = http.body
						#print body
						try:
							# Execute the SQL command
							cursor.execute("INSERT INTO Ad_Responses(SOURCE_IP,DESTINATION_IP,RES_STREAM,TCP_ACK,DPORT) VALUES(%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE SOURCE_IP=%s,DESTINATION_IP=%s,RES_STREAM=%s,DPORT=%s", (source,dst,body,ack,dport,source,dst,body,dport))
							# Commit your changes in the database
							db.commit()
						except MySQLdb.Error as err:
		  					print("Something went wrong: {}".format(err))
							# Rollback in case there is any error
							db.rollback()
					#print http.status
					#print "Request deleted"
					del conn[tupl]
				elif tcp.dport==80 and len(tcp.data)>0:
					http = dpkt.http.Request(stream)
					#print http.method, http.uri
					#print conn[tupl]
					host = http.headers['host']
					if 'user-agent' in http.headers:
						user_agent= http.headers['user-agent']
					elif 'User-Agent' in http.headers:
						user_agent=http.headers['User-Agent']
					else:
						user_agent = "No User Agent Found."
					source = socket.inet_ntoa(ip.src)
					dst = socket.inet_ntoa(ip.dst)
					length = int(len(tcp.data))
					seq = int(tcp.seq)
					sport = tcp.sport
					#accept=http.headers['accept']
					
					#sql = "INSERT INTO Ad_Requests(HOST,USER_AGENT,SOURCE_IP,DESTINATION_IP,REQ_STREAM,HTTP_SEQ,LEN_TCP,TCP_ACK) VALUES(%s,%s,%s,%s,%s,%d,%d,%d)", (host,user_agent,source,dst,http.body,seq,length,seq+length)
					try:
						if host=="googleads.g.doubleclick.net":
							# Execute the SQL command
					   		cursor.execute("INSERT INTO Ad_Requests(HOST,USER_AGENT,SOURCE_IP,DESTINATION_IP,REQ_STREAM,HTTP_SEQ,LEN_TCP,TCP_ACK,SPORT) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)", (host,user_agent,source,dst,stream,seq,length,seq+length,sport))
					  	# Commit your changes in the database
					   		db.commit()
					except MySQLdb.Error as err:
  						print("Something went wrong: {}".format(err))
					   	# Rollback in case there is any error
					   	db.rollback()
					#print "Request deleted"
					del conn[tupl]
			except  dpkt.UnpackError, e:
		  		#print "dpkt raised an unpack error %s" % (e)
				pass
			except dpkt.NeedData,e:
		  		#print "dpkt raised an Need error %s" % (e)
				pass
			except KeyError,e:
				print 'Hello',source,dst
				pass
	try:
		cursor.execute("SELECT Ad_Requests.SOURCE_IP,Ad_Requests.DESTINATION_IP,Ad_Requests.REQ_STREAM,Ad_Responses.RES_STREAM FROM Ad_Requests,Ad_Responses where Ad_Responses.TCP_ACK=Ad_Requests.TCP_ACK and Ad_Responses.DPORT=Ad_Requests.SPORT and Ad_Requests.DESTINATION_IP=Ad_Responses.SOURCE_IP")
		result = cursor.fetchall()
		for row in result:
			text = "\n\n'Request': "
			SOURCE_IP = row[0]
			DESTINATION_IP = row[1]
			REQ_STREAM = row[2]
			text += REQ_STREAM
			RES_STREAM = row[3]
			text+="'Response': " + RES_STREAM+"\n\n"
			print text
	except MySQLdb.Error as err:
  		print("Something went wrong while Selecting: {}".format(err))
		# Rollback in case there is any error
		db.rollback()			
	
	db.close()
	f.close()

if __name__ == '__main__':
	import sys
	if len(sys.argv) <= 1:
		print "%s <pcap filename>" % sys.argv[0]
		sys.exit(2)

	parse_pcap_file(sys.argv[1])
