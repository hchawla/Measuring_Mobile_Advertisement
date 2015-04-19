import json, codecs

input_file = 'data_beta_final.json'
input_f = open(input_file, 'r')
data = input_f.read()
input_f.close()
ads = json.loads(data)

ip2url = dict()
url2ip = dict()
uri_list = list()
length = 0
for entry in ads:
	length += 1
	dst_ip = entry["dst_addr"]
	ad_url = ''
	try:
		ad_url = entry["ad_url"]
	except KeyError:
		pass
	url = ad_url
	uri = entry["request_uri"]
	if 'gtisc.wei' in uri:
		uri_list.append(uri)
	if dst_ip not in ip2url:
		ip2url[dst_ip] = [url]
	else:
		ip2url[dst_ip].append(url)
	if url not in url2ip:
		url2ip[url] = [dst_ip]
	else:
		url2ip[url].append(dst_ip)
	

for key, value in sorted(ip2url.items(), key=lambda x:len(x[1]), reverse=True):
	if len(value) < 5:
		break
	print key, len(value)
print len(ip2url)

output_file = 'data_beta_final_url2num.txt'
output_f = codecs.open(output_file, encoding='utf-8', mode='w')
for key, value in sorted(url2ip.items(), key=lambda x:len(x[1]), reverse=True):
	if len(value) > 40:
		print key, len(value)
	string = key+'\t'+str(len(value))+'\n'
#	string = string.decode('utf-8')
	output_f.write(string)
print len(url2ip)
output_f.close()

print len(uri_list), length
