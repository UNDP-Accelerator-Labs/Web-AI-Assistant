from sys import path as syspath
from os.path import join, splitext, dirname, basename

from pypdf import PdfReader
# DOCUMENTATION: https://pypdf.readthedocs.io/en/stable/modules/PdfReader.html
import datetime
import re
from dateutil.tz import tzutc, tzoffset

syspath.append(join(dirname(__file__), '..'))
from operations import chunk as chunk_content

## SOURCE: https://www.thepythoncode.com/article/extract-pdf-metadata-in-python 
def transform_date (date_str):
	"""
	Convert a pdf date such as "D:20120321183444+07'00'" into a usable datetime
	http://www.verypdf.com/pdfinfoeditor/pdf-date-format.htm
	(D:YYYYMMDDHHmmSSOHH'mm')
	:param date_str: pdf date string
	:return: datetime object
	"""
	
	pdf_date_pattern = re.compile(''.join([
		r'(D:)?',
		r'(?P<year>\d\d\d\d)',
		r'(?P<month>\d\d)',
		r'(?P<day>\d\d)',
		r'(?P<hour>\d\d)',
		r'(?P<minute>\d\d)',
		r'(?P<second>\d\d)',
		r'(?P<tz_offset>[+-zZ])?',
		r'(?P<tz_hour>\d\d)?',
	   	r"'?(?P<tz_minute>\d\d)?'?"
	]))	

	match = re.match(pdf_date_pattern, date_str)
	if match:
		date_info = match.groupdict()

		for k, v in date_info.items():  # transform values
			if v is None:
				pass
			elif k == 'tz_offset':
				date_info[k] = v.lower()  # so we can treat Z as z
			else:
				date_info[k] = int(v)

		if date_info['tz_offset'] in ('z', None):  # UTC
			date_info['tzinfo'] = tzutc()
		else:
			multiplier = 1 if date_info['tz_offset'] == '+' else -1
			date_info['tzinfo'] = tzoffset(None, multiplier*(3600 * date_info['tz_hour'] + 60 * date_info['tz_minute']))

		for k in ('tz_offset', 'tz_hour', 'tz_minute'):  # no longer needed
			del date_info[k]

		return datetime.datetime(**date_info)

def parse (file, **kwargs):
	datum = kwargs.get('datum', {})
	complex_content = kwargs.get('complex_content', False)
	chunk = kwargs.get('chunk', False)

	pdf = PdfReader(file)
	metadata = pdf.metadata

	name, ext = splitext(file)
	datum['name'] = basename(file)
	datum['type'] = ext

	if '/Title' in metadata: datum['title'] = str(metadata['/Title'])
	else: datum['title'] = None
	if '/Subject' in metadata: datum['subject'] = str(metadata['/Subject'])
	else: datum['subject'] = None
	if '/Author' in metadata: datum['author'] = str(metadata['/Author'])
	else: datum['author'] = None
	if '/Keywords' in metadata: datum['keywords'] = str(metadata['/Keywords'])
	else: datum['keywords'] = None
	if '/CreationDate' in metadata and metadata['/CreationDate'] != '': 
		datum['created'] = transform_date(str(metadata['/CreationDate'])).strftime('%m/%d/%Y, %H:%M')
	else: datum['created'] = None
	if '/ModDate' in metadata and metadata['/ModDate'] != '': 
		print(metadata['/ModDate'] == '')
		print(str(metadata['/ModDate']))
		print(transform_date(str(metadata['/ModDate'])))
		datum['modified'] = transform_date(str(metadata['/ModDate'])).strftime('%m/%d/%Y, %H:%M')
	else: datum['modified'] = None
	
	datum['content'] = ''
	
	for p in pdf.pages:
		datum['content'] += p.extract_text()
	
	if chunk == True:
		datum['content'] = chunk_content(datum['content'], 4000, 2000)
	
	return datum

if __name__ == '__main__':
	file = '/Users/myjyby/Documents/Projects/Teams/scraper/files/The Long Shadow of Informality--World Bank.pdf'
	print(parse(file, chunk=True))