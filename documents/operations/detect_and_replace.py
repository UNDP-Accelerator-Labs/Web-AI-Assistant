from sys import path as syspath
from os.path import join, dirname
import re

syspath.append(join(dirname(__file__), '..'))
from parsers import parse_xhtml

def detect(string):
	# Pattern from https://www.geeksforgeeks.org/python-check-url-string/
	pattern = r'https?://\S+|www\.\S+'
	urls = re.findall(pattern, string)
	return urls

def replace(string):
	urls = detect(string)
	if len(urls) > 0:
		for u in urls:
			document = parse_xhtml(u)
			string = string.replace(u, f'\n{document}\n')
	return string

if __name__ == '__main__':
	prompt = 'please get the information at https://unstats.un.org/sdgs/hlg/Call_for_Applications_from_data_and_statistics_communities/'
	print(replace(prompt))