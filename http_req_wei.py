#!/usr/bin/env python

import sys
import dpkt
import zlib
import socket
import MySQLdb
import json
import os
import commands
import urllib
import codecs
import re
from BeautifulSoup import BeautifulSoup as BS


def parse_pcap_file(filename, output_f):
	global ad_request_counter, ad_response_counter, ad_written_counter, ad_html_counter
	start_ad_request_counter = ad_request_counter
	start_ad_response_counter = ad_response_counter
	start_ad_written_counter = ad_written_counter
	start_ad_html_counter = ad_html_counter
	# Open the pcap file
	f = open(filename, 'rb')
	pcap = dpkt.pcap.Reader(f)
	# I need to reassmble the TCP flows before decoding the HTTP
	conn = dict() # Connections with current buffer
	request_packets = dict()
	response_packets = dict()
	request_dict = dict()
	response_dict = dict()
	frame_counter = 0
	for ts, buf in pcap:
		frame_counter+=1
		try:
			ip = dpkt.ip.IP(buf)
			if ip.p != dpkt.ip.IP_PROTO_TCP:
				continue
		except (dpkt.dpkt.UnpackError, dpkt.dpkt.NeedData) as e:
			continue
		tcp = ip.data
		tcp_tuple = (socket.inet_ntoa(ip.src), socket.inet_ntoa(ip.dst), tcp.sport, tcp.dport)
		src_addr = socket.inet_ntoa(ip.src)
		dst_addr = socket.inet_ntoa(ip.dst)
		src_port = tcp.sport
		dst_port = tcp.dport
		seq = int(tcp.seq)
		ack = int(tcp.ack)
		tcp_tuple = (src_addr, dst_addr, src_port, dst_port)
		if len(tcp.data) > 0:
#			print frame_counter, tcp_tuple
			if dst_port == 80:
				if tcp_tuple not in request_packets:
					request_packets[tcp_tuple] = [(seq, ack, tcp.data)]
				else:
					request_packets[tcp_tuple].append((seq, ack, tcp.data))
				if (tcp.flags & dpkt.tcp.TH_PUSH) != 0:
					request_stream = sorted(request_packets[tcp_tuple], key=lambda x:x[0])
					length = len(request_stream)
					next_seq = request_stream[0][0]
					request_seq = next_seq
					request = None
					for i in range(0, length):
						current_seq, request_ack, tcp_data = request_stream[i]
						if current_seq == next_seq:
							if request:
								request += tcp_data
							else:
								request = tcp_data
							next_seq += len(tcp_data)
					if request:
						try:
							request = dpkt.http.Request(request)
						except dpkt.dpkt.NeedData as e:
							index_1 = request.find('Content-Length')
							if index_1 > 0:
								index_2 = request.find('\n', index_1)
								content_length = int(request[index_1+16: index_2])
								if content_length > 0:
									print 'Request', content_length
									continue
							print 'Request:', e
							continue
						except dpkt.dpkt.UnpackError as e:
							print 'Request:', e
							continue
						request_dict[tcp_tuple] = (request_seq, request_ack, request)
						if 'doubleclick.net' in request.headers['host'] and request.uri[:6] == '/mads/':
#						if 'gtisc.wei' in request.uri:
							ad_request_counter += 1
					del request_packets[tcp_tuple]
			elif src_port == 80:
				if tcp_tuple not in response_packets:
					response_packets[tcp_tuple] = [(seq, ack, tcp.data)]
				else:
					response_packets[tcp_tuple].append((seq, ack, tcp.data))
				if (tcp.flags & dpkt.tcp.TH_PUSH) != 0:
					request_tuple = (dst_addr, src_addr, dst_port, src_port)
					if request_tuple in request_dict:
						request_seq, request_ack, request = request_dict[request_tuple]
						if not ('doubleclick.net' in request.headers['host'] and request.uri[:6] == '/mads/'):
#						if not ('gtisc.wei' in request.uri):
							del request_dict[request_tuple]
							del response_packets[tcp_tuple]
							continue
						response_stream = sorted(response_packets[tcp_tuple], key=lambda x:x[0])
						length = len(response_stream)
						next_seq = request_ack
						response = None
						for i in range(0, length):
							response_seq, response_ack, tcp_data = response_stream[i]
							if response_seq == next_seq:
								if response:
									response += tcp_data
								else:
									response = tcp_data
								next_seq = response_seq + len(tcp_data)
#								print frame_counter, len(response)
#							print response_seq, len(tcp_data), next_seq, response_seq+len(tcp_data)
						if response:
							try:
								response = dpkt.http.Response(response)
								if 'content-encoding' in response.headers.keys():
									#print "Encoded using ", http.headers['content-encoding']
									if response.headers['content-encoding']=="gzip":
										body = zlib.decompress(response.body, 16+zlib.MAX_WBITS)
									else:
										body = response.body.decode(response.headers['content-encoding'],'strict')
								else:
									body = response.body
								if 'doubleclick.net' in request.headers['host'] and request.uri[:6] == '/mads/' and body:
#								if 'gtisc.wei' in request.uri:
#									pair = {'src_addr': src_addr, 'dst_addr': dst_addr, 'src_port': src_port, 'dst_port': dst_port, 'timestamp': ts, 'request_headers': request.headers, 'request_uri': request.uri, 'response_headers': response.headers, 'response_body': body}
#									print pair
#									print json.dumps(pair)
#									print request.headers
#									print request.uri
#									print response.headers
									ad_response_counter += 1
									
									try:
										soup = BS(body)
										scripts = soup.body.findAll('script')
									except AttributeError:
										continue

									soup_string = str(soup.html)
									soup_string = re.sub(u"(\u2018|\u2019)", "'", soup_string)
									soup_string = soup_string.replace("\u2018", "'")
									soup_string = soup_string.replace("\u2019", "'")
									'''
									soup_string = soup_string.replace("\\u2018", "'")
									soup_string = soup_string.replace("\\u2019", "'")
									soup_string = soup_string.replace("\\\\u2018", "'")
									soup_string = soup_string.replace("\\\\u2019", "'")
									'''
									soup_string = soup_string.replace("\\\\u0026", "&")
									soup_string = soup_string.replace("\\u0026", "&")
									try:
										soup_string = soup_string.decode('string_escape')
									except UnicodeEncodeError as e:
										pass
									num = 0
#									script = scripts[0].string
									script = None
									for s in scripts:
										try:
											if 'renderAd(' in s.string and script is None:
												script = s.string
												num += 1
										except Exception as e:
											print e
											pass
									if num > 1:
										print num
										for s in scripts:
											print s
										raw_input("check some error now!")
									if script is None:
										for s in scripts:
											try:
												if 'buildRhTextAd(' in s.string and script is None:
													script = s.string
													num += 1
											except Exception as e:
												pass
										if script is None:
											if soup_string is None:
												print soup
												raw_input("check error 1 now!")
												continue
											index1 = soup_string.find('go.href')
											if index1 < 0:
												index1 = soup_string.find('adurl=')
												if index1 < 0:
													index1 = soup_string.find('destination_url:')
													if index1 < 0:
														pair = {'src_addr': src_addr, 'dst_addr': dst_addr, 'src_port': src_port, 'dst_port': dst_port, 'timestamp': ts, 'request_uri': request.uri, 'html': soup_string}
													else:
														index2 = soup_string.find("'", index1+20)
														index1 = soup_string.rfind("'", index1, index2-1)
														if index2 < 0 or index1 < 0:
															print soup_string, index1
															raw_input('check')
														destination_url = soup_string[index1+1:index2]
														try:
															destination_url = destination_url.decode('string_escape')
														except UnicodeEncodeError:
															pass
														pair = {'src_addr': src_addr, 'dst_addr': dst_addr, 'src_port': src_port, 'dst_port': dst_port, 'timestamp': ts, 'request_uri': request.uri, 'ad_url': destination_url}
												else:
													index2 = soup_string.find('"', index1+8)
													if index2 < 0:
														index2 = soup_string.find("'", index1+8)
													ad_url= soup_string[index1+6:index2]
													try:
														ad_url = ad_url.decode('string_escape')
													except UnicodeEncodeError:
														pass
													pair = {'src_addr': src_addr, 'dst_addr': dst_addr, 'src_port': src_port, 'dst_port': dst_port, 'timestamp': ts, 'request_uri': request.uri, 'ad_url': ad_url}
											else:
												index2 = soup_string.find('"', index1+14)
												index1 = soup_string.rfind('"', index1, index2-1)
												if index2 < 0:
													print soup_string, index1
													raw_input('check')
												go_href = soup_string[index1+1:index2]
												try:
													go_href = go_href.decode('string_escape')
												except UnicodeEncodeError:
													pass
												pair = {'src_addr': src_addr, 'dst_addr': dst_addr, 'src_port': src_port, 'dst_port': dst_port, 'timestamp': ts, 'request_uri': request.uri, 'ad_url': go_href}
										else:
											script = re.sub(u"(\u2018|\u2019)", "'", script)
											script = script.replace("\\\\u0026", "&")
											script = script.replace("\\u0026", "&")
											try:
												script = script.decode('string_escape')
											except UnicodeEncodeError as e:
												pass
											index1 = script.find('http')
											if index1 < 0:
												print len(scripts), 'XXX\n'
												print script
												raw_input('check missing click and destination url')
												continue
											index2 = script.find('"', index1)
											text_ad_url = script[index1:index2]
											try:
												text_ad_url = text_ad_url.decode('string_escape')
											except UnicodeEncodeError:
												pass
											pair = {'src_addr': src_addr, 'dst_addr': dst_addr, 'src_port': src_port, 'dst_port': dst_port, 'timestamp': ts, 'request_uri': request.uri, 'ad_url': text_ad_url}
#											pair = {'src_addr': src_addr, 'dst_addr': dst_addr, 'src_port': src_port, 'dst_port': dst_port, 'timestamp': ts, 'request_uri': request.uri, 'text_ad_url': text_ad_url}
									else:
										script = re.sub(u"(\u2018|\u2019)", "'", script)
										script = script.replace("\\\\u0026", "&")
										script = script.replace("\\u0026", "&")
										try:
											script = script.decode('string_escape')
										except UnicodeEncodeError as e:
											pass
										index1 = script.find('{')
										index2 = script.rfind('}')
										ad_json = script[index1:index2+1]
										index1 = ad_json.find('final_destination_url')
										if index1 < 0:
											'''
											ad_json = json.loads(ad_json)
											creatives = ad_json['creatives']
											buttons = creatives[0]['buttons']
											final_destination_url = buttons[0]['action_urls']['final_destination_url']
											final_destination_url = buttons[0]['action_urls']['click_url']
											print creatives
	#											print final_destination_url
											'''
											index1 = ad_json.find('click_url')
											if index1 < 0:
												print len(scripts), 'XXX\n'
												print script
												pair = {'src_addr': src_addr, 'dst_addr': dst_addr, 'src_port': src_port, 'dst_port': dst_port, 'timestamp': ts, 'request_uri': request.uri, 'html': soup_string}
#												raw_input('check mising click and destination url')
											else:
												index2 = ad_json.find('"', index1+14)
												index1 = ad_json.rfind('"', index1, index2-1)
												if index2 < 0 or index1 < 0:
													print ad_json
													raw_input('check error')
												click_url = ad_json[index1+1:index2]
												pair = {'src_addr': src_addr, 'dst_addr': dst_addr, 'src_port': src_port, 'dst_port': dst_port, 'timestamp': ts, 'request_uri': request.uri, 'ad_url': click_url}
#												pair = {'src_addr': src_addr, 'dst_addr': dst_addr, 'src_port': src_port, 'dst_port': dst_port, 'timestamp': ts, 'request_uri': request.uri, 'click_url': click_url}
										else:
											index2 = ad_json.find('"', index1+24)
#											final_destination_url = ad_json[index1+24:index2]
											index1 = ad_json.rfind('"', index1, index2-1)
											final_destination_url = ad_json[index1+1:index2]
											try:
												final_destination_url = final_destination_url.decode('string_escape')
											except UnicodeEncodeError:
												print final_destination_url
											pair = {'src_addr': src_addr, 'dst_addr': dst_addr, 'src_port': src_port, 'dst_port': dst_port, 'timestamp': ts, 'request_uri': request.uri, 'ad_url': final_destination_url}
#											pair = {'src_addr': src_addr, 'dst_addr': dst_addr, 'src_port': src_port, 'dst_port': dst_port, 'timestamp': ts, 'request_uri': request.uri, 'final_destination_url': final_destination_url}
#									pair = {'src_addr': src_addr, 'dst_addr': dst_addr, 'src_port': src_port, 'dst_port': dst_port, 'timestamp': ts, 'request_headers': request.headers, 'request_uri': request.uri, 'response_headers': response.headers, 'final_destination_url': final_destination_url}
									if 'html' in pair:
										ad_html_counter += 1
									output_f.write(json.dumps(pair)+',\n')
									ad_written_counter += 1

							except dpkt.dpkt.NeedData as e:
								index_1 = response.find('Content-Length')
								if index_1 > 0:
									index_2 = response.find('\n', index_1)
									content_length = int(response[index_1+16: index_2])
									if content_length > 0:
										print 'Response', content_length
										continue
								print 'Response', e
								continue
#								raise e
						del request_dict[request_tuple]
#						del response_dict[tcp_tuple]
					del response_packets[tcp_tuple]

	del request_dict
	del request_packets
	del response_packets
	f.close()
	print 'Current Ad Counter %d/%d, %d-%d=%d' % (ad_request_counter, ad_response_counter, ad_written_counter, ad_html_counter, ad_written_counter-ad_html_counter)
	if ad_request_counter > start_ad_request_counter:
		log_file = 'data_beta.log'
		log_f = open(log_file, 'a')
		string = '%s\t%d\t%d\t%d\t%d\n' % (filename, ad_request_counter-start_ad_request_counter, ad_response_counter-start_ad_response_counter, ad_written_counter-start_ad_written_counter, ad_html_counter-start_ad_html_counter)
		log_f.write(string)
		log_f.close()

if __name__ == '__main__':
	global ad_request_counter, ad_response_counter, ad_written_counter, ad_html_counter
	ad_request_counter = 0
	ad_response_counter = 0
	ad_written_counter = 0
	ad_html_counter = 0
	log_file = 'data_beta.log'
	pcap_files = list()
	try:
		log_f = open(log_file, 'r')
		for line in log_f:
			data = line.split('\t')
			file_name = data[0]
			index = file_name.find('/')
			if index > 0:
				file_name = file_name[index+1:]
			pcap_files.append(file_name)
		log_f.close()
	except IOError:
		pass
	log_f = open(log_file, 'w')
	log_f.close()
	if len(sys.argv) == 2:
		output_file = 'test.json'
		output_f = open(output_file, 'w')
		output_f.write('[\n')
		parse_pcap_file(sys.argv[1], output_f)
		output_f.seek(-2, os.SEEK_END)
		output_f.truncate()
		output_f.write('\n]\n')
		output_f.close()
#		print "%s <pcap filename>" % sys.argv[0]
#		sys.exit(2)
	else:
		if len(pcap_files) == 0:
			os.chdir('data_beta')
			pcap_files = commands.getoutput('ls *.pcap').split('\n')
			os.chdir('..')
		output_file = 'data_beta.json'
#		output_f = codecs.open(output_file, encoding='utf-8', mode='w')
		output_f = open(output_file, 'w')
		output_f.write('[\n')
		for pcap_file in pcap_files:
			print pcap_file
			parse_pcap_file('data_beta/'+pcap_file, output_f)
		output_f.seek(-2, os.SEEK_END)
		output_f.truncate()
		output_f.write('\n]\n')
		output_f.close()
