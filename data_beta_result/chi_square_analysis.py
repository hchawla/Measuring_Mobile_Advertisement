import json, codecs, csv, time
import numpy as np
from chi_square_test import chi_square_test
from urlparse import urlparse

def chi_square_test_of_independence(alpha, rows, columns, userid2row, print_array=False):
	column_num = len(columns)
	row_num = len(rows)
	observed_array = np.zeros((row_num, column_num))
	expected_array = np.zeros((row_num, column_num))
	for j in range(0, column_num):
		url = url_list[j]
		ips = url2ip[url]
		for ip in ips:
			userid = ip2userid[ip]
			i = userid2row[userid]
			observed_array[i, j] += 1
	row_sums = [sum(observed_array[i,:]) for i in range(row_num)]
	column_sums = [sum(observed_array[:,j]) for j in range(column_num)]
	total_sum = sum(row_sums) + sum(column_sums)
	for i in range(0, row_num):
		print rows[i], row_sums[i]
		for j in range(0, column_num):
			expected_value = row_sums[i] * column_sums[j] / total_sum
			expected_array[i,j] = expected_value
	if print_array:
		print observed_array
		print expected_array
	test = chi_square_test()
	chi_square = test.compute_array_chi_square(observed_array, expected_array)
	df = (row_num - 1) * (column_num - 1)
	reject = test.reject_null(chi_square, df, alpha)
	print reject, alpha



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
	print userid, userid_b64, ip, zip_code
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
	userid = ip2userid[key]
	print userid, key, len(value)
print len(ip2url)
user_list = list()
for ip in ip_list:
	userid = ip2userid[ip]
	userid_b64 = userid2useridb64[userid]
	if ip not in ip2url:
		print userid, userid_b64, ip
	else:
		user_list.append(userid)


url_list = list()
total_length = 1.0*sum([len(value) for value in url2ip.values()])
length = 0
for key, value in sorted(url2ip.items(), key=lambda x:len(x[1]), reverse=True):
	length += len(value)
	url_list.append(key)
	if length > 0.8 * total_length:
		print key, length
		break
print total_length

alpha = 0.005

# gender analysis
rows = ['M', 'F']
userid2row = dict()
for userid, answers in userid2answers.items():
	if userid not in user_list:
		continue
	gender = answers[5]
	row = rows.index(gender)
	userid2row[userid] = row

chi_square_test_of_independence(alpha, rows, url_list, userid2row, True)
different_list = [4,5,6,8,11]
for i in different_list:
	url = url_list[i]
	ip2num = dict()
	ips = url2ip[url]
	for ip in ips:
		if ip not in ip2num:
			ip2num[ip] = 1
		else:
			ip2num[ip] += 1
	print i, url, ip2num

'''
# education analysis
#rows = [str(i) for i in range(1, 8)]
rows = [str(i) for i in range(3, 7)]
userid2row = dict()
for userid, answers in userid2answers.items():
	if userid not in user_list:
		continue
	education = answers[7]
	row = rows.index(education)
	userid2row[userid] = row

chi_square_test_of_independence(alpha, rows, url_list, userid2row, True)

# income analysis
rows = [str(i) for i in range(1, 8)]
userid2row = dict()
for userid, answers in userid2answers.items():
	if userid not in user_list:
		continue
	income = answers[8]
	row = rows.index(income)
	userid2row[userid] = row

chi_square_test_of_independence(alpha, rows, url_list, userid2row, True)
'''



'''
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
'''
