import json, codecs, csv, time
import numpy

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
no_clients = 0
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
	no_clients +=1
input_f.close()
print "No. of Clients are: ",no_clients
matrix = numpy.zeros(shape=(no_clients,33))
userid2answers = dict()
userid2zip = dict()
userid2gender = dict()
input_file = 'surveys_beta.txt'
input_f = open(input_file, 'r')
client = 0
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
	email = answers[14]
	userid2zip[userid] = zip_code
	userid2gender[userid] = gender
	#print ip
	#print "Age: ", age
	#print "Gender: ", gender
	#print "Education: ", education
	#print "Income: ", income
	#print "Job: ", job
	#print "Ethnicity: ", ethnicity
	#print "Politics: ", politic
	#print "Children: ", children
	#print "Interests: ", interests
	#print "\n\n"
	matrix[client][0]= int(userid[-2:])
	matrix[client][1]= age
	if gender =='M':
		matrix[client][2]= 1
	matrix[client][3]= education
	matrix[client][4]= income
	matrix[client][6]= ethnicity
	matrix[client][7]= politic
	if children =='Y':
		matrix[client][8]= 1
	if 'Arts & Entertainment' in interests:
		matrix[client][9]= 1	#Arts & Entertainment
	if 'Autos & Vehicles' in interests:
		matrix[client][10]= 1	#Autos & Vehicles
	if 'Beauty & Fitness' in interests:
		matrix[client][11]= 1	#Beauty & Fitness
	if 'Books & Literature' in interests:
		matrix[client][12]= 1	#Books & Literature
	if 'Business & Industrial' in interests:
		matrix[client][13]= 1	#Business & Industrial
	if 'Computers & Electronics' in interests:
		matrix[client][14]= 1	#Computers & Electronics
	if 'Finance' in interests:
		matrix[client][15]= 1	#Finance
	if 'Food & Drinks' in interests:
		matrix[client][16]= 1	#Food & Drinks
	if 'Games' in interests:
		matrix[client][17]= 1	#Games
	if 'Hobbies & Leisure' in interests:
		matrix[client][18]= 1	#Hobbies & Leisure
	if 'Home & Garden' in interests:
		matrix[client][19]= 1	#Home & Garden
	if 'Internet & Telecom' in interests:
		matrix[client][20]= 1	#Internet & Telecom
	if 'Jobs & Education' in interests:
		matrix[client][21]= 1	#Jobs & Education
	if 'Law & Government' in interests:
		matrix[client][22]= 1	#Law & Government
	if 'News' in interests:
		matrix[client][23]= 1	#News
	if 'Online Communities' in interests:
		matrix[client][24]= 1	#Online Communities
	if 'People & Society' in interests:
		matrix[client][25]= 1	#People & Society
	if 'Pets & Animals' in interests:
		matrix[client][26]= 1	#Pets & Animals
	if 'Real Estate' in interests:
		matrix[client][27]= 1	#Real Estate
	if 'Reference' in interests:
		matrix[client][28]= 1	#Reference
	if 'Science' in interests:
		matrix[client][29]= 1	#Science
	if 'Shopping' in interests:
		matrix[client][30]= 1	#Shopping
	if 'Sports' in interests:
		matrix[client][31]= 1	#Sports
	if 'Travel' in interests:
		matrix[client][32]= 1	#Travel
	client += 1

input_f.close()

#print matrix

input_file = 'data_beta_final.json'
input_f = open(input_file, 'r')
data = input_f.read()
input_f.close()
ads = json.loads(data)
mat_Cat = numpy.zeros(shape=(no_clients,25))
ip2url = dict()
url2ip = dict()
uri_list = list()
length = 0
url2category = dict()
input_file = 'ad_cat.txt'
input_f = open(input_file, 'r')
for line in input_f:
	data = line[:-1].split('\t')
	url = data[0]
	Category = data[1]
	url2category[url] = Category
input_f.close()
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
client=0	
for key in ip2url.keys():
	mat_Cat[client][0]= ip2userid[key][-2:]
	data = ip2url[key]
	for url in data:
		try:
		
			Category = url2category[url]
			if 'Arts & Entertainment' in Category:
				mat_Cat[client][1] += 1		#Arts & Entertainment
			if 'Autos & Vehicles' in Category:
				mat_Cat[client][2] += 1		#Autos & Vehicles
			if 'Beauty & Fitness' in Category:
				mat_Cat[client][3] += 1		#Beauty & Fitness
			if 'Books & Literature' in Category:
				mat_Cat[client][4] += 1		#Books & Literature
			if 'Business & Industrial' in Category:
				mat_Cat[client][5] += 1		#Business & Industrial
			if 'Computers & Electronics' in Category:
				mat_Cat[client][6] += 1		#Computers & Electronics
			if 'Finance' in Category:
				mat_Cat[client][7] += 1		#Finance
			if 'Food & Drinks' in Category:
				mat_Cat[client][8] += 1		#Food & Drinks
			if 'Games' in Category:
				mat_Cat[client][9] += 1		#Games
			if 'Hobbies & Leisure' in Category:
				mat_Cat[client][10] += 1	#Hobbies & Leisure
			if 'Home & Garden' in Category:
				mat_Cat[client][11] += 1	#Home & Garden
			if 'Internet & Telecom' in Category:
				mat_Cat[client][12] += 1	#Internet & Telecom
			if 'Jobs & Education' in Category:
				mat_Cat[client][13] += 1	#Jobs & Education
			if 'Law & Government' in Category:
				mat_Cat[client][14] += 1	#Law & Government
			if 'News' in Category:
				mat_Cat[client][15] += 1	#News
			if 'Online Communities' in Category:
				mat_Cat[client][16] += 1	#Online Communities
			if 'People & Society' in Category:
				mat_Cat[client][17] += 1	#People & Society
			if 'Pets & Animals' in Category:
				mat_Cat[client][18] += 1	#Pets & Animals
			if 'Real Estate' in Category:
				mat_Cat[client][19] += 1	#Real Estate
			if 'Reference' in Category:
				mat_Cat[client][20] += 1	#Reference
			if 'Science' in Category:
				mat_Cat[client][21] += 1	#Science
			if 'Shopping' in Category:
				mat_Cat[client][22] += 1	#Shopping
			if 'Sports' in Category:
				mat_Cat[client][23] += 1	#Sports
			if 'Travel' in Category:
				mat_Cat[client][24] += 1	#Travel
		except KeyError as e:
			print "KeyError for URL:",e
			continue
	client += 1
#print mat_Cat
list1 = [int(x) for x in matrix[:,0].tolist()]
list2 = [int(y) for y in mat_Cat[:,0].tolist()]
x = list()
y = list()
for ip in ip2userid:
	client= int(ip2userid[ip][-2:])
	#print client
	try:
		index1 = list1.index(client)
		x = matrix[index1,:].tolist()
		index2 = list2.index(client)
		y = mat_Cat[index2,:].tolist()
	except:
		continue
print ",".join([str(i) for i in x])
print ",".join(str(i) for i in y)
