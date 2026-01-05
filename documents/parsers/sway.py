from os import getcwd, remove, makedirs
from os.path import join, exists
from shutil import rmtree

from selenium import webdriver

from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

## THIS IS FOR DOWNLOADING THE IMAGES
from urllib.request import urlretrieve
from PIL import Image

## CUSTOM MODULES
from files import parse as parse_files


def parse (browser, datum = {}, complex_content = False):
	download_dir = join(getcwd(), 'sway_downloads')
	if not exists(download_dir):
		makedirs(download_dir)

	WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'viewport')))
	root = browser.find_element_by_css_selector('#storyroot')
	viewport = root.find_element_by_css_selector('.viewport-background')
	main_container = root.find_element_by_css_selector('.viewport-background > .container')

	# WAIT UNTIL THE LAST PART OF THE PAGE IS LOADED (THIS ASSUMES CONTENT IS LOADED SYNCHRONOUSLY, WHICH IS UNCERTAIN)
	WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'endOfStoryWrapper')))

	datum['url'] = browser.current_url
	datum['title'] = browser.title
	datum['keywords'] = browser.find_element(By.XPATH, '//meta[@name="keywords"]').get_attribute('content')

	## ADDITIONAL METADATA
	datum['additional_metadata'] = {}
	datum['additional_metadata']['description'] = browser.find_element(By.XPATH, '//meta[@name="description"]').get_attribute('content')

	if complex_content == True: datum['content'] = []
	else: datum['content'] = ''

	containers = root.find_elements_by_css_selector('.viewport-background > .container > .container > .container')
	for container in containers:
		## THIS DOES THE SCROLLING
		action = ActionChains(browser)
		action.move_to_element(container).perform()

		if container.get_attribute('role') != 'contentinfo':
			cid = container.get_attribute('id')
			text_wrappers = container.find_elements_by_css_selector('.text_wrapper')
			imgs = container.find_elements_by_css_selector('img:not(.missingImageIcon)')
			
			for text in text_wrappers:
				## CREATE OBJECT WITH VALUES
				if complex_content == True: datum['content'].append({ 'type': text.get_attribute('class').split(' ')[1].replace('None', '').lower(), 'content': text.get_attribute('innerText') })
				else: datum['content'] += '\n\n{}'.format(text.get_attribute('innerText'))
			for img in imgs:
				src = img.get_attribute('src')
				try: 
					file = join(download_dir, cid)
					urlretrieve(src, file)
					png = '{}.png'.format(file)
					Image.open(file).save(png)
					remove(file)

					## CREATE OBJECT WITH VALUES
					# print(parse_files(png))
					if complex_content == True: datum['content'].append(parse_files(png))
					else: datum['content'] += '\n\n----media/image:\n{}----\n\n'.format(parse_files(png)['content'])
				except: pass
	
	## REMOVE THE TEMP DIR
	rmtree(download_dir)

	return datum

if __name__ == '__main__':
	## THIS IS TO MAKE THE BROWSER HEADLESS (DON'T SHOW THE BROWSER)
	headless = False
	chrome_options = Options()
	if headless: chrome_options.add_argument('--headless')
	
	# prefs = { 'download.default_directory': download_dir, 'profile.default_content_setting_values.automatic_downloads': 1 }
	# chrome_options.add_experimental_option('prefs', prefs)

	## LAUNCH THE BROWSER (DRIVER)
	browser = webdriver.Chrome(ChromeDriverManager().install(), options = chrome_options)
	url = 'https://sway.office.com/khdDlcR4GjpoPsom?ref=Link'
	
	browser.get(url)
	if '404' not in browser.title: 
		print(parse(browser))