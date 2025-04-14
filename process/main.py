"""
This script serves for testing the module. For running the full application,
prefer the @root/main.py file.

The general workflow in this file is inspired by: https://www.youtube.com/watch?v=9KKnNh89AGU
"""

import pprint
from sys import path as syspath
from os.path import join, dirname
import json, re

from tqdm import tqdm # this is for the loader
from colorama import Fore # this is to colorize the terminal output

# Search modules
syspath.append(join(dirname(__file__), './'))
from _00_assistant_response import assistant_response
from _01_require_search import require_search
from _02_interpret_prompt import interpret_prompt
from _03_perform_search import perform_search
from _04_summarize_search_results import summarize_search_result
# from _05_refine_response import refine_response

def run_web_search (prompt, conversation, **kwargs):
	QUERIES = kwargs.get('n_queries', 3)
	STREAM = kwargs.get('stream_output', False)
	MODEL = kwargs.get('model', 'llama3.2')
	INVALID_SOURES = kwargs.get('invalid_sources', [])
	# Check if additional web search is needed
	search_needed = require_search(prompt=prompt, conversation=conversation, model=MODEL, stream_output=STREAM)

	if search_needed == 'true':
		print(Fore.YELLOW + "A set of AI agents and workers will work to retrieve online information in order to improve you AI Assistant's response.")
		print(Fore.RED + 'Would you like to see how they reason? y/n')
		show_reasoning = input(Fore.WHITE)
		if show_reasoning.strip().lower() == 'y':
			STREAM = True
		else:
			STREAM = False

		# Interpret the prompt as a set of queries
		queries = interpret_prompt(prompt=prompt, conversation=conversation, n_queries=QUERIES, stream_output=STREAM)

		# For each generated keyword, perform a search
		summaries = []
		all_search_results = []
		for q in tqdm(queries, desc=Fore.YELLOW + 'iterating over online searches'):
			search_results, invalid_sources = perform_search(search=q, stream_output=STREAM, invalid_sources=INVALID_SOURES)
			all_search_results.append(search_results)
			# Update the invalid sources
			INVALID_SOURES = invalid_sources
			# Generate a summary of the top level in formation of the search results
			summary = summarize_search_result(prompt=prompt, json_input=search_results, model=MODEL, stream_output=STREAM)
			summaries.append(summary)
		
		# Reset stream output
		STREAM = False
		# Return list of summaries and all invalidated sources
		return (summaries, INVALID_SOURES)
	else:
		# Reset stream output
		STREAM = False
		return (None, INVALID_SOURES)

def main ():
	MODEL = 'llama3.2'
	STREAM = False

	# Initialize the conversation
	conversation = [
		{ 
			'role': 'system',
			'content': """
				You are an AI assistant that responds to a USER PROMPT.

				You have several AI agents and workers working for you to retrieve 
				relevant and up-to-date information from search enginge queries 
				using engines like Google Search. 
				These SEARCH RESULTS are passed to you as a python list of strings.
				
				You must use the SEARCH RESULTS as context to produce 
				a high quality response to the USER PROMPT. 
				Your response must be intelligible and useful to a human reader.
			"""
		}
	]

	while True:
		print(Fore.WHITE + 'USER:')
		prompt = input()

		if prompt.lower() == 'bye':
			break
		else: 
			summaries, invalid_sources = run_web_search(prompt, conversation, n_queries=3, model=MODEL, stream_output=STREAM)
			if summaries and len(summaries) > 0:
				conversation.append({
					'role': 'user', 
					'content': f"""
						SEARCH RESULTS: {summaries}
						USER PROMPT: {prompt}
					"""
				})
			else:
				conversation.append({ 'role': 'user', 'content': prompt })

			response = assistant_response(conversation=conversation, model=MODEL, stream_output=True)
			conversation.append({ 'role': 'assistant', 'content': response })


if __name__ == '__main__':
	main()