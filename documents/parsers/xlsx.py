import pandas as pd
from openpyxl import load_workbook

def parse (file, datum = {}):
	wb = load_workbook(file)
	print(wb.properties)
	print(wb.properties.creator)

	datum['title'] = wb.properties.title
	datum['subject'] = wb.properties.subject
	datum['author'] = wb.properties.creator
	datum['keywords'] = wb.properties.keywords
	datum['created'] = wb.properties.created.strftime('%m/%d/%Y, %H:%M')
	datum['modified'] = wb.properties.modified.strftime('%m/%d/%Y, %H:%M')

	datum['content'] = ''
	
	sheets = pd.read_excel(file, engine = 'openpyxl', sheet_name = None)
	for sheet in sheets:
		datum['content'] += '\n\n----xlsx/sheet:\n{}----\n'.format(sheet)
		datum['content'] += sheets[sheet].to_string()

	datum['content'] = datum['content'].strip()
	
	datum['additional_metadata'] = {}
	datum['additional_metadata']['description'] = wb.properties.description
	datum['additional_metadata']['identifier'] = wb.properties.identifier
	datum['additional_metadata']['language'] = wb.properties.language
	datum['additional_metadata']['last_modified_by'] = wb.properties.lastModifiedBy
	datum['additional_metadata']['category'] = wb.properties.category
	datum['additional_metadata']['content_status'] = wb.properties.contentStatus
	datum['additional_metadata']['version'] = wb.properties.version
	datum['additional_metadata']['revision'] = wb.properties.revision
	datum['additional_metadata']['last_printed'] = wb.properties.lastPrinted

	return datum

if __name__ == '__main__':
	file = '/Users/myjyby/Documents/Projects/Teams/scraper/files/InnovationCompetencies_11June2021_v2.xlsx'
	print(parse(file))