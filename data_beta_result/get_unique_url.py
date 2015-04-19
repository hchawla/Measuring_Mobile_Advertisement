import random, calendar, time, os, shutil, re, codecs, sys, commands, hmac, urllib, urllib2
from termcolor import colored
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, ElementNotVisibleException, WebDriverException, NoSuchWindowException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import BeautifulSoup
from BeautifulSoup import BeautifulSoup as BS
from BeautifulSoup import Tag
from urlparse import urlparse

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
	url2dsturl = dict()
	dsturl2url = dict()
	try:
		input_file = 'data_beta_url2final.txt'
		input_f = codecs.open(input_file, encoding='utf-8', mode='r')
		for line in input_f:
			if "\\u0026" in line or "\\x" in line:
				continue
			data = line[:-1].split('\t')
			url = data[0]
			dst_url = data[1]
			url2dsturl[url] = dst_url
			if dst_url not in dsturl2url:
				dsturl2url[dst_url] = [url]
			else:
				dsturl2url[dst_url].append(url)
		input_f.close()
	except IOError:
		pass

	dstdomain2url = dict()
	for dsturl, urls in sorted(dsturl2url.items(), key=lambda x:len(x[1]), reverse=True):
		length = len(urls)
		if length > 20:
			print dsturl, length
		index = dsturl.find('?')
		if index > 0:
			host = dsturl[:index]
		else:
			index = dsturl.find(';')
			if index > 0:
				host = dsturl[:index]
			else:
				host = urlparse(dsturl).netloc
		if host not in dstdomain2url:
			dstdomain2url[host] = [dsturl]
		else:
			dstdomain2url[host].append(dsturl)
	
	print len(url2dsturl), len(dsturl2url), len(dstdomain2url)
	for dsthost, urls in sorted(dstdomain2url.items(), key=lambda x:len(x[1]), reverse=True):
		length = len(urls)
		print dsthost, length
		if length < 2:
			break
		if length < 500:
			browser = create_browser()
			try:
				for url in urls:
					browser.get(url)
			except:
				pass
			result = raw_input('next?')
			if result != 'n':
				dst_url = urls[0]
				index = dst_url.find('?')
				if index > 0:
					final_dst_url = dst_url[:index]
				else:
					final_dst_url = 'http://'+dsthost
				dsthost = urlparse(final_dst_url).netloc
				if dsthost == 'spyfly.com':
					final_dst_url = 'http://'+dsthost
				if result == 'm':
					final_dst_url = raw_input('enter the URL:')
				print 'FINAL:', final_dst_url
				for dst_url in urls:
					url_list = dsturl2url[dst_url]
					for url in url_list:
						url2dsturl[url] = final_dst_url
			try:
				close_browser(browser)
			except:
				pass
	
	del dsturl2url
	dsturl2url = dict()
	output_file = 'data_beta_url2unique_final.txt'
	output_f = codecs.open(output_file, encoding='utf-8', mode='w')
	for url, dst_url in url2dsturl.items():
		if dst_url not in dsturl2url:
			dsturl2url[dst_url] = [url]
		else:
			dsturl2url[dst_url].append(url)
		output_f.write(url+'\t'+dst_url+'\n')
	output_f.close()
	print len(dsturl2url)


if __name__ == '__main__':
	main()
