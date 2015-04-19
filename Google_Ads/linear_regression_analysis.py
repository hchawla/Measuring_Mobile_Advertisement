import json, codecs, csv, time
import numpy as np

ip_black_list = ['10.8.1.1', '10.8.1.2']	
ip_list = list()
useridb642userid = dict()
userid2useridb64 = dict()
userid2workerid = dict()
userid2ip = dict()
userid2timestamp = dict()
ip2userid = dict()
input_file = 'vpn_clients_beta.txt'
input_f = open(input_file, 'r')
for line in input_f:
	data = line[:-1].split('\t')
	userid = data[0]
	userid_b64 = data[1]
	ip = data[2]
	timestamp = data[3]
	ip_list.append(ip)
	workerId = data[4]
	ip2userid[ip] = userid
	userid2ip[userid] = ip
	userid2workerid[userid] = workerId
	useridb642userid[userid_b64] = userid
	userid2useridb64[userid] = userid_b64
input_f.close()

userid2answers = dict()
userid2zip = dict()
userid2gender = dict()
input_file = 'surveys_beta.txt'
input_f = open(input_file, 'r')
for line in input_f:
	data = line[:-1].split('\t')
	userid_b64 = data[0]
	userid = useridb642userid[userid_b64]
	ip = userid2ip[userid]
	timestamp = data[2]
	timestamp = time.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
	timestamp = time.mktime(timestamp)
	userid2timestamp[userid] = timestamp
	answers = data[3:]
	userid2answers[userid] = answers
	frequency = int(answers[3])
	age = 2015 - int(answers[4])
	gender = answers[5]
	zip_code = answers[6]
	#print userid, userid_b64, ip, zip_code
	education = answers[7]
	income = int(answers[8])
	job = answers[9]
	ethnicity = answers[10]
	politic = answers[11]
	children = answers[12]
	interests = answers[13].split(';')
	userid2zip[userid] = zip_code
	userid2gender[userid] = gender
	print "Age: ", age
	print "Gender: ", gender
	print "Education: ", education
	print "Income: ", income
	print "Job: ", job
	print "Ethnicity: ", ethnicity
	print "Politics: ", politic
	print "Children: ", children
	print "Interests: ", interests
	print "\n\n"

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
print '# of zip_code:', len(zip_code2location)

ip2url = dict()
url2ip = dict()
uri_list = list()
length = 0
for entry in ads:
	length += 1
	dst_ip = entry["dst_addr"]
	if dst_ip in ip_black_list or dst_ip not in ip_list:
		continue
	userid = ip2userid[dst_ip]
	timestamp = float(entry["timestamp"])
	if timestamp+3600 < userid2timestamp[userid]:
#		print userid, timestamp, userid2timestamp[userid]
		continue
	ad_url = ''
	try:
		ad_url = entry["ad_url"]
	except KeyError:
		print 'KeyError'
		pass
	uri = entry["request_uri"]
	if 'gtisc.wei' in uri:
		uri_list.append(uri)
	if dst_ip not in ip2url:
		ip2url[dst_ip] = [ad_url]
	else:
		ip2url[dst_ip].append(ad_url)
	if ad_url not in url2ip:
		url2ip[ad_url] = [dst_ip]
	else:
		url2ip[ad_url].append(dst_ip)
#for key in ip2url.keys():
	#print "IP: "+ key
	#print ip2url[key]

url2category = dict()
input_file = 'ad_cat.txt'
input_f = open(input_file, 'r')
for line in input_f:
	data = line[:-1].split('\t')
	url = data[0]
	Category = data[1]
	url2category[url] = Category

input_f.close()



