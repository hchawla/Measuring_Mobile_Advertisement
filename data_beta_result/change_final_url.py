import json, codecs

url2dsturl = dict()
input_file = 'data_beta_url2unique_final.txt'
input_f = codecs.open(input_file, encoding='utf-8', mode='r')
for line in input_f:
	data = line[:-1].split('\t')
	url = data[0]
	dst_url = data[1]
	url2dsturl[url] = dst_url
input_f.close()

input_file = 'data_beta_url.json'
input_f = open(input_file, 'r')
data = input_f.read()
input_f.close()
ads = json.loads(data)

length = 0
for entry in ads:
	length += 1
	dst_ip = entry["dst_addr"]
	ad_url = ''
	try:
		ad_url = entry["ad_url"]
	except KeyError:
		pass
	try:
		entry["ad_url"] = url2dsturl[ad_url]
	except KeyError:
		print ad_url
	
output_file = 'data_beta_final.json'
output_f = open(output_file, 'w')
output_f.write(json.dumps(ads))
output_f.close()
