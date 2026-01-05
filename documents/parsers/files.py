from sys import path as syspath
from os import remove, getcwd
from os.path import join, splitext, dirname, basename, getsize
from mimetypes import guess_type

## CUSTOM MODULES
from pdf import parse as parse_pdf
from ppt import parse as parse_ppt
from docx import parse as parse_docx
from xlsx import parse as parse_xlsx

## LOAD OPERATIONS
syspath.append(join(dirname(__file__), 'operations/'))
from extract import extract as extract_text

def parse (file, datum = {}, delete = True): ## THE datum ARG SHOULD PROVIDE A STRUCTURE FOR THE OUTPUT DATA IF DEFINED
	name, ext = splitext(file)
	size = getsize(file)
	mimetype, encoding = guess_type(file)
	print(size)
	print(mimetype)
	parsed_file = []
	
	if ext == '.pdf':
		parsed_file = parse_pdf(file, datum)
	elif ext in ['.ppt', '.pptx']:
		parsed_file = parse_ppt(file, datum)
	elif ext in ['.doc', '.docx']:
		parsed_file = parse_docx(file, datum)
	elif ext in ['.xls', '.xlsx']:
		parsed_file = parse_xlsx(file, datum)
	else:
		name, ext = splitext(file)
		datum['name'] = basename(file)
		datum['type'] = ext
		datum['content'] = extract_text(file)
		parsed_file = datum

	## DELETE FILE
	if delete == True: 
		try: remove(file)
		except: 
			print('failed to remove file: {}'.format(basename(file)))
			pass

	return parsed_file

if __name__ == '__main__':
	file = '/Users/myjyby/Documents/Projects/Teams/scraper/files/Luker 2008 Salsa Dancing in the Social Sciences Ch4.pdf'
	# file = '/Users/myjyby/Documents/Projects/Teams/scraper/files/mural_test.png'
	print(parse(file, {}, False))