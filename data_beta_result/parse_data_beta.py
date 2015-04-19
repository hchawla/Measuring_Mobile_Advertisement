import json, codecs, commands
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, ElementNotVisibleException, WebDriverException, NoSuchWindowException, TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

def kill_chrome():
	output = commands.getoutput('ps ax |grep google-chrome')
#	print output
	lines = output.split('\n')
	for line in lines:
		if ('--disable-background-networking' in line):
			line = line.strip()
			index = line.find(' ')
			pid = line[:index]
#			print pid
			try:
				output = commands.getoutput('kill -9 '+pid)
			except OSError:
#				print 'OSError caught when killing phantomjs', pid
				pass

def close_handles(browser, opened_handles, current_handle):
	handles = set(browser.window_handles)
	new_handles = handles - opened_handles
	for handle in new_handles:
		try:
			browser.switch_to_window(handle)
			browser.close()
		except NoSuchWindowException:
			pass
	browser.switch_to_window(current_handle)

def getgmtime():
	return time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())

def getlocaltime():
	return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

def create_browser(first_page=None, ext=None):
#	browser = webdriver.Chrome(service_args=['--verbose', '--log-path=/dev/null'])
#	executable_path = "/usr/bin/chromedriver"
#	os.environ["webdriver.chrome.driver"] = executable_path
	options = Options()
	options.add_argument('--disable-plugins')
	if ext: 
		if type(ext) == list:
			for e in ext:
				options.add_extension('/home/wei/adware/samples/'+e)
		else:
			options.add_extension('/home/wei/adware/samples/'+ext)

#		options.add_extension('/Users/francis/project/adware/translate.crx')
#	browser = webdriver.Chrome(chrome_options=options, service_args=['--verbose', '--log-path=/dev/null'])
#	browser = webdriver.Chrome(executable_path=executable_path, chrome_options=options)
	try:
		browser = webdriver.Chrome(chrome_options=options)
	except WebDriverException as e:
		print 'Failed to create browser', first_page, ext
		print e
		return None

	if first_page:
		browser.get(first_pate)
	
	return browser

def close_browser(browser):
	browser.quit()

def wait_find_element_by_id(driver, _id):
	counter = 0
	while counter < 5:
		try:
			elem = driver.find_element_by_id(_id)
			break
		except NoSuchElementException:
			time.sleep(1)
			counter += 1
			elem = None
	return elem

def wait_find_element_by_tag_name(driver, name):
	counter = 0
	while counter < 5:
		try:
			elem = driver.find_element_by_tag_name(name)
			break
		except NoSuchElementException:
			time.sleep(1)
			counter += 1
			elem = None
	return elem

def wait_find_elements_by_tag_name(driver, name):
	counter = 0
	while counter < 5:
		elem = driver.find_elements_by_tag_name(name)
		if len(elem) <= 0:
			time.sleep(1)
			counter += 1
		else:
			break
	return elem

def wait_find_element_by_class_name(driver, name):
	counter = 0
	while counter < 5:
		try:
			elem = driver.find_element_by_class_name(name)
			break
		except NoSuchElementException:
			time.sleep(1)
			counter += 1
			elem = None
	return elem

def wait_find_elements_by_class_name(driver, name):
	counter = 0
	while counter < 5:
		elem = driver.find_elements_by_class_name(name)
		if len(elem) <= 0:
			time.sleep(1)
			counter += 1
		else:
			break
	return elem

def main():
	pwd = commands.getoutput('pwd')
	input_file = 'data_beta.json'
#	input_file = 'data_beta_url.json'
	input_f = open(input_file, 'r')
	data = input_f.read()
	input_f.close()
	ads = json.loads(data)
	new_ads = []

	browser = create_browser()
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
		url = url.replace("\\\\u0026", "&")
		url = url.replace("\\u0026", "&")
		if len(url) == 0:
			html = entry["html"]
			html = html.encode('utf-8')
			output_file = 'ad.html'
			output_f = open(output_file, 'w')
			output_f.write(html)
			output_f.close()
			location = 'file://'+pwd+'/'+output_file
			url_set = set()
			try:
				browser.get(location)
				current_handle = browser.current_window_handle
				current_handles = set(browser.window_handles)
				opened_handles = current_handles
				'''
				eles = browser.find_elements_by_xpath("./*")
				eles += browser.find_elements_by_xpath("./*/*")
				eles += browser.find_elements_by_xpath("./*/*/*")
				'''
				eles = wait_find_elements_by_tag_name(browser, '*')
				for ele in eles:
					try:
						value = ele.click()
					except Exception as e:
						pass
				handles = set(browser.window_handles) - current_handles
				print 'New Handles:', len(handles)
				if len(handles) == 0:
					index1 = html.find('destination_url:')
					if index1 > 0:
						index2 = html.find("'", index1+20)
						index1 = html.rfind("'", index1, index2-1)
						destination_url = html[index1+1:index2]
						url_set.add(destination_url)
						print 'destination_url:', destination_url
					else:
						continue
#						raw_input('check')

				while len(handles) > 0:
					handle = handles.pop()
					try:
						browser.switch_to_window(handle)
					except NoSuchWindowException as e:
						print e
						continue
					try:
						alert = browser.switch_to_alert()
						alert.accept()
					except Exception as e:
						pass
					try:
						current_url = browser.current_url
						url_set.add(current_url)
					except TimeoutException as e:
						print e
						pass
					try:
						browser.close()
					except Exception:
						browser.switch_to_window(current_handle)
				close_handles(browser, current_handles, current_handle)
				if len(url_set) > 1 or len(url_set) == 0:
					print 'Multiple Destination URL', url_set 
				url = url_set.pop()
				print url
			except Exception as e:
				print e
		if url[:4] != 'http' and url[:6] != 'market':
			index1 = url.find('destination_url:')
			if index1 < 0:
				continue
			else:
				index2 = url.find("'", index1+20)
				index1 = url.rfind("'", index1, index2-1)
				destination_url = url[index1+1:index2]
				print destination_url
				url = destination_url
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
		entry["ad_url"] = url
		try:
			del entry["html"]
		except KeyError:
			pass
		new_ads.append(entry)
	
	output_file = 'data_beta_url.json'
	output_f = open(output_file, 'w')
	output_f.write(json.dumps(new_ads))
	output_f.close()
		
	close_browser(browser)

	for key, value in sorted(ip2url.items(), key=lambda x:len(x[1]), reverse=True):
		if len(value) < 5:
			break
		print key, len(value)
	print len(ip2url)

	output_file = 'data_beta_url2num.txt'
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

if __name__ == '__main__':
	main()
