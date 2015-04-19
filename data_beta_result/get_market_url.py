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
	input_file = 'data_beta_url2num.txt'
	input_f = codecs.open(input_file, encoding='utf-8', mode='r')
	url_list = list()
	for line in input_f:
		data = line[:-1].split('\t')
		url = data[0]
		url_list.append(url)
	input_f.close()
	processed_urls = list()
	try:
		input_file = 'data_beta_url2final.txt'
		input_f = codecs.open(input_file, encoding='utf-8', mode='r')
		for line in input_f:
			data = line[:-1].split('\t')
			url = data[0]
			processed_urls.append(url)
		input_f.close()
	except IOError:
		pass

	length = len(url_list)
	counter = 0
	browser = create_browser()
	output_file = 'data_beta_url2final.txt'
	output_f = codecs.open(output_file, encoding='utf-8', mode='a')
	for url in url_list:
		counter += 1
		if url in processed_urls:
			continue
		print 'Processing %d/%d\t%s' % (counter, length, url)
		browser_url = url.replace('\\u0026', '&')
		index = browser_url.find('http')
		if index > 0:
			browser_url = browser_url[index:]
		index = browser_url.find('adurl=')
		if index > 0:
			browser_url = browser_url[index+6:]
		browser_url = urllib.unquote(browser_url)
		if browser_url[:6] == "market":
			index1 = browser_url.find('id=')
			if index1 > 0:
				index2 = browser_url.find('&', index1)
				if index2 < 0:
					app_id = browser_url[index1+3:]
				else:
					app_id = browser_url[index1+3:index2]
				browser_url = 'https://play.google.com/store/apps/details?id='+app_id
				browser_url = urllib.unquote(browser_url)
		else:
			try:
				response = urllib2.urlopen(browser_url)
			except Exception as e:
				str_e = str(e)
				if 'Redirection to url' and 'market://' in str_e:
					index1 = str_e.find('market://')
					index2 = str_e.find("'", index1)
					if index2 < 0:
						index2 = str_e.find('"', index1)
					browser_url = str_e[index1:index2]
					index1 = browser_url.find('id=')
					if index1 > 0:
						index2 = browser_url.find('&', index1)
						if index2 < 0:
							app_id = browser_url[index1+3:]
						else:
							app_id = browser_url[index1+3:index2]
						browser_url = 'https://play.google.com/store/apps/details?id='+app_id
						browser_url = urllib.unquote(browser_url)
				else:
					print e
					continue
		
		try:
			browser.get(browser_url)
		except Exception as e:
			continue
		try:
			alert = browser.switch_to_alert()
			alert.accept()
		except Exception as e:
			pass
		num = 0
		while num < 3:
			current_url = browser.current_url
			if len(current_url) > 0:
				break
			time.sleep(1)
			num += 1
		if num == 3 and len(current_url) == 0:
			continue
		if 'play.google.com/store/apps/details?' in current_url:
			index1 = current_url.find('id=')
			if index1 > 0:
				index2 = current_url.find('&', index1)
				if index2 > 0:
					current_url = current_url[:index2]
		print current_url + '\n'
		output_f.write(url+'\t'+current_url+'\n')
	output_f.close()
	close_browser(browser)

if __name__ == '__main__':
	main()
