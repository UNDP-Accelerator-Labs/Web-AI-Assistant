from sys import path as syspath
from os import getcwd, remove, makedirs
from os.path import join, exists, dirname
from shutil import rmtree

from selenium import webdriver

from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

## THIS IS FOR DOWNLOADING THE IMAGES
from binascii import a2b_base64

## LOAD OPERATIONS
syspath.append(join(dirname(__file__), 'operations/'))
from extract import extract as extract_text

def parse (browser, datum = {}):
	download_dir = join(getcwd(), 'mural_downloads/')
	if not exists(download_dir):
		makedirs(download_dir)

	WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'render-engine-placeholder')))

	datum['url'] = browser.current_url
	datum['title'] = browser.title

	img_data = browser.execute_script("""
		const main_engine = document.querySelector('canvas.render-engine');
		main_engine.parentNode.style.transform = 'scale(3, 3)';
		return main_engine.toDataURL();
	""").replace('data:image/png;base64,', '')
	binary_data = a2b_base64(img_data)
	
	file = join(download_dir, 'image.png')
	with open(file, 'wb') as f:
		f.write(binary_data)

	datum['content'] = extract_text(file)
	remove(file)

	## REMOVE THE TEMP DIR
	rmtree(download_dir)
	return datum

if __name__ == '__main__':
	## THIS IS TO MAKE THE BROWSER HEADLESS (DON'T SHOW THE BROWSER)
	headless = False
	chrome_options = Options()

	if headless: chrome_options.add_argument('--headless')
	
	## LAUNCH THE BROWSER (DRIVER)
	browser = webdriver.Chrome(ChromeDriverManager().install())
	url = 'https://app.mural.co/t/undpinnovationgender1434/m/undpinnovationgender1434/1635952019532/01dc2e0d32434cabd74333ca3f4c004473a616b4?sender=acceleratorlabs4427'
	
	browser.get(url)
	if '404' not in browser.title: 
		print(parse(browser))
