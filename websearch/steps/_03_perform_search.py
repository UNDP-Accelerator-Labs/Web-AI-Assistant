"""
This part of the script runs the different search queries
in the preferred search engine.

It takes the host and port at which the search
engine is running as input, as well as the search query
and a list of user-determined invalid sources.

The invalid sources are retrieved from interaction
history, and complemented with user inputs at running time.

The output must be a json array of objects that follow the basic structure:
[
	{
		"title": "Title of the retrieved page",
		"description": "A description of any length of the content 
		of the page. This could be part of or the entire html document, 
		or the open graph description."
	}
]
If you use Searxng with the json format activated, this should be default.
If not, you will have to reconstruct the json object so the next
part of the process does not break.

*Notes*: if you opt for a local search engine, 
make sure it is running at this point. 
You can easily download and run an instance of Searxng using 
a docker image from https://github.com/searxng/searxng-docker
The Searxng search api documentation can be found at: 
https://docs.searxng.org/dev/search_api.html
"""

import pprint
from sys import argv
import urllib.request as req
import urllib.parse as parse
import json
import re
import inquirer

from colorama import Fore # this is to colorize the terminal output

def perform_search (**kwargs):
	host = kwargs.get('host', 'localhost')
	port = kwargs.get('port', '8080')
	search = kwargs.get('search')
	stream_output = kwargs.get('stream_output', False)
	invalid_sources = kwargs.get('invalid_sources', [])
	limit = kwargs.get('limit', 15)
	
	if host is None:
		raise Exception('missing host')
	if port is None:
		raise Exception('port is missing')
	if search is None:
		raise Exception('missing search term')

	output = []

	safe_search = parse.quote_plus(search)

	# &categories=science
	# &categories=news
	with req.urlopen(f'http://{host}:{port}/search?q={safe_search}&format=json&categories=news') as response:

		parsed_response = json.loads(response.read())
		
		# answers = parsed_response['answers']
		results = parsed_response['results']
		if limit is not None:
			results = results[:limit]

		if stream_output == True:
			# Check if there are any sources the user would like to exclude
			print(f'[Workflow] SearXNG:')
			print(f'Searching for "{search}"')
			sources = list(set([r['parsed_url'][1] for r in results]))
			print(Fore.RED + 'Below is a list of web sources retrieved by SearXNG. Are there any you would like to exclude? These might include untrusted sources or simply sources you consider irrelevant for what you are interested in.')
			print(Fore.RED + 'Use up and down arrow keys to navigate, and right and left arrow keys to select and deselect sources you wish to exclude.')
			
			questions = [inquirer.Checkbox(
				'invalid_sources',
				message='List of sources:',
				choices=sources,
				default=[i for i in invalid_sources if i in sources]
			)]
			exclude = inquirer.prompt(questions)
			invalid_sources = invalid_sources + exclude['invalid_sources']

			if len(invalid_sources) > 0:
				# Filter results
				results = [r for r in results if r['parsed_url'][1] not in invalid_sources]
				# Offer to save excluded domains for future searches

			print(f'The search for "{search}" retrieved {len(results)} page(s).')

		for entry in results:
			keys = ('title','content','url','publishedDate','score')
			# Check whether the page explicitely mentions necessary login
			if not re.search('login|log in', entry['content'], re.IGNORECASE):
				out = {}
				for k in keys:
					try:
						out[k] = entry[k]
					except KeyError as e:
						out[k] = None
				
				if out['url'] not in list(set([o['url'] for o in output])):
					output.append(out)
			
	return (sorted(output, key=lambda x: x['score'], reverse=True), invalid_sources)

def main ():
	if len(argv) < 2:
		print ('missing search')
	else:
		search = argv[1]
		results, invalid_sources = perform_search(host='localhost', port='8080', search=search)
		pprint.pprint(results)

if __name__ == '__main__':
	main()