import json, codecs, csv
from urlparse import urlparse


ip_black_list = ['10.8.1.1', '10.8.1.2']
useridb642userid = dict()
userid2useridb64 = dict()
userid2workerid = dict()
ip2userid = dict()
input_file = 'vpn_clients_beta.txt'
input_f = open(input_file, 'r')
for line in input_f:
	data = line[:-1].split('\t')
	userid = data[0]
	userid_b64 = data[1]
	ip = data[2]
	workerId = data[4]
	ip2userid[ip] = userid
	userid2workerid[userid] = workerId
	useridb642userid[userid_b64] = userid
	userid2useridb64[userid] = userid_b64
input_f.close()


userid2zip = dict()
userid2gender = dict()
input_file = 'surveys_beta.txt'
input_f = open(input_file, 'r')
for line in input_f:
	data = line[:-1].split('\t')
	userid_b64 = data[0]
	userid = useridb642userid[userid_b64]
	timestamp = data[2]
	answers = data[3:]
	frequency = int(answers[3])
	age = 2015 - int(answers[4])
	gender = answers[5]
	zip_code = answers[6]
	print userid, zip_code
	education = answers[7]
	income = int(answers[8])
	job = answers[9]
	echnicity = answers[10]
	politic = answers[11]
	children = answers[12]
	interests = answers[13].split(';')
	userid2zip[userid] = zip_code
	userid2gender[userid] = gender
input_f.close()

input_file = 'data_beta_final.json'
input_f = open(input_file, 'r')
data = input_f.read()
input_f.close()
ads = json.loads(data)

zip_code2location = dict()
input_file = 'free-zipcode-database-Primary.csv'
with open(input_file, 'rb') as csvfile:
	reader = csv.reader(csvfile, delimiter=',', quotechar='"')
	row_num = 0
	for row in reader:
		row_num += 1
		if row_num == 1:
			continue
		zip_code = row[0]
		city = row[2]
		state = row[3]
		zip_code2location[zip_code] = city+', '+state
		if zip_code == '':
			break

print 'zip_code:', len(zip_code2location)

ip2url = dict()
url2ip = dict()
uri_list = list()
length = 0
for entry in ads:
	length += 1
	dst_ip = entry["dst_addr"]
	if dst_ip in ip_black_list:
		continue
	final_url = ''
	text_url = ''
	click_url = ''
	try:
		final_url = entry["final_destination_url"]
	except KeyError:
		pass
	try:
		text_url = entry["text_ad_url"]
	except KeyError:
		pass
	try:
		click_url = entry["click_url"]
	except KeyError:
		pass
	url = final_url + text_url + click_url
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
	if len(value) < 50:
		break
	print key, len(value)
print len(ip2url)

ip2location_url = dict()
output_file = 'data_beta_final_url2num.txt'
output_f = codecs.open(output_file, encoding='utf-8', mode='w')
for key, value in sorted(url2ip.items(), key=lambda x:len(x[1]), reverse=True):
	host = urlparse(key).netloc
#	if 'localsaver' in host or 'planetfitness'in host:
	if 'localsaver' in host:
		print key, set(value)
		for ip in set(value):
			if ip not in ip2location_url:
				ip2location_url[ip] = [key]
			else:
				ip2location_url[ip].append(key)
	string = key+'\t'+str(len(value))+'\n'
#	string = string.decode('utf-8')
	output_f.write(string)

	if 'spokeo' in host:
		print key
		for ip in set(value):
			try:
				userid = ip2userid[ip]
			except KeyError:
				print 'KeyError', ip
				continue
			gender = userid2gender[userid]
			print ip, userid, gender

print len(url2ip)
output_f.close()

print len(uri_list), length

for key, value in sorted(url2ip.items(), key=lambda x:len(set(x[1])), reverse=True):
	length = len(set(value))
	print key, len(set(value))

for ip, urls in ip2location_url.items():
	userid = ip2userid[ip]
	zip_code = userid2zip[userid]
	try:
		location = zip_code2location[zip_code]
	except KeyError:
		location = 'NULL'
	print ip, zip_code, location, urls
